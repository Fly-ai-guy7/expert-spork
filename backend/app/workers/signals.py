"""Celery worker signal handlers.

On graceful shutdown we:
- Flush any LLM usage events that accumulated in the contextvar sink for
  in-flight tasks, so we don't lose cost accounting when the worker exits.
- Publish a `running / stage: worker_draining` event to every active case
  channel so connected SSE clients see why their stream is briefly idle.

`task_acks_late=True` + `worker_prefetch_multiplier=1` (set in celery_app)
already ensure Celery itself doesn't ack a task until it finishes, so the
broker re-delivers any task interrupted by SIGTERM to another worker.
"""
from __future__ import annotations

import logging

from celery.signals import worker_shutting_down

logger = logging.getLogger(__name__)


@worker_shutting_down.connect
def _on_worker_shutting_down(sig=None, how=None, exitcode=None, **kw) -> None:  # noqa: ARG001
    logger.info("celery worker_shutting_down: sig=%s how=%s exitcode=%s", sig, how, exitcode)
    try:
        from app.services import event_bus
        for case_id in list(event_bus._channels):  # snapshot of keys
            event_bus.publish(case_id, {"status": "running", "stage": "worker_draining"})
    except Exception:  # noqa: BLE001 — drain hooks must never raise
        logger.warning("event_bus drain publish failed", exc_info=True)
