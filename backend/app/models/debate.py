import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UuidCol


class DebateRound(Base, TimestampMixin):
    __tablename__ = "debate_rounds"

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    round_no: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)
    team_a_llm: Mapped[str | None] = mapped_column(String(64), nullable=True)
    team_b_llm: Mapped[str | None] = mapped_column(String(64), nullable=True)

    case: Mapped["Case"] = relationship(back_populates="debate_rounds")  # noqa: F821
    arguments: Mapped[list["Argument"]] = relationship(  # noqa: F821
        back_populates="debate_round", cascade="all, delete-orphan"
    )
