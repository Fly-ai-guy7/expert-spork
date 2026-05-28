import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import JsonCol, TimestampMixin, UuidCol


class Ruling(Base, TimestampMixin):
    __tablename__ = "rulings"

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    plaintiff_success_prob: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    critical_evidence_gaps: Mapped[list | None] = mapped_column(JsonCol(), nullable=True)
    precedent_refs: Mapped[list | None] = mapped_column(JsonCol(), nullable=True)
    text_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    override_applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    case: Mapped["Case"] = relationship(back_populates="ruling")  # noqa: F821
