import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal, get_db
from app.models import Case, CaseStatus, CounselLog, TraineeRole, TrainingSession
from app.schemas.case import StartTrainingIn
from app.services import orchestrator

router = APIRouter(prefix="/api", tags=["training"])


@router.post("/cases/{case_id}/run-training", status_code=202)
def run_training(
    case_id: uuid.UUID,
    payload: StartTrainingIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    case = db.execute(select(Case).where(Case.id == case_id)).scalar_one_or_none()
    if not case:
        raise HTTPException(404, "Case not found")
    try:
        role = TraineeRole(payload.trainee_role)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e

    ts = TrainingSession(
        user_id=payload.user_id,
        case_id=case_id,
        trainee_role=role,
        difficulty=payload.difficulty,
        started_at=datetime.now(timezone.utc),
    )
    db.add(ts)
    case.status = CaseStatus.DRAFT  # ensure it can be started
    db.commit()
    db.refresh(ts)

    background_tasks.add_task(_run_in_background, case_id, None)
    return {"training_session_id": str(ts.id), "case_id": str(case_id), "status": "RUNNING"}


@router.get("/training/{session_id}/coaching")
def get_coaching(session_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    ts = db.execute(
        select(TrainingSession).where(TrainingSession.id == session_id)
    ).scalar_one_or_none()
    if not ts:
        raise HTTPException(404, "Training session not found")
    return {
        "training_session_id": str(ts.id),
        "case_id": str(ts.case_id),
        "trainee_role": ts.trainee_role.value,
        "difficulty": ts.difficulty,
        "total_score": ts.total_score,
        "coaching_report": ts.coaching_report or {},
        "started_at": ts.started_at,
        "completed_at": ts.completed_at,
    }


@router.get("/training/{session_id}/counsel-log")
def get_counsel_log(session_id: uuid.UUID, db: Session = Depends(get_db)) -> list[dict]:
    ts = db.execute(
        select(TrainingSession).where(TrainingSession.id == session_id)
    ).scalar_one_or_none()
    if not ts:
        raise HTTPException(404, "Training session not found")
    logs = db.execute(
        select(CounselLog)
        .where(CounselLog.training_session_id == session_id)
        .order_by(CounselLog.created_at)
    ).scalars().all()
    return [
        {
            "id": str(log.id),
            "created_at": log.created_at,
            "trainee_role": log.trainee_role,
            "draft_en": log.draft_en,
            "draft_ar": log.draft_ar,
            "citations": log.citations or [],
            "advice": log.advice,
            "llm_used": log.llm_used,
        }
        for log in logs
    ]


@router.get("/training/sessions")
def list_training_sessions(user_id: str | None = None, db: Session = Depends(get_db)) -> list[dict]:
    stmt = select(TrainingSession).order_by(TrainingSession.created_at.desc())
    if user_id:
        stmt = stmt.where(TrainingSession.user_id == user_id)
    sessions = db.execute(stmt).scalars().all()
    return [
        {
            "id": str(s.id),
            "case_id": str(s.case_id),
            "trainee_role": s.trainee_role.value,
            "difficulty": s.difficulty,
            "total_score": s.total_score,
            "completed_at": s.completed_at,
        }
        for s in sessions
    ]


def _run_in_background(case_id: uuid.UUID, max_rounds: int | None) -> None:
    import asyncio

    async def _go():
        db = SessionLocal()
        try:
            await orchestrator.run_simulation(db, case_id, max_rounds)
        finally:
            db.close()

    asyncio.run(_go())
