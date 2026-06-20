import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin


class CounselLog(Base, TimestampMixin):
    """One Advisory Counsel call: the trainee's draft + the advice returned."""

    __tablename__ = "counsel_logs"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    training_session_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("training_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    checkpoint_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hil_checkpoints.id", ondelete="SET NULL"),
        nullable=True,
    )
    trainee_role: Mapped[str] = mapped_column(String(32), nullable=False)
    draft_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    draft_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    citations: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    advice: Mapped[dict] = mapped_column(JSONB, nullable=False)
    llm_used: Mapped[str | None] = mapped_column(String(64), nullable=True)

    training_session: Mapped["TrainingSession | None"] = relationship(  # noqa: F821
        back_populates="counsel_logs"
    )
