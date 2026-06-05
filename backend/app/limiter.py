"""Shared rate limiter.

Module-level singleton so per-route `@limiter.limit(...)` decorators in
routers can reach the same instance that the SlowAPIMiddleware enforces.
Per-route limits are looked up via callables so tests (and config reloads)
can adjust them without rebuilding the limiter.
"""
from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings


def _default_limit() -> str:
    """Re-evaluated per request, so tests / config reloads take effect
    without rebuilding the Limiter."""
    return settings.rate_limit_default


def run_limit() -> str:
    """Per-IP ceiling for POST /cases/{id}/run — each call kicks off an LLM
    pipeline, so we hold it tighter than the global default."""
    return settings.rate_limit_run


def generate_limit() -> str:
    """Per-IP ceiling for POST /cases/generate — AI case generation is the
    single most expensive call, so the tightest limit."""
    return settings.rate_limit_generate


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[_default_limit],
    enabled=settings.rate_limit_enabled,
)


def sync_enabled() -> None:
    """Refresh the limiter's enabled flag from settings. Called by
    create_app() so tests that toggle rate_limit_enabled take effect."""
    limiter.enabled = settings.rate_limit_enabled
    limiter.reset()
