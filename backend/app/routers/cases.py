import json
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, selectinload

from app import pagination
from app.auth.deps import current_org_id_dep, current_user
from app.db import get_db
from app.disclaimer import disclaimer_block
from app.i18n import Lang
from app.models import (
    Case,
    CaseStatus,
    Evidence,
    Fact,
    HilCheckpoint,
    HilStatus,
    Job,
    Outcome,
    Party,
    Ruling,
    User,
)
from app.schemas.case import CaseIn, CaseListItem, CaseOut, CasePage, GenerateCaseIn, RunIn
from app.services import audit, case_generator, event_bus, job_service, pdf_service

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseOut, status_code=201)
def create_case(
    payload: CaseIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
    org_id: uuid.UUID = Depends(current_org_id_dep),
) -> Case:
    case = Case(
        org_id=org_id,
        created_by_user_id=user.id,
        title_en=payload.title_en,
        title_ar=payload.title_ar,
        summary_en=payload.summary_en,
        summary_ar=payload.summary_ar,
        language_primary=payload.language_primary,
        jurisdiction=payload.jurisdiction,
        area_of_law=payload.area_of_law,
        created_by=payload.created_by or user.email,
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
    audit.record(
        db, action="CASE_CREATE", resource_type="case", resource_id=case.id,
        after={"title_en": case.title_en, "area_of_law": case.area_of_law},
        actor=user, org_id=org_id, request=request,
    )
    return _load_case(db, case.id)


@router.post("/generate", response_model=CaseOut, status_code=201)
async def generate_case(
    payload: GenerateCaseIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
    org_id: uuid.UUID = Depends(current_org_id_dep),
) -> Case:
    case = await case_generator.generate_case(
        db,
        area_of_law=payload.area_of_law,
        difficulty=payload.difficulty,
        language=payload.language,
        user_id=payload.user_id or user.email,
    )
    # Stamp tenancy on the generated case so it shows up in this org's list
    case.org_id = org_id
    case.created_by_user_id = user.id
    db.commit()
    return _load_case(db, case.id)


@router.get("", response_model=CasePage)
def list_cases(
    limit: int = pagination.DEFAULT_LIMIT,
    cursor: str | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> CasePage:
    # tenant auto-filter applies here via the SQLAlchemy event hook
    limit = pagination.clamp_limit(limit)
    stmt = select(Case).order_by(Case.created_at.desc(), Case.id.desc())
    if cursor:
        c_ts, c_id = pagination.decode_cursor(cursor)
        stmt = stmt.where(
            or_(
                Case.created_at < c_ts,
                and_(Case.created_at == c_ts, Case.id < c_id),
            )
        )
    rows = db.execute(stmt.limit(limit + 1)).scalars().all()
    has_more = len(rows) > limit
    items = rows[:limit]
    next_cursor = (
        pagination.encode_cursor(items[-1].created_at, items[-1].id)
        if has_more and items
        else None
    )
    return CasePage(
        items=[CaseListItem.model_validate(c) for c in items],
        next_cursor=next_cursor,
    )


@router.get("/{case_id}", response_model=CaseOut)
def get_case(
    case_id: uuid.UUID,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
):
    case = _load_case(db, case_id)
    etag = _case_etag(case)
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers={"ETag": etag})
    response.headers["ETag"] = etag
    return case


@router.post("/{case_id}/cancel")
def cancel_case(
    case_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    """Request cooperative cancellation. The running worker checks this flag
    at each stage boundary and halts; an already-terminal case is a no-op."""
    case = _load_case(db, case_id)
    if case.status in (CaseStatus.COMPLETE, CaseStatus.CANCELLED):
        return {"case_id": str(case_id), "status": case.status.value, "cancel_requested": case.cancel_requested}
    if not case.cancel_requested:
        case.cancel_requested = True
        db.commit()
        audit.record(
            db, action="CASE_CANCEL", resource_type="case", resource_id=case_id,
            actor=user, request=request,
        )
        event_bus.publish(case_id, {"status": "running", "stage": "cancel_requested"})
    return {"case_id": str(case_id), "status": case.status.value, "cancel_requested": True}


@router.post("/{case_id}/run")
def run_case(
    case_id: uuid.UUID,
    payload: RunIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict:
    case = _load_case(db, case_id)
    # An idempotent replay returns the original job regardless of the case's
    # current status (it may already have completed the first run).
    if idempotency_key:
        existing = job_service.find_job_by_key(db, case_id, idempotency_key)
        if existing:
            return {
                "case_id": str(case_id),
                "job_id": str(existing.id),
                "status": existing.status.value,
                "disclaimer": disclaimer_block(),
            }
    if case.status not in (CaseStatus.DRAFT, CaseStatus.PAUSED_HIL, CaseStatus.FAILED):
        raise HTTPException(409, f"Case in status {case.status}, cannot run")
    job = job_service.enqueue_simulation(db, case_id, payload.max_rounds, idempotency_key)
    audit.record(
        db, action="CASE_RUN", resource_type="case", resource_id=case_id,
        after={"job_id": str(job.id), "max_rounds": payload.max_rounds},
        actor=user, request=request,
    )
    return {
        "case_id": str(case_id),
        "job_id": str(job.id),
        "status": job.status.value,
        "disclaimer": disclaimer_block(),
    }


@router.get("/{case_id}/status")
def case_status(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> dict:
    case = _load_case(db, case_id)
    pending = db.execute(
        select(HilCheckpoint)
        .where(HilCheckpoint.case_id == case_id, HilCheckpoint.status == HilStatus.PENDING)
        .order_by(HilCheckpoint.created_at.desc())
    ).scalars().first()
    latest_job = db.execute(
        select(Job).where(Job.case_id == case_id).order_by(Job.created_at.desc())
    ).scalars().first()
    return {
        "case_id": str(case.id),
        "status": case.status.value,
        "job": {
            "id": str(latest_job.id),
            "kind": latest_job.kind.value,
            "status": latest_job.status.value,
            "error": latest_job.error,
        } if latest_job else None,
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
def case_report(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> dict:
    case = _load_case(db, case_id)
    ruling = db.execute(select(Ruling).where(Ruling.case_id == case_id)).scalar_one_or_none()
    outcome = db.execute(select(Outcome).where(Outcome.case_id == case_id)).scalar_one_or_none()
    return _report_payload(case, ruling, outcome)


@router.get("/{case_id}/report.pdf")
def case_report_pdf(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> Response:
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


@router.get("/{case_id}/events")
async def case_events(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> StreamingResponse:
    """Server-Sent Events stream for live pipeline updates.

    Replays the case's recent event history (so a late client doesn't miss
    anything) then tails new events until the pipeline reaches a terminal
    state (complete/failed/paused) or the idle timeout elapses.
    """
    _load_case(db, case_id)  # 404 + tenant scoping

    async def _gen():
        async for evt in event_bus.subscribe(case_id, replay=True):
            yield f"data: {json.dumps(evt)}\n\n"

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# --- helpers ---

def _case_etag(case: Case) -> str:
    """Weak validator keyed on the case's last-modified timestamp."""
    return f'W/"{case.updated_at.isoformat()}"'


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
