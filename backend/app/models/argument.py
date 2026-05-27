import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Index, Integer, String, Text
from app.models.base import JsonCol, UuidCol
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin


class AgentRole(str, enum.Enum):
    PROSECUTION = "PROSECUTION"
    DEFENSE = "DEFENSE"
    JUDICIAL = "JUDICIAL"
    TRAINEE = "TRAINEE"


class Argument(Base, TimestampMixin):
    __tablename__ = "arguments"
    __table_args__ = (Index("ix_arguments_case_round", "case_id", "round_no"),)

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    debate_round_id: Mapped[uuid.UUID | None] = mapped_column(
        UuidCol(), ForeignKey("debate_rounds.id", ondelete="CASCADE"), nullable=True
    )
    agent: Mapped[AgentRole] = mapped_column(Enum(AgentRole, name="agent_role"), nullable=False)
    round_no: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    content_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    citations: Mapped[list | None] = mapped_column(JsonCol(), nullable=True)
    llm_used: Mapped[str | None] = mapped_column(String(64), nullable=True)

    case: Mapped["Case"] = relationship(back_populates="arguments")  # noqa: F821
    debate_round: Mapped["DebateRound | None"] = relationship(back_populates="arguments")  # noqa: F821
    score: Mapped["Score | None"] = relationship(  # noqa: F821
        back_populates="argument", uselist=False, cascade="all, delete-orphan"
    )
