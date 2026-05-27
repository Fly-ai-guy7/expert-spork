import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Text
from app.models.base import JsonCol, UuidCol
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin


class HilStage(str, enum.Enum):
    POST_EVIDENCE = "POST_EVIDENCE"
    POST_PROSECUTION = "POST_PROSECUTION"
    PRE_DEFENSE_REBUTTAL = "PRE_DEFENSE_REBUTTAL"
    PRE_RULING = "PRE_RULING"
    TRAINEE_TURN = "TRAINEE_TURN"


class HilStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    MODIFIED = "MODIFIED"
    HALTED = "HALTED"
    SUBMITTED = "SUBMITTED"


class HilCheckpoint(Base, TimestampMixin):
    __tablename__ = "hil_checkpoints"
    __table_args__ = (Index("ix_hil_case_status", "case_id", "status"),)

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    stage: Mapped[HilStage] = mapped_column(Enum(HilStage, name="hil_stage"), nullable=False)
    status: Mapped[HilStatus] = mapped_column(
        Enum(HilStatus, name="hil_status"), default=HilStatus.PENDING, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    modified_payload: Mapped[dict | None] = mapped_column(JsonCol(), nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    case: Mapped["Case"] = relationship(back_populates="checkpoints")  # noqa: F821
