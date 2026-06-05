"""FastAPI dependencies for auth + RBAC."""
from __future__ import annotations

import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import api_keys as api_keys_svc
from app.auth.security import InvalidToken, parse_bearer
from app.auth.tenant import AuthContext, set_context
from app.db import bind_tenant, get_db
from app.models import Membership, Role, User

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def current_user(
    request: Request,
    token: str | None = Depends(oauth2),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")

    # API-key path: token starts with `eq_`. Maps to the key's creator (or a
    # synthetic-actor pattern if the creator is gone) with the key's org as
    # the active tenant. Role defaults to ADMIN for programmatic access.
    if api_keys_svc.looks_like_api_key(token):
        key = api_keys_svc.verify(db, token)
        if key is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or revoked API key")
        actor = (
            db.execute(select(User).where(User.id == key.created_by_user_id, User.is_active.is_(True))).scalar_one_or_none()
            if key.created_by_user_id
            else None
        )
        if actor is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "API key creator unavailable")
        m = db.execute(
            select(Membership).where(Membership.user_id == actor.id, Membership.org_id == key.org_id)
        ).scalar_one_or_none()
        if m is None:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "API key creator no longer in org")
        ctx = AuthContext(user_id=actor.id, org_id=key.org_id, role=m.role.value)
        set_context(ctx)
        request.state.auth = ctx
        bind_tenant(db, key.org_id)
        return actor

    try:
        payload = parse_bearer(token)
    except InvalidToken as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid token: {e}") from e
    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Malformed token") from e
    user = db.execute(select(User).where(User.id == user_id, User.is_active.is_(True))).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")

    org_id = uuid.UUID(payload["org_id"]) if payload.get("org_id") else None
    role = payload.get("role")
    # Cross-check: claimed org must still match an active membership
    if org_id:
        m = db.execute(
            select(Membership).where(Membership.user_id == user_id, Membership.org_id == org_id)
        ).scalar_one_or_none()
        if not m:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Membership revoked")
        role = m.role.value
    ctx = AuthContext(user_id=user.id, org_id=org_id, role=role)
    set_context(ctx)
    request.state.auth = ctx
    # Bind the org to THIS session so the tenant-filter event hook scopes every
    # Case query for the remainder of the request (works across threadpool
    # boundaries, unlike the contextvar).
    if org_id is not None:
        bind_tenant(db, org_id)
    return user


def require_role(*allowed: Role | str) -> Callable:
    """Dep factory that enforces the authenticated user holds one of the allowed roles."""
    allowed_str = {r.value if isinstance(r, Role) else r for r in allowed}

    def _checker(request: Request, user: User = Depends(current_user)) -> User:
        ctx: AuthContext = request.state.auth
        if ctx.role not in allowed_str:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Role {ctx.role!r} not in {sorted(allowed_str)}",
            )
        return user

    return _checker


def current_org_id_dep(request: Request, _user: User = Depends(current_user)) -> uuid.UUID:
    ctx: AuthContext = request.state.auth
    if ctx.org_id is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No active organisation on token")
    return ctx.org_id
