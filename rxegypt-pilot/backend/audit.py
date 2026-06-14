"""Audit-trail helper.

Records sensitive actions to the append-only ``audit_logs`` table for PDPL
accountability and pharmacy traceability. The row is added to the caller's
session and persisted by the caller's existing ``commit()`` (so it is atomic
with the action it describes).
"""
from sqlalchemy.orm import Session

from models import AuditLog


def record(db: Session, actor_email: str, action: str, target: str = "", detail: str = "") -> None:
    db.add(AuditLog(actor_email=actor_email or "", action=action, target=target, detail=detail))
