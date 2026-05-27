import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from app.models.base import UuidCol
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin


class Fact(Base, TimestampMixin):
    __tablename__ = "facts"

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    text_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    disputed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source_evidence_id: Mapped[uuid.UUID | None] = mapped_column(
        UuidCol(), ForeignKey("evidence.id", ondelete="SET NULL"), nullable=True
    )

    case: Mapped["Case"] = relationship(back_populates="facts")  # noqa: F821
