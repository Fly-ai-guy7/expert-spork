import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin


class TraineeRole(str, enum.Enum):
    PROSECUTION = "PROSECUTION"
    DEFENSE = "DEFENSE"


class TrainingSession(Base, TimestampMixin):
    __tablename__ = "training_sessions"
    __table_args__ = (Index("ix_training_user_completed", "user_id", "completed_at"),)

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    case_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    trainee_role: Mapped[TraineeRole] = mapped_column(
        Enum(TraineeRole, name="trainee_role"), nullable=False
    )
    difficulty: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    coaching_report: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    case: Mapped["Case"] = relationship(back_populates="training_sessions")  # noqa: F821
