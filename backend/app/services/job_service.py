"""Create a Job row and dispatch the matching Celery task.

In eager mode (.delay runs synchronously) the Job is already terminal by the
time these return; in real Redis mode it's QUEUED and the worker advances it.
"""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models import Job, JobKind, JobStatus


def enqueue_simulation(db: Session, case_id: uuid.UUID, max_rounds: int | None) -> Job:
    job = Job(case_id=case_id, kind=JobKind.SIMULATION, status=JobStatus.QUEUED)
    db.add(job)
    db.commit()
    db.refresh(job)

    from app.workers.tasks import run_simulation_task

    run_simulation_task.delay(str(job.id), str(case_id), max_rounds)
    db.refresh(job)
    return job


def enqueue_trainee_resume(
    db: Session,
    case_id: uuid.UUID,
    checkpoint_id: uuid.UUID,
    content_en: str | None,
    content_ar: str | None,
    citations: list[str] | None,
) -> Job:
    job = Job(case_id=case_id, kind=JobKind.TRAINEE_RESUME, status=JobStatus.QUEUED)
    db.add(job)
    db.commit()
    db.refresh(job)

    from app.workers.tasks import submit_trainee_task

    submit_trainee_task.delay(
        str(job.id), str(checkpoint_id), content_en, content_ar, citations
    )
    db.refresh(job)
    return job
