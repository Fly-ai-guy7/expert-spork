import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.agents import (
    AgentContext,
    DefenseAgent,
    EvidenceMigrationAgent,
    JudicialAgent,
    ProsecutionAgent,
    ScoringAgent,
)
from app.agents.base import LegalAgent
from app.config import settings
from app.i18n import Lang
from app.models import (
    Argument,
    Case,
    CaseStatus,
    DebateRound,
    Evidence,
    EvidenceKind,
    Fact,
    HilCheckpoint,
    HilStage,
    HilStatus,
    Outcome,
    Ruling,
    Score,
    TraineeRole,
    TrainingSession,
)
from app.models.argument import AgentRole
from app.services.corpus_service import build_statute_block, find_articles_by_short_codes

logger = logging.getLogger(__name__)

PROSECUTION_LLM_BY_ROUND = ["claude-opus", "deepseek", "claude-opus"]
DEFENSE_LLM_BY_ROUND = ["deepseek", "claude-opus", "deepseek"]


def _case_snapshot(case: Case) -> dict:
    return {
        "title_en": case.title_en,
        "title_ar": case.title_ar,
        "summary_en": case.summary_en,
        "summary_ar": case.summary_ar,
        "parties": [
            {"role": p.role.value, "name_en": p.name_en, "name_ar": p.name_ar, "kind": p.kind.value}
            for p in case.parties
        ],
        "facts": [
            {"text_en": f.text_en, "text_ar": f.text_ar, "disputed": f.disputed, "order": f.order_index}
            for f in sorted(case.facts, key=lambda x: x.order_index)
        ],
        "evidence": [
            {"kind": e.kind.value, "title_en": e.title_en, "title_ar": e.title_ar, "missing": e.missing}
            for e in case.evidence
        ],
    }


def _load_case(db: Session, case_id: uuid.UUID) -> Case:
    return db.execute(
        select(Case)
        .options(
            selectinload(Case.parties),
            selectinload(Case.facts),
            selectinload(Case.evidence),
            selectinload(Case.arguments),
            selectinload(Case.debate_rounds),
            selectinload(Case.training_sessions),
        )
        .where(Case.id == case_id)
    ).scalar_one()


def _has_side_argument(case: Case, round_no: int, side: AgentRole) -> bool:
    trainee = AgentRole.TRAINEE
    target = {side, trainee} if side in (AgentRole.PROSECUTION, AgentRole.DEFENSE) else {side}
    return any(a.round_no == round_no and a.agent in target for a in case.arguments)


def _get_or_create_round(
    db: Session, case_id: uuid.UUID, round_no: int, prosecution_llm: str, defense_llm: str,
    debate_rounds: list[DebateRound],
) -> DebateRound:
    existing = next((r for r in debate_rounds if r.round_no == round_no), None)
    if existing:
        return existing
    row = DebateRound(
        case_id=case_id, round_no=round_no, status="RUNNING",
        team_a_llm=prosecution_llm, team_b_llm=defense_llm,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _active_training(case: Case) -> TrainingSession | None:
    for ts in case.training_sessions:
        if ts.completed_at is None:
            return ts
    return None


async def _score_argument(
    db: Session, argument: Argument, ctx: AgentContext, scorer: ScoringAgent
) -> Score:
    score_ctx = ctx.model_copy(
        update={
            "extra": {
                "argument": argument.content_en or argument.content_ar,
                "citations": argument.citations or [],
            }
        }
    )
    out = await scorer.run(score_ctx)
    raw = out.raw
    score = Score(
        argument_id=argument.id,
        factual=float(raw.get("factual", 0)),
        provable=float(raw.get("provable", 0)),
        unbiased=float(raw.get("unbiased", 0)),
        legal_law_based=float(raw.get("legal_law_based", 0)),
        overall=float(raw.get("overall", 0)),
        rationale_en=raw.get("rationale_en"),
        rationale_ar=raw.get("rationale_ar"),
    )
    db.add(score)
    db.commit()
    return score


async def _run_agent(
    db: Session,
    agent: LegalAgent,
    ctx: AgentContext,
    role: AgentRole,
    round_no: int,
    debate_round_id: uuid.UUID | None,
) -> Argument:
    out = await agent.run(ctx)
    citation_refs = out.raw.get("citations", [])
    article_ids = find_articles_by_short_codes(db, citation_refs) if citation_refs else []
    arg = Argument(
        case_id=ctx.case_id,
        debate_round_id=debate_round_id,
        agent=role,
        round_no=round_no,
        content_en=out.content_en,
        content_ar=out.content_ar,
        citations=[str(i) for i in article_ids],
        llm_used=out.llm_used,
    )
    db.add(arg)
    db.commit()
    db.refresh(arg)
    return arg


def _build_prior(case: Case) -> list[dict]:
    return [
        {"agent": a.agent.value, "round": a.round_no, "content": a.content_en or a.content_ar}
        for a in sorted(case.arguments, key=lambda x: (x.round_no, x.created_at))
    ]


async def run_simulation(db: Session, case_id: uuid.UUID, max_rounds: int | None = None) -> dict:
    case = _load_case(db, case_id)
    case.status = CaseStatus.RUNNING
    db.commit()

    lang = Lang(case.language_primary)
    max_rounds = max_rounds or settings.default_max_debate_rounds
    statute_block = build_statute_block(db, None, lang)
    snapshot = _case_snapshot(case)

    ctx_base = AgentContext(
        case_id=case_id,
        lang=lang,
        case_snapshot=snapshot,
        statute_block=statute_block,
    )

    # 1. Evidence Migration — idempotent: skip if facts exist
    if not case.facts:
        em_out = await EvidenceMigrationAgent().run(ctx_base)
        raw = em_out.raw
        for i, f in enumerate(raw.get("facts", []) or []):
            db.add(Fact(
                case_id=case_id, text_en=f.get("text_en"), text_ar=f.get("text_ar"),
                disputed=bool(f.get("disputed", False)),
                order_index=int(f.get("order_index", i)),
            ))
        for e in raw.get("evidence", []) or []:
            try:
                ek = EvidenceKind(e.get("kind", "DOCUMENT"))
            except ValueError:
                ek = EvidenceKind.DOCUMENT
            db.add(Evidence(
                case_id=case_id, kind=ek,
                title_en=e.get("title_en"), title_ar=e.get("title_ar"),
                description=e.get("description"), missing=bool(e.get("missing", False)),
            ))
        if raw.get("summary_en") and not case.summary_en:
            case.summary_en = raw["summary_en"]
        if raw.get("summary_ar") and not case.summary_ar:
            case.summary_ar = raw["summary_ar"]
        db.commit()
        case = _load_case(db, case_id)
        snapshot = _case_snapshot(case)
        ctx_base = ctx_base.model_copy(update={"case_snapshot": snapshot})

    scorer = ScoringAgent()
    training = _active_training(case)

    # 2. Debate loop — argument-level idempotent
    for round_no in range(1, max_rounds + 1):
        idx = (round_no - 1) % len(PROSECUTION_LLM_BY_ROUND)
        prosecution_llm = PROSECUTION_LLM_BY_ROUND[idx]
        defense_llm = DEFENSE_LLM_BY_ROUND[idx]

        prosecution_done = _has_side_argument(case, round_no, AgentRole.PROSECUTION)
        defense_done = _has_side_argument(case, round_no, AgentRole.DEFENSE)
        if prosecution_done and defense_done:
            continue

        round_row = _get_or_create_round(
            db, case_id, round_no, prosecution_llm, defense_llm, case.debate_rounds
        )

        # --- Prosecution side ---
        if not prosecution_done:
            if training and training.trainee_role == TraineeRole.PROSECUTION:
                cp = _pause_for_trainee(db, case, round_no, "PROSECUTION")
                return {"case_id": str(case_id), "status": "PAUSED_HIL", "checkpoint_id": str(cp.id)}
            ctx = ctx_base.model_copy(update={"prior_arguments": _build_prior(case), "extra": {"round_no": round_no}})
            arg = await _run_agent(
                db, ProsecutionAgent(llm=prosecution_llm), ctx, AgentRole.PROSECUTION, round_no, round_row.id
            )
            await _score_argument(db, arg, ctx, scorer)
            case = _load_case(db, case_id)

        # --- Defense side ---
        if not defense_done:
            if training and training.trainee_role == TraineeRole.DEFENSE:
                cp = _pause_for_trainee(db, case, round_no, "DEFENSE")
                return {"case_id": str(case_id), "status": "PAUSED_HIL", "checkpoint_id": str(cp.id)}
            ctx = ctx_base.model_copy(update={"prior_arguments": _build_prior(case), "extra": {"round_no": round_no}})
            arg = await _run_agent(
                db, DefenseAgent(llm=defense_llm), ctx, AgentRole.DEFENSE, round_no, round_row.id
            )
            await _score_argument(db, arg, ctx, scorer)
            case = _load_case(db, case_id)

        round_row.status = "COMPLETE"
        db.commit()

    # 3. Judicial Reasoning — idempotent
    case = _load_case(db, case_id)
    if case.ruling is None:
        ctx = ctx_base.model_copy(update={"prior_arguments": _build_prior(case)})
        j_out = await JudicialAgent().run(ctx)
        j = j_out.raw
        ruling = Ruling(
            case_id=case_id,
            plaintiff_success_prob=float(j.get("plaintiff_success_prob", 50)),
            critical_evidence_gaps=j.get("critical_evidence_gaps", []),
            precedent_refs=j.get("precedent_refs", []),
            text_en=j.get("ruling_en"),
            text_ar=j.get("ruling_ar"),
            override_applied=bool(j.get("override_applied", False)),
        )
        db.add(ruling)
        db.commit()
        case = _load_case(db, case_id)

    # 4. Outcome — idempotent
    if case.outcome is None and case.ruling is not None:
        prob = case.ruling.plaintiff_success_prob
        risk = abs(50 - prob) / 50.0 * 100
        outcome = Outcome(
            case_id=case_id,
            projected_prob=prob,
            risk_score=100 - risk,
            pretrial_resolution_en=(
                "Settlement recommended" if 30 < prob < 70 else "Strong position — proceed"
            ),
            pretrial_resolution_ar=(
                "يُنصح بالتسوية الودية" if 30 < prob < 70 else "موقف قوي — يُنصح بالمضي قدماً"
            ),
        )
        db.add(outcome)
        db.commit()

    # 5. Coaching (training only)
    if training and training.coaching_report is None:
        from app.services.coaching_service import generate_coaching_report
        generate_coaching_report(db, training.id)

    case = _load_case(db, case_id)
    case.status = CaseStatus.COMPLETE
    db.commit()
    return {"case_id": str(case_id), "status": "COMPLETE"}


def _pause_for_trainee(db: Session, case: Case, round_no: int, side: str) -> HilCheckpoint:
    cp = HilCheckpoint(
        case_id=case.id,
        stage=HilStage.TRAINEE_TURN,
        status=HilStatus.PENDING,
        modified_payload={"side": side, "round_no": round_no},
    )
    db.add(cp)
    case.status = CaseStatus.PAUSED_HIL
    db.commit()
    db.refresh(cp)
    return cp


async def submit_trainee_argument(
    db: Session,
    checkpoint_id: uuid.UUID,
    content_en: str | None,
    content_ar: str | None,
    citations: list[str] | None,
) -> dict:
    cp = db.execute(select(HilCheckpoint).where(HilCheckpoint.id == checkpoint_id)).scalar_one()
    if cp.stage != HilStage.TRAINEE_TURN or cp.status != HilStatus.PENDING:
        raise ValueError("Checkpoint is not a pending TRAINEE_TURN")

    payload = cp.modified_payload or {}
    round_no = int(payload.get("round_no", 1))
    case = _load_case(db, cp.case_id)

    round_row = next((r for r in case.debate_rounds if r.round_no == round_no), None)
    if round_row is None:
        round_row = DebateRound(case_id=case.id, round_no=round_no, status="RUNNING")
        db.add(round_row)
        db.commit()
        db.refresh(round_row)

    article_ids = find_articles_by_short_codes(db, citations or [])
    trainee_arg = Argument(
        case_id=case.id,
        debate_round_id=round_row.id,
        agent=AgentRole.TRAINEE,
        round_no=round_no,
        content_en=content_en,
        content_ar=content_ar,
        citations=[str(i) for i in article_ids],
        llm_used=None,
    )
    db.add(trainee_arg)
    cp.status = HilStatus.SUBMITTED
    cp.responded_at = datetime.now(timezone.utc)
    db.commit()

    lang = Lang(case.language_primary)
    statute_block = build_statute_block(db, None, lang)
    snapshot = _case_snapshot(case)
    score_ctx = AgentContext(
        case_id=case.id, lang=lang, case_snapshot=snapshot, statute_block=statute_block,
        extra={"argument": content_en or content_ar, "citations": citations or []},
    )
    await _score_argument(db, trainee_arg, score_ctx, ScoringAgent())

    case.status = CaseStatus.RUNNING
    db.commit()
    return await run_simulation(db, case.id)
