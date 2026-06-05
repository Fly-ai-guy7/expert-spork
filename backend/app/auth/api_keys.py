"""API key issuance, lookup, and revocation.

Format: `eq_<32 url-safe chars>`. The first 12 characters of the secret
form a non-secret display prefix, shown in the UI ("eq_aBcDeFgH…") so
admins can identify a key without seeing the full secret. Only the
SHA-256 hash is persisted.
"""
from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ApiKey

PREFIX = "eq_"
SECRET_BYTES = 24  # ~32 base64 chars
DISPLAY_PREFIX_LEN = 12  # "eq_" + first 9 of the secret


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def looks_like_api_key(token: str) -> bool:
    return token.startswith(PREFIX)


def issue(
    db: Session,
    *,
    org_id: uuid.UUID,
    name: str,
    created_by_user_id: uuid.UUID | None = None,
    expires_at: datetime | None = None,
) -> tuple[ApiKey, str]:
    """Mint a new key. Returns (row, raw_token). The caller MUST surface the
    raw_token to the requester exactly once; we never store it."""
    secret = secrets.token_urlsafe(SECRET_BYTES)
    raw = f"{PREFIX}{secret}"
    row = ApiKey(
        org_id=org_id,
        created_by_user_id=created_by_user_id,
        name=name,
        prefix=raw[:DISPLAY_PREFIX_LEN],
        token_hash=_hash(raw),
        expires_at=expires_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row, raw


def verify(db: Session, raw_token: str) -> ApiKey | None:
    """Return the matching ApiKey if the token is valid + active, else None.
    Bumps last_used_at on a successful match."""
    if not looks_like_api_key(raw_token):
        return None
    row = db.execute(
        select(ApiKey).where(ApiKey.token_hash == _hash(raw_token))
    ).scalar_one_or_none()
    if row is None or row.revoked_at is not None:
        return None
    if row.expires_at is not None:
        exp = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=UTC)
        if exp < datetime.now(UTC):
            return None
    row.last_used_at = datetime.now(UTC)
    db.commit()
    return row


def revoke(db: Session, *, key_id: uuid.UUID, org_id: uuid.UUID) -> bool:
    """Revoke an org's key by id. Returns True if anything changed."""
    row = db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.org_id == org_id)
    ).scalar_one_or_none()
    if row is None or row.revoked_at is not None:
        return False
    row.revoked_at = datetime.now(UTC)
    db.commit()
    return True
