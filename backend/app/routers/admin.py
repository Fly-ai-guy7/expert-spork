"""Admin endpoints — org-scoped, ADMIN-only.

Currently: LLM usage + cost rollup for the caller's organisation, plus the
month-to-date spend against the configured token budget.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.deps import current_org_id_dep, require_role
from app.db import get_db
from app.models import LlmUsage, Organization, Role, User
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
