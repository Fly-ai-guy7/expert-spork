import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import current_user
from app.db import get_db
from app.models import HilCheckpoint, HilStatus, User
from app.schemas.simulation import HilActionIn, TraineeSubmissionIn
from app.security.sanitize import sanitize_citations, sanitize_text
from app.services import job_service

router = APIRouter(prefix="/hil", tags=["hil"])


@router.get("/pending")
def list_pending(
    case_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> list[dict]:
    stmt = select(HilCheckpoint).where(HilCheckpoint.status == HilStatus.PENDING)
    if case_id:
        stmt = stmt.where(HilCheckpoint.case_id == case_id)
    cps = db.execute(stmt.order_by(HilCheckpoint.created_at)).scalars().all()
    return [
        {
            "id": str(cp.id),
            "case_id": str(cp.case_id),
            "stage": cp.stage.value,
            "status": cp.status.value,
            "modified_payload": cp.modified_payload,
            "created_at": cp.created_at,
        }
        for cp in cps
    ]


@router.post("/{cp_id}/approve")
def approve(
    cp_id: uuid.UUID,
    payload: HilActionIn,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> dict:
    cp = _get(db, cp_id)
    cp.status = HilStatus.APPROVED
    cp.notes = payload.notes
    cp.responded_at = datetime.now(UTC)
    db.commit()
    return {"id": str(cp.id), "status": cp.status.value}


@router.post("/{cp_id}/modify")
def modify(
    cp_id: uuid.UUID,
    payload: HilActionIn,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> dict:
    cp = _get(db, cp_id)
    cp.status = HilStatus.MODIFIED
    cp.notes = payload.notes
    cp.modified_payload = payload.modified_payload
    cp.responded_at = datetime.now(UTC)
    db.commit()
    return {"id": str(cp.id), "status": cp.status.value}


@router.post("/{cp_id}/halt")
def halt(
    cp_id: uuid.UUID,
    payload: HilActionIn,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> dict:
    cp = _get(db, cp_id)
    cp.status = HilStatus.HALTED
    cp.notes = payload.notes
    cp.responded_at = datetime.now(UTC)
    db.commit()
    return {"id": str(cp.id), "status": cp.status.value}


@router.post("/{cp_id}/submit-trainee", status_code=202)
def submit_trainee(
    cp_id: uuid.UUID,
    payload: TraineeSubmissionIn,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> dict:
    cp = _get(db, cp_id)
    job = job_service.enqueue_trainee_resume(
        db,
        cp.case_id,
        cp_id,
        sanitize_text(payload.content_en),
        sanitize_text(payload.content_ar),
        sanitize_citations(payload.citations),
    )
    return {"id": str(cp.id), "job_id": str(job.id), "status": job.status.value}


def _get(db: Session, cp_id: uuid.UUID) -> HilCheckpoint:
    cp = db.execute(select(HilCheckpoint).where(HilCheckpoint.id == cp_id)).scalar_one_or_none()
    if cp is None:
        raise HTTPException(404, "Checkpoint not found")
    return cp
