"""LLM usage accounting.

The LLM layer is context-free (it doesn't know which org/case a call belongs
to), so usage events are pushed onto a contextvar sink by the factory's
on_usage callback during a pipeline run. The orchestrator — which holds the
db session + case — flushes the sink into `llm_usage` rows with tenant
attribution.

Costs use published per-model rates (USD per 1M tokens). Unknown models cost
0 rather than raising; pricing drifts and we'd rather under-report than crash
a pipeline.
"""
from __future__ import annotations

import uuid
from contextvars import ContextVar
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

# USD per 1,000,000 tokens: (input, output)
COST_PER_MTOKEN: dict[str, tuple[float, float]] = {
    "claude-opus-4-7": (15.0, 75.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "deepseek-chat": (0.27, 1.10),
}

_sink: ContextVar[list[dict] | None] = ContextVar("llm_usage_sink", default=None)


def record(provider: str, model: str, usage: dict) -> None:
    """Append a usage event. Called from the LLM layer; never raises."""
    sink = _sink.get()
    if sink is None:
        sink = []
        _sink.set(sink)
    sink.append({"provider": provider, "model": model, "usage": dict(usage or {})})


def _drain() -> list[dict]:
    sink = _sink.get() or []
    _sink.set([])
    return sink


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = COST_PER_MTOKEN.get(model)
    if not rates:
        return 0.0
    return input_tokens / 1_000_000 * rates[0] + output_tokens / 1_000_000 * rates[1]


def flush(db: Session, *, org_id: uuid.UUID | None, case_id: uuid.UUID | None) -> int:
    """Persist accumulated usage events as llm_usage rows. Returns row count."""
    from app.models import LlmUsage

    rows = _drain()
    for r in rows:
        u = r["usage"]
        inp = int(u.get("input_tokens", 0) or 0)
        out = int(u.get("output_tokens", 0) or 0)
        cached = int(u.get("cache_read_input_tokens", 0) or 0)
        db.add(
            LlmUsage(
                org_id=org_id,
                case_id=case_id,
                provider=r["provider"],
                model=r["model"],
                input_tokens=inp,
                output_tokens=out,
                cached_tokens=cached,
                cost_usd=cost_usd(r["model"], inp, out),
            )
        )
    if rows:
        db.commit()
    return len(rows)


def _month_start(now: datetime | None = None) -> datetime:
    now = now or datetime.now(UTC)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def month_to_date_tokens(db: Session, org_id: uuid.UUID) -> int:
    from app.models import LlmUsage

    total = db.execute(
        select(func.coalesce(func.sum(LlmUsage.input_tokens + LlmUsage.output_tokens), 0)).where(
            LlmUsage.org_id == org_id,
            LlmUsage.created_at >= _month_start(),
        )
    ).scalar_one()
    return int(total or 0)


def is_over_budget(db: Session, org_id: uuid.UUID | None) -> bool:
    """True when the org has a monthly_token_budget and has met/exceeded it."""
    if org_id is None:
        return False
    from app.models import Organization

    org = db.get(Organization, org_id)
    if org is None or not org.monthly_token_budget:
        return False
    return month_to_date_tokens(db, org_id) >= org.monthly_token_budget
