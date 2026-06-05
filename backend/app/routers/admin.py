"""Admin endpoints — org-scoped, ADMIN-only.

Currently: LLM usage + cost rollup for the caller's organisation, plus the
month-to-date spend against the configured token budget.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app import pagination
from app.auth import api_keys as api_keys_svc
from app.auth.deps import current_org_id_dep, require_role
from app.db import get_db
from app.models import ApiKey, AuditEvent, LlmUsage, Organization, Role, User
from app.services import audit, usage_recorder

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


# --- API keys ---------------------------------------------------------------

class ApiKeyCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ApiKeyOut(BaseModel):
    id: uuid.UUID
    name: str
    prefix: str
    last_used_at: str | None
    expires_at: str | None
    revoked_at: str | None
    created_at: str


class ApiKeyCreateOut(ApiKeyOut):
    raw_token: str  # surfaced exactly once


def _serialize_key(k: ApiKey) -> dict:
    return {
        "id": str(k.id),
        "name": k.name,
        "prefix": k.prefix,
        "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
        "expires_at": k.expires_at.isoformat() if k.expires_at else None,
        "revoked_at": k.revoked_at.isoformat() if k.revoked_at else None,
        "created_at": k.created_at.isoformat(),
    }


@router.post("/api-keys", status_code=201)
def create_api_key(
    payload: ApiKeyCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(Role.ADMIN)),
    org_id: uuid.UUID = Depends(current_org_id_dep),
) -> dict:
    """Mint a new API key for the caller's org. `raw_token` is returned ONCE;
    only its hash is persisted."""
    row, raw = api_keys_svc.issue(db, org_id=org_id, name=payload.name, created_by_user_id=user.id)
    audit.record(
        db, action="API_KEY_CREATE", resource_type="api_key", resource_id=row.id,
        after={"name": row.name, "prefix": row.prefix}, actor=user, request=request,
    )
    return {**_serialize_key(row), "raw_token": raw}


@router.get("/api-keys")
def list_api_keys(
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(Role.ADMIN)),
    org_id: uuid.UUID = Depends(current_org_id_dep),
) -> dict:
    rows = db.execute(
        select(ApiKey).where(ApiKey.org_id == org_id).order_by(ApiKey.created_at.desc())
    ).scalars().all()
    return {"items": [_serialize_key(r) for r in rows]}


@router.delete("/api-keys/{key_id}", status_code=204)
def revoke_api_key(
    key_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(Role.ADMIN)),
    org_id: uuid.UUID = Depends(current_org_id_dep),
) -> None:
    if not api_keys_svc.revoke(db, key_id=key_id, org_id=org_id):
        raise HTTPException(404, "API key not found")
    audit.record(
        db, action="API_KEY_REVOKE", resource_type="api_key", resource_id=key_id,
        actor=user, request=request,
    )
