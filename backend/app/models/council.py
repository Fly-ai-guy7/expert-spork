import uuid

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin


class CouncilVerdict(Base, TimestampMixin):
    """One judicial council member's independent verdict on a ruling."""

    __tablename__ = "council_verdicts"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ruling_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("rulings.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    member_llm: Mapped[str] = mapped_column(String(64), nullable=False)
    llm_used: Mapped[str | None] = mapped_column(String(64), nullable=True)
    plaintiff_success_prob: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    verdict: Mapped[str] = mapped_column(String(32), nullable=False)
    override_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reasoning_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    reasoning_en: Mapped[str | None] = mapped_column(Text, nullable=True)

    ruling: Mapped["Ruling"] = relationship(back_populates="council_verdicts")  # noqa: F821
