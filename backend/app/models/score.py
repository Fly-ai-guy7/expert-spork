import uuid

from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UuidCol


class Score(Base, TimestampMixin):
    __tablename__ = "scores"

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    argument_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("arguments.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    factual: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    provable: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    unbiased: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    legal_law_based: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    overall: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rationale_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    rationale_en: Mapped[str | None] = mapped_column(Text, nullable=True)

    argument: Mapped["Argument"] = relationship(back_populates="score")  # noqa: F821
