"""Refresh-token issuance + rotation.

Refresh tokens are opaque 32-byte URL-safe strings. We store only the
SHA-256 hash in the DB, so a leaked database snapshot doesn't yield usable
tokens. On every exchange we rotate: revoke the presented token and issue
a fresh one in the same `family_id`. If a token that was already revoked
is later presented (the classic stolen-then-replayed pattern), the entire
family is revoked — the legitimate user has to re-login, but the attacker
is also locked out.
"""
from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import RefreshToken


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _request_meta(request: Request | None) -> tuple[str | None, str | None]:
    if request is None:
        return None, None
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    if ua and len(ua) > 512:
        ua = ua[:512]
    return ip, ua


def issue(
    db: Session,
    *,
    user_id: uuid.UUID,
    family_id: uuid.UUID | None = None,
    request: Request | None = None,
) -> str:
    """Mint a new refresh token. Returns the raw token string — the caller
    sends it to the client; only the hash is persisted."""
    raw = secrets.token_urlsafe(32)
    ip, ua = _request_meta(request)
    rt = RefreshToken(
        user_id=user_id,
        family_id=family_id or uuid.uuid4(),
        token_hash=_hash(raw),
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_ttl_days),
        ip=ip,
        user_agent=ua,
    )
    db.add(rt)
    db.commit()
    return raw


class RefreshError(Exception):
    """Refresh failed — caller should map to 401."""


def _revoke_family(db: Session, family_id: uuid.UUID) -> None:
    now = datetime.now(UTC)
    for rt in db.execute(
        select(RefreshToken).where(
            RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None)
        )
    ).scalars():
        rt.revoked_at = now
    db.commit()


def exchange(
    db: Session,
    *,
    raw_token: str,
    request: Request | None = None,
) -> tuple[uuid.UUID, str]:
    """Validate a refresh token, rotate it, and return (user_id, new_raw).

    Detects replay: if the presented token was already revoked, we revoke
    the whole family and refuse.
    """
    rt = db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == _hash(raw_token))
    ).scalar_one_or_none()
    if rt is None:
        raise RefreshError("unknown token")

    if rt.revoked_at is not None:
        # Replay of a token we already burned — revoke the family and bail.
        _revoke_family(db, rt.family_id)
        raise RefreshError("token replay detected")

    expires = rt.expires_at if rt.expires_at.tzinfo else rt.expires_at.replace(tzinfo=UTC)
    if expires < datetime.now(UTC):
        rt.revoked_at = datetime.now(UTC)
        db.commit()
        raise RefreshError("expired")

    rt.revoked_at = datetime.now(UTC)
    db.commit()
    new_raw = issue(db, user_id=rt.user_id, family_id=rt.family_id, request=request)
    return rt.user_id, new_raw


def revoke(db: Session, *, raw_token: str) -> bool:
    """Revoke a single refresh token's whole family (logout from this
    device chain). Returns True if anything was revoked."""
    rt = db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == _hash(raw_token))
    ).scalar_one_or_none()
    if rt is None:
        return False
    _revoke_family(db, rt.family_id)
    return True
