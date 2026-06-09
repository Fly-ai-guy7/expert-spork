"""Audit-log read access (admin only)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_db
from models import AuditLog, User
from schemas import AuditOut
from security import require_admin

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditOut])
def list_audit(
    action: str | None = Query(default=None, description="Filter by action"),
    limit: int = Query(default=100, le=500),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Most recent audit entries, newest first (admin only)."""
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
    if action:
        stmt = stmt.where(AuditLog.action == action)
    return list(db.scalars(stmt.limit(limit)))
