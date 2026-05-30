"""Admin endpoints — org-scoped, ADMIN-only.

Currently: LLM usage + cost rollup for the caller's organisation, plus the
month-to-date spend against the configured token budget.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app import pagination
from app.auth.deps import current_org_id_dep, require_role
from app.db import get_db
from app.models import AuditEvent, LlmUsage, Organization, Role, User
from app.services import usage_recorder

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/usage")
def usage_summary(
    request: Request,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(Role.ADMIN)),
    org_id: uuid.UUID = Depends(current_org_id_dep),
) -> dict:
    """Per-model token + cost rollup for the caller's org, plus month-to-date
    spend vs. budget."""
    rows = db.execute(
        select(
            LlmUsage.model,
            func.sum(LlmUsage.input_tokens),
            func.sum(LlmUsage.output_tokens),
            func.sum(LlmUsage.cached_tokens),
            func.sum(LlmUsage.cost_usd),
            func.count(LlmUsage.id),
        )
        .where(LlmUsage.org_id == org_id)
        .group_by(LlmUsage.model)
    ).all()

    by_model = [
        {
            "model": model,
            "input_tokens": int(inp or 0),
            "output_tokens": int(out or 0),
            "cached_tokens": int(cached or 0),
            "cost_usd": round(float(cost or 0.0), 4),
            "calls": int(calls or 0),
        }
        for model, inp, out, cached, cost, calls in rows
    ]

    org = db.get(Organization, org_id)
    mtd_tokens = usage_recorder.month_to_date_tokens(db, org_id)
    budget = org.monthly_token_budget if org else None

    return {
        "org_id": str(org_id),
        "total_cost_usd": round(sum(m["cost_usd"] for m in by_model), 4),
        "total_tokens": sum(m["input_tokens"] + m["output_tokens"] for m in by_model),
        "by_model": by_model,
        "month_to_date_tokens": mtd_tokens,
        "monthly_token_budget": budget,
        "over_budget": usage_recorder.is_over_budget(db, org_id),
    }


@router.get("/audit")
def audit_log(
    limit: int = pagination.DEFAULT_LIMIT,
    cursor: str | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(Role.ADMIN)),
    org_id: uuid.UUID = Depends(current_org_id_dep),
) -> dict:
    """Append-only audit trail for the caller's org. Cursor paginated,
    newest first. Optional filters on action verb + resource type."""
    limit = pagination.clamp_limit(limit)
    stmt = (
        select(AuditEvent)
        .where(AuditEvent.org_id == org_id)
        .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
    )
    if action:
        stmt = stmt.where(AuditEvent.action == action)
    if resource_type:
        stmt = stmt.where(AuditEvent.resource_type == resource_type)
    if cursor:
        c_ts, c_id = pagination.decode_cursor(cursor)
        stmt = stmt.where(
            or_(
                AuditEvent.created_at < c_ts,
                and_(AuditEvent.created_at == c_ts, AuditEvent.id < c_id),
            )
        )
    rows = db.execute(stmt.limit(limit + 1)).scalars().all()
    has_more = len(rows) > limit
    items = rows[:limit]
    return {
        "items": [
            {
                "id": str(r.id),
                "actor_email": r.actor_email,
                "action": r.action,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "before": r.before,
                "after": r.after,
                "ip": r.ip,
                "user_agent": r.user_agent,
                "request_id": r.request_id,
                "created_at": r.created_at.isoformat(),
            }
            for r in items
        ],
        "next_cursor": (
            pagination.encode_cursor(items[-1].created_at, items[-1].id)
            if has_more and items
            else None
        ),
    }
