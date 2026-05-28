"""Cursor pagination helpers.

Opaque base64 cursor over (created_at, id) — stable under inserts, unlike
offset pagination. Ordering is created_at DESC, id DESC (id breaks ties so
rows created in the same tick still paginate deterministically).
"""
from __future__ import annotations

import base64
import binascii
import uuid
from datetime import datetime

from fastapi import HTTPException

MAX_LIMIT = 200
DEFAULT_LIMIT = 50


def clamp_limit(limit: int) -> int:
    return max(1, min(limit, MAX_LIMIT))


def encode_cursor(created_at: datetime, row_id: uuid.UUID) -> str:
    raw = f"{created_at.isoformat()}|{row_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, uuid.UUID]:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode()).decode()
        ts_str, id_str = raw.split("|", 1)
        return datetime.fromisoformat(ts_str), uuid.UUID(id_str)
    except (ValueError, binascii.Error) as e:
        raise HTTPException(400, "Invalid cursor") from e
