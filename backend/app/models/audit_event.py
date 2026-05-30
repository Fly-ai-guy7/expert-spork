import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import JsonCol, TimestampMixin, UuidCol


class AuditEvent(Base, TimestampMixin):
    """Append-only audit trail. Every mutation should emit one row.

    org_id / actor_user_id are nullable because some events (e.g.
    registration that creates the org) happen before either exists. We
    capture actor_email as a plain string so the trail survives user
    deletion.
    """

    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_org_created", "org_id", "created_at"),
        Index("ix_audit_actor", "actor_user_id"),
        Index("ix_audit_resource", "resource_type", "resource_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID | None] = mapped_column(
        UuidCol(), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UuidCol(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    actor_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    before: Mapped[dict | None] = mapped_column(JsonCol(), nullable=True)
    after: Mapped[dict | None] = mapped_column(JsonCol(), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
