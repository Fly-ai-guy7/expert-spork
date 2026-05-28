import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import SessionLocal, get_db
from app.disclaimer import disclaimer_block
from app.i18n import Lang
from app.models import (
    Case,
    CaseStatus,
    Evidence,
    Fact,
    HilCheckpoint,
    HilStatus,
    Outcome,
    Party,
    Ruling,
)
from app.schemas.case import CaseIn, CaseListItem, CaseOut, GenerateCaseIn, RunIn
from app.services import case_generator, orchestrator, pdf_service

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.post("", response_model=CaseOut, status_code=201)
def create_case(payload: CaseIn, db: Session = Depends(get_db)) -> Case:
    case = Case(
        title_en=payload.title_en,
        title_ar=payload.title_ar,
        summary_en=payload.summary_en,
        summary_ar=payload.summary_ar,
        language_primary=payload.language_primary,
        jurisdiction=payload.jurisdiction,
        area_of_law=payload.area_of_law,
        created_by=payload.created_by,
    )
    db.add(case)
    db.flush()
    for p in payload.parties:
        db.add(Party(case_id=case.id, **p.model_dump()))
    for f in payload.facts:
        db.add(Fact(case_id=case.id, **f.model_dump()))
    for e in payload.evidence:
        db.add(Evidence(case_id=case.id, **e.model_dump()))
    db.commit()
    db.refresh(case)
    return _load_case(db, case.id)


@router.post("/generate", response_model=CaseOut, status_code=201)
async def generate_case(payload: GenerateCaseIn, db: Session = Depends(get_db)) -> Case:
    case = await case_generator.generate_case(
        db,
        area_of_law=payload.area_of_law,
        difficulty=payload.difficulty,
        language=payload.language,
        user_id=payload.user_id,
    )
    return _load_case(db, case.id)


@router.get("", response_model=list[CaseListItem])
def list_cases(db: Session = Depends(get_db)) -> list[Case]:
    return db.execute(select(Case).order_by(Case.created_at.desc())).scalars().all()


@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: uuid.UUID, db: Session = Depends(get_db)) -> Case:
    return _load_case(db, case_id)


@router.post("/{case_id}/run")
async def run_case(
    case_id: uuid.UUID,
    payload: RunIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    case = _load_case(db, case_id)
    if case.status not in (CaseStatus.DRAFT, CaseStatus.PAUSED_HIL, CaseStatus.FAILED):
        raise HTTPException(409, f"Case in status {case.status}, cannot run")
    background_tasks.add_task(_run_in_background, case_id, payload.max_rounds)
    return {"case_id": str(case_id), "status": "RUNNING", "disclaimer": disclaimer_block()}


@router.get("/{case_id}/status")
def case_status(case_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    case = _load_case(db, case_id)
    pending = db.execute(
        select(HilCheckpoint)
        .where(HilCheckpoint.case_id == case_id, HilCheckpoint.status == HilStatus.PENDING)
        .order_by(HilCheckpoint.created_at.desc())
    ).scalars().first()
    return {
        "case_id": str(case.id),
        "status": case.status.value,
        "rounds_complete": len([r for r in case.debate_rounds if r.status == "COMPLETE"]),
        "rounds_total": len(case.debate_rounds),
        "arguments": [
            {
                "id": str(a.id),
                "agent": a.agent.value,
                "round_no": a.round_no,
                "content_en": a.content_en,
                "content_ar": a.content_ar,
                "llm_used": a.llm_used,
                "score_overall": a.score.overall if a.score else None,
                "unverified_citations": a.unverified_citations or [],
            }
            for a in sorted(case.arguments, key=lambda x: (x.round_no, x.created_at))
        ],
        "hallucinated_citations_count": sum(
            len(a.unverified_citations or []) for a in case.arguments
        ),
        "pending_checkpoint_id": str(pending.id) if pending else None,
        "pending_checkpoint_stage": pending.stage.value if pending else None,
    }


@router.get("/{case_id}/report")
def case_report(case_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    case = _load_case(db, case_id)
    ruling = db.execute(select(Ruling).where(Ruling.case_id == case_id)).scalar_one_or_none()
    outcome = db.execute(select(Outcome).where(Outcome.case_id == case_id)).scalar_one_or_none()
    return _report_payload(case, ruling, outcome)


@router.get("/{case_id}/report.pdf")
def case_report_pdf(case_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    case = _load_case(db, case_id)
    ruling = db.execute(select(Ruling).where(Ruling.case_id == case_id)).scalar_one_or_none()
    outcome = db.execute(select(Outcome).where(Outcome.case_id == case_id)).scalar_one_or_none()
    payload = _report_payload(case, ruling, outcome)
    lang = Lang(case.language_primary)
    pdf_bytes = pdf_service.render_report_pdf(payload, lang)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="case-{case_id}.pdf"'},
    )


# --- helpers ---

def _load_case(db: Session, case_id: uuid.UUID) -> Case:
    case = db.execute(
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
    ).scalar_one_or_none()
    if case is None:
        raise HTTPException(404, "Case not found")
    return case


def _report_payload(case: Case, ruling: Ruling | None, outcome: Outcome | None) -> dict:
    args_by_role: dict[str, list[dict]] = {"PROSECUTION": [], "DEFENSE": [], "TRAINEE": []}
    for a in sorted(case.arguments, key=lambda x: (x.round_no, x.created_at)):
        if a.agent.value in args_by_role:
            args_by_role[a.agent.value].append({
                "round_no": a.round_no,
                "content_en": a.content_en,
                "content_ar": a.content_ar,
                "llm_used": a.llm_used,
                "score_overall": a.score.overall if a.score else None,
                "unverified_citations": a.unverified_citations or [],
            })
    return {
        "disclaimer": disclaimer_block(),
        "case": {
            "id": str(case.id),
            "title_en": case.title_en, "title_ar": case.title_ar,
            "summary_en": case.summary_en, "summary_ar": case.summary_ar,
            "language_primary": case.language_primary,
            "area_of_law": case.area_of_law,
            "parties": [
                {"role": p.role.value, "name_en": p.name_en, "name_ar": p.name_ar}
                for p in case.parties
            ],
        },
        "prosecution_arguments": args_by_role["PROSECUTION"],
        "defense_arguments": args_by_role["DEFENSE"],
        "trainee_arguments": args_by_role["TRAINEE"],
        "hallucinated_citations": [
            ref
            for a in case.arguments
            for ref in (a.unverified_citations or [])
        ],
        "ruling": {
            "plaintiff_success_prob": ruling.plaintiff_success_prob if ruling else None,
            "text_en": ruling.text_en if ruling else None,
            "text_ar": ruling.text_ar if ruling else None,
            "critical_evidence_gaps": ruling.critical_evidence_gaps if ruling else [],
            "precedent_refs": ruling.precedent_refs if ruling else [],
            "override_applied": ruling.override_applied if ruling else False,
        } if ruling else None,
        "outcome": {
            "projected_prob": outcome.projected_prob if outcome else None,
            "risk_score": outcome.risk_score if outcome else None,
            "pretrial_resolution_en": outcome.pretrial_resolution_en if outcome else None,
            "pretrial_resolution_ar": outcome.pretrial_resolution_ar if outcome else None,
        } if outcome else None,
    }


def _run_in_background(case_id: uuid.UUID, max_rounds: int | None) -> None:
    """Background task — gets its own DB session."""
    import asyncio

    async def _go():
        db = SessionLocal()
        try:
            await orchestrator.run_simulation(db, case_id, max_rounds)
        finally:
            db.close()

    asyncio.run(_go())
