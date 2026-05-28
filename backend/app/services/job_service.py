"""Create a Job row and dispatch the matching Celery task.

In eager mode (.delay runs synchronously) the Job is already terminal by the
time these return; in real Redis mode it's QUEUED and the worker advances it.
"""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Job, JobKind, JobStatus


def find_job_by_key(db: Session, case_id: uuid.UUID, idempotency_key: str) -> Job | None:
    return db.execute(
        select(Job).where(
            Job.case_id == case_id,
            Job.idempotency_key == idempotency_key,
        )
    ).scalars().first()


def enqueue_simulation(
    db: Session,
    case_id: uuid.UUID,
    max_rounds: int | None,
    idempotency_key: str | None = None,
) -> Job:
    # Idempotency: a repeated request with the same key for this case returns
    # the original job instead of starting a duplicate run.
    if idempotency_key:
        existing = find_job_by_key(db, case_id, idempotency_key)
        if existing:
            return existing

    job = Job(
        case_id=case_id,
        kind=JobKind.SIMULATION,
        status=JobStatus.QUEUED,
        idempotency_key=idempotency_key,
    )
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
