from datetime import datetime

from sqlalchemy import JSON, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["TimestampMixin", "UuidCol", "JsonCol"]


def _json_type():
    try:
        from sqlalchemy.dialects.postgresql import JSONB

        return JSON().with_variant(JSONB(), "postgresql")
    except ImportError:  # pragma: no cover
        return JSON()


def UuidCol():
    """Cross-DB UUID column type. Native UUID on Postgres, CHAR(32) on SQLite."""
    return Uuid()


def JsonCol():
    """Cross-DB JSON column type. JSONB on Postgres, JSON on SQLite."""
    return _json_type()


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
