from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["TimestampMixin", "UuidCol", "JsonCol"]


def _utcnow() -> datetime:
    return datetime.now(UTC)


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
    # Python-side defaults give microsecond precision that round-trips
    # consistently (SQLite's CURRENT_TIMESTAMP drops sub-second precision,
    # which breaks keyset-cursor comparisons). server_default stays as a
    # fallback for raw SQL inserts that bypass the ORM.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        server_default=func.now(),
        nullable=False,
    )
