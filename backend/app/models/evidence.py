import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UuidCol


class EvidenceKind(str, enum.Enum):
    DOCUMENT = "DOCUMENT"
    WITNESS = "WITNESS"
    PHYSICAL = "PHYSICAL"


class Evidence(Base, TimestampMixin):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[EvidenceKind] = mapped_column(
        Enum(EvidenceKind, name="evidence_kind"), nullable=False
    )
    title_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    title_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    case: Mapped["Case"] = relationship(back_populates="evidence")  # noqa: F821
