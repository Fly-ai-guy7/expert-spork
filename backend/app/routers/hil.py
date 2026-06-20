import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal, get_db
from app.models import HilCheckpoint, HilStage, HilStatus
from app.schemas.simulation import CounselRequestIn, HilActionIn, TraineeSubmissionIn
from app.services import counsel_service, orchestrator

router = APIRouter(prefix="/api/hil", tags=["hil"])


@router.get("/pending")
def list_pending(case_id: uuid.UUID | None = None, db: Session = Depends(get_db)) -> list[dict]:
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
def approve(cp_id: uuid.UUID, payload: HilActionIn, db: Session = Depends(get_db)) -> dict:
    cp = _get(db, cp_id)
    cp.status = HilStatus.APPROVED
    cp.notes = payload.notes
    cp.responded_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": str(cp.id), "status": cp.status.value}


@router.post("/{cp_id}/modify")
def modify(cp_id: uuid.UUID, payload: HilActionIn, db: Session = Depends(get_db)) -> dict:
    cp = _get(db, cp_id)
    cp.status = HilStatus.MODIFIED
    cp.notes = payload.notes
    cp.modified_payload = payload.modified_payload
    cp.responded_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": str(cp.id), "status": cp.status.value}


@router.post("/{cp_id}/halt")
def halt(cp_id: uuid.UUID, payload: HilActionIn, db: Session = Depends(get_db)) -> dict:
    cp = _get(db, cp_id)
    cp.status = HilStatus.HALTED
    cp.notes = payload.notes
    cp.responded_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": str(cp.id), "status": cp.status.value}


@router.post("/{cp_id}/submit-trainee", status_code=202)
async def submit_trainee(
    cp_id: uuid.UUID,
    payload: TraineeSubmissionIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    cp = _get(db, cp_id)
    background_tasks.add_task(
        _submit_in_background, cp_id, payload.content_en, payload.content_ar, payload.citations
    )
    return {"id": str(cp.id), "status": "RESUMING"}


@router.post("/{cp_id}/counsel")
async def counsel(
    cp_id: uuid.UUID, payload: CounselRequestIn, db: Session = Depends(get_db)
) -> dict:
    cp = _get(db, cp_id)
    if cp.stage != HilStage.TRAINEE_TURN:
        raise HTTPException(409, "Counsel is only available at a TRAINEE_TURN checkpoint")
    side = (cp.modified_payload or {}).get("side", "DEFENSE")
    return await counsel_service.generate_counsel(
        db,
        cp.case_id,
        side,
        payload.content_en,
        payload.content_ar,
        payload.citations,
        checkpoint_id=cp.id,
    )


def _get(db: Session, cp_id: uuid.UUID) -> HilCheckpoint:
    cp = db.execute(select(HilCheckpoint).where(HilCheckpoint.id == cp_id)).scalar_one_or_none()
    if cp is None:
        raise HTTPException(404, "Checkpoint not found")
    return cp


def _submit_in_background(
    cp_id: uuid.UUID, content_en: str | None, content_ar: str | None, citations: list[str]
) -> None:
    import asyncio

    async def _go():
        db = SessionLocal()
        try:
            await orchestrator.submit_trainee_argument(db, cp_id, content_en, content_ar, citations)
        finally:
            db.close()

    asyncio.run(_go())
