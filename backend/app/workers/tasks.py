"""Celery tasks wrapping the async orchestrator.

Each task owns its DB session and updates the Job row through its lifecycle:
QUEUED -> RUNNING -> (PAUSED | COMPLETE | FAILED). The orchestrator itself is
idempotent, so a retried task resumes cleanly rather than duplicating work.

Tenant note: tasks run WITHOUT a bound tenant (no auth context), so the
Case tenant-filter hook is inert here — the orchestrator legitimately needs
to read/write the whole case graph. Authorization happened at enqueue time
in the router.
"""
from __future__ import annotations

import asyncio
import uuid

from app.db import SessionLocal
from app.models import Job, JobStatus
from app.services import orchestrator
from app.workers.celery_app import celery_app


def _set_job(db, job_id: uuid.UUID, **fields) -> None:
    job = db.get(Job, job_id)
    if job is None:
        return
    for k, v in fields.items():
        setattr(job, k, v)
    db.commit()


def _finish_status(result: dict) -> JobStatus:
    status = (result or {}).get("status")
    if status == "PAUSED_HIL":
        return JobStatus.PAUSED
    if status == "COMPLETE":
        return JobStatus.COMPLETE
    return JobStatus.FAILED


@celery_app.task(name="equalise.run_simulation", bind=True)
def run_simulation_task(self, job_id: str, case_id: str, max_rounds: int | None = None) -> dict:
    jid = uuid.UUID(job_id)
    cid = uuid.UUID(case_id)
    db = SessionLocal()
    try:
        _set_job(db, jid, status=JobStatus.RUNNING, task_id=self.request.id)
        result = asyncio.run(orchestrator.run_simulation(db, cid, max_rounds))
        _set_job(db, jid, status=_finish_status(result), result=result)
        return result
    except Exception as exc:  # noqa: BLE001 — record then re-raise for Celery
        _set_job(db, jid, status=JobStatus.FAILED, error=str(exc))
        raise
    finally:
        db.close()


@celery_app.task(name="equalise.submit_trainee", bind=True)
def submit_trainee_task(
    self,
    job_id: str,
    checkpoint_id: str,
    content_en: str | None,
    content_ar: str | None,
    citations: list[str] | None,
) -> dict:
    jid = uuid.UUID(job_id)
    db = SessionLocal()
    try:
        _set_job(db, jid, status=JobStatus.RUNNING, task_id=self.request.id)
        result = asyncio.run(
            orchestrator.submit_trainee_argument(
                db, checkpoint_id, content_en, content_ar, citations
            )
        )
        _set_job(db, jid, status=_finish_status(result), result=result)
        return result
    except Exception as exc:  # noqa: BLE001
        _set_job(db, jid, status=JobStatus.FAILED, error=str(exc))
        raise
    finally:
        db.close()
