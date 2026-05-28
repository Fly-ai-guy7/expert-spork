"""Tenant context — current user + active org propagated via contextvars.

Set by the auth dependency on every authenticated request. Consumed by
the tenant-filter event hook in `app.db`. When unset (e.g. background
tasks, orchestrator tests calling services directly), no auto-filter is
applied — services that need scoping must pass org_id explicitly.
"""
from __future__ import annotations

import uuid
from contextvars import ContextVar
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthContext:
    user_id: uuid.UUID
    org_id: uuid.UUID | None
    role: str | None


_ctx: ContextVar[AuthContext | None] = ContextVar("equalise_auth_ctx", default=None)


def set_context(ctx: AuthContext | None) -> None:
    _ctx.set(ctx)


def current() -> AuthContext | None:
    return _ctx.get()


def current_org_id() -> uuid.UUID | None:
    c = _ctx.get()
    return c.org_id if c else None
