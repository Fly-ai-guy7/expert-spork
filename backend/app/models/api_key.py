import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UuidCol


class ApiKey(Base, TimestampMixin):
    """Long-lived API key for programmatic access (CI, server-to-server).

    Token format: `eq_<32 url-safe chars>`. We store the SHA-256 hash plus
    a non-secret 12-char display prefix so the UI can show "eq_aBcDeFgH…"
    without revealing the full secret. The raw token is only returned on
    create — once.
    """

    __tablename__ = "api_keys"
    __table_args__ = (
        Index("ix_api_keys_org", "org_id"),
        Index("ix_api_keys_hash", "token_hash", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UuidCol(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
