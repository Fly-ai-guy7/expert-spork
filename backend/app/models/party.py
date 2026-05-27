import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from app.models.base import UuidCol
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin


class PartyRole(str, enum.Enum):
    PLAINTIFF = "PLAINTIFF"
    DEFENDANT = "DEFENDANT"
    THIRD_PARTY = "THIRD_PARTY"


class PartyKind(str, enum.Enum):
    NATURAL = "NATURAL"
    LEGAL = "LEGAL"


class Party(Base, TimestampMixin):
    __tablename__ = "parties"

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[PartyRole] = mapped_column(Enum(PartyRole, name="party_role"), nullable=False)
    kind: Mapped[PartyKind] = mapped_column(
        Enum(PartyKind, name="party_kind"), default=PartyKind.NATURAL, nullable=False
    )
    name_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    name_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    case: Mapped["Case"] = relationship(back_populates="parties")  # noqa: F821
