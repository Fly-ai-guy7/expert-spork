import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UuidCol


class RefreshToken(Base, TimestampMixin):
    """Opaque, per-device refresh token. We store only the SHA-256 hash of
    the token secret so a leaked DB doesn't yield usable tokens.

    Each token belongs to a `family_id` — the chain of rotations seeded by
    the initial login. On refresh we revoke the presented token and issue a
    new one in the same family. If a *revoked* token is later presented (the
    classic stolen-then-replayed scenario), we revoke the entire family —
    the legitimate user has to log in again, but the attacker is also
    locked out.
    """

    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index("ix_refresh_user", "user_id"),
        Index("ix_refresh_family", "family_id"),
        Index("ix_refresh_hash", "token_hash", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    family_id: Mapped[uuid.UUID] = mapped_column(UuidCol(), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
