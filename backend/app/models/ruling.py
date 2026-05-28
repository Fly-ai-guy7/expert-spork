import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin


class Ruling(Base, TimestampMixin):
    __tablename__ = "rulings"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    plaintiff_success_prob: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    critical_evidence_gaps: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    precedent_refs: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    text_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    override_applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    council_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    council_vote: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    dissent_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    dissent_en: Mapped[str | None] = mapped_column(Text, nullable=True)

    case: Mapped["Case"] = relationship(back_populates="ruling")  # noqa: F821
    council_verdicts: Mapped[list["CouncilVerdict"]] = relationship(  # noqa: F821
        back_populates="ruling", cascade="all, delete-orphan"
    )
