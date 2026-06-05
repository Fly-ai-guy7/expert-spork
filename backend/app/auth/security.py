"""Password hashing + JWT issuance / decoding.

Argon2id via passlib (no per-MAU fees, no external service). Tokens are
short-lived; refresh-token flow is deferred to Tier 1.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

_pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _pwd_context.verify(plain, hashed)
    except ValueError:
        return False


def issue_token(user_id: uuid.UUID, org_id: uuid.UUID | None, role: str | None) -> str:
    """Issue a signed JWT containing user_id + active org + role. Each token
    gets a unique `jti` so a same-second refresh doesn't yield byte-identical
    tokens (matters for revocation lists, audit, and replay reasoning)."""
    secret = settings.jwt_secret or "dev-insecure-do-not-use-in-prod"
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "org_id": str(org_id) if org_id else None,
        "role": role,
        "jti": uuid.uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_ttl_minutes)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode + verify a JWT. Raises JWTError on bad signature or expiry."""
    secret = settings.jwt_secret or "dev-insecure-do-not-use-in-prod"
    return jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])


class InvalidToken(Exception):
    """Wraps jose.JWTError for clean handling at the dep boundary."""


def parse_bearer(token: str) -> dict[str, Any]:
    try:
        return decode_token(token)
    except JWTError as e:
        raise InvalidToken(str(e)) from e
