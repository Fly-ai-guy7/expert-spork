"""Celery application.

When `settings.celery_broker_url` is empty (dev + tests), Celery runs in
eager mode: `.delay()` executes the task synchronously in-process and returns
an EagerResult. Production sets CELERY_BROKER_URL / CELERY_RESULT_BACKEND to a
Redis URL and runs `celery -A app.workers.celery_app worker`.
"""
from __future__ import annotations

from celery import Celery

from app.config import settings

celery_app = Celery(
    "equalise",
    broker=settings.celery_broker_url or "memory://",
    backend=settings.celery_result_backend or "cache+memory://",
)

celery_app.conf.update(
    task_always_eager=settings.celery_eager,
    task_eager_propagates=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Ensure task modules are imported so they register with the app.
celery_app.autodiscover_tasks(["app.workers"])

import app.workers.tasks  # noqa: E402,F401 — registers tasks
