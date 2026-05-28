import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import current_user, require_role
from app.db import get_db
from app.i18n import Lang
from app.models import Case, CaseStatus, Role, TraineeRole, TrainingSession, User
from app.schemas.case import StartTrainingIn
from app.services import job_service, pdf_service, training_analytics

router = APIRouter(prefix="", tags=["training"])


@router.post("/cases/{case_id}/run-training", status_code=202)
def run_training(
    case_id: uuid.UUID,
    payload: StartTrainingIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    case = db.execute(select(Case).where(Case.id == case_id)).scalar_one_or_none()
    if not case:
        raise HTTPException(404, "Case not found")
    try:
        role = TraineeRole(payload.trainee_role)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e

    ts = TrainingSession(
        user_id=payload.user_id or user.email,
        case_id=case_id,
        trainee_role=role,
        difficulty=payload.difficulty,
        started_at=datetime.now(UTC),
    )
    db.add(ts)
    case.status = CaseStatus.DRAFT  # ensure it can be started
    db.commit()
    db.refresh(ts)

    job = job_service.enqueue_simulation(db, case_id, None)
    return {
        "training_session_id": str(ts.id),
        "case_id": str(case_id),
        "job_id": str(job.id),
        "status": job.status.value,
    }


@router.get("/training/{session_id}/coaching")
def get_coaching(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> dict:
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


@router.get("/training/{session_id}/coaching.pdf")
def get_coaching_pdf(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> Response:
    ts = db.execute(
        select(TrainingSession).where(TrainingSession.id == session_id)
    ).scalar_one_or_none()
    if not ts:
        raise HTTPException(404, "Training session not found")
    if not ts.coaching_report:
        raise HTTPException(409, "Coaching report not yet generated")
    case = db.execute(select(Case).where(Case.id == ts.case_id)).scalar_one()
    lang = Lang(case.language_primary)
    payload = {
        **(ts.coaching_report or {}),
        "session": {
            "id": str(ts.id),
            "trainee_role": ts.trainee_role.value,
            "difficulty": ts.difficulty,
            "user_id": ts.user_id,
        },
        "case": {
            "id": str(case.id),
            "title_en": case.title_en,
            "title_ar": case.title_ar,
            "area_of_law": case.area_of_law,
        },
    }
    pdf_bytes = pdf_service.render_coaching_pdf(payload, lang)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="coaching-{session_id}.pdf"'},
    )


@router.get("/training/progress")
def get_progress(
    user_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> dict:
    """Per-trainee learning signal: averages, weakest dimension, trend."""
    return training_analytics.progress(db, user_id)


@router.get("/training/cohort")
def get_cohort(
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(Role.INSTRUCTOR, Role.ADMIN)),
) -> dict:
    """Instructor view: grade distribution, dimension averages, top missed statutes."""
    return training_analytics.cohort(db)


@router.get("/training/recommendations")
def get_recommendations(
    user_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> dict:
    """What this trainee should practice next."""
    return training_analytics.recommendations(db, user_id)


@router.get("/training/sessions")
def list_training_sessions(
    user_id: str | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(current_user),
) -> list[dict]:
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
