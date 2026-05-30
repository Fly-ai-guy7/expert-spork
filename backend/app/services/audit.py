"""Audit logging.

`record()` is the single chokepoint: routers call it after every mutation
with a stable action verb and the (optional) before/after diff. It pulls
actor + request metadata from the FastAPI Request when supplied, so callers
don't have to plumb those values themselves.

Audit writes are append-only and best-effort: a failed insert logs at
WARNING but never blocks the business operation.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.models import AuditEvent, User
from app.observability.logging import request_id_var

logger = logging.getLogger(__name__)


def record(
    db: Session,
    *,
    action: str,
    resource_type: str | None = None,
    resource_id: str | uuid.UUID | None = None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    actor: User | None = None,
    org_id: uuid.UUID | None = None,
    request: Request | None = None,
) -> None:
    try:
        ip = None
        ua = None
        if request is not None:
            ip = request.client.host if request.client else None
            ua = request.headers.get("user-agent")
            # Honour the actor on request.state.auth when caller didn't pass one
            if actor is None:
                auth = getattr(request.state, "auth", None)
                if auth and auth.user_id:
                    actor = db.get(User, auth.user_id)
            if org_id is None:
                auth = getattr(request.state, "auth", None)
                if auth:
                    org_id = auth.org_id

        evt = AuditEvent(
            org_id=org_id,
            actor_user_id=actor.id if actor else None,
            actor_email=actor.email if actor else None,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            before=before,
            after=after,
            ip=ip,
            user_agent=ua,
            request_id=request_id_var.get(),
        )
        db.add(evt)
        db.commit()
    except Exception:  # noqa: BLE001 — audit must never block business logic
        logger.warning("audit.record failed for action=%s", action, exc_info=True)
        try:
            db.rollback()
        except Exception:  # noqa: BLE001
            pass
