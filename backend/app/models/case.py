import enum
import uuid

from sqlalchemy import Enum, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import JsonCol, TimestampMixin, UuidCol


class CaseStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    RUNNING = "RUNNING"
    PAUSED_HIL = "PAUSED_HIL"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class CaseSource(str, enum.Enum):
    USER_AUTHORED = "USER_AUTHORED"
    AI_GENERATED = "AI_GENERATED"


class Case(Base, TimestampMixin):
    __tablename__ = "cases"
    __table_args__ = (
        Index("ix_cases_status", "status"),
        Index("ix_cases_source_difficulty", "source", "difficulty"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    title_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    title_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    jurisdiction: Mapped[str] = mapped_column(String(64), default="EG", nullable=False)
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, name="case_status"), default=CaseStatus.DRAFT, nullable=False
    )
    language_primary: Mapped[str] = mapped_column(String(2), default="en", nullable=False)
    source: Mapped[CaseSource] = mapped_column(
        Enum(CaseSource, name="case_source"), default=CaseSource.USER_AUTHORED, nullable=False
    )
    difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    area_of_law: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    max_rounds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Specialist agent outputs
    procedural_analysis: Mapped[dict | None] = mapped_column(JsonCol(), nullable=True)
    precedent_analysis: Mapped[dict | None] = mapped_column(JsonCol(), nullable=True)
    damages_estimate: Mapped[dict | None] = mapped_column(JsonCol(), nullable=True)
    # Courtroom agent outputs
    docket: Mapped[dict | None] = mapped_column(JsonCol(), nullable=True)
    expert_testimony: Mapped[dict | None] = mapped_column(JsonCol(), nullable=True)
    mediation_proposal: Mapped[dict | None] = mapped_column(JsonCol(), nullable=True)
    cassation_review: Mapped[dict | None] = mapped_column(JsonCol(), nullable=True)

    parties: Mapped[list["Party"]] = relationship(back_populates="case", cascade="all, delete-orphan")  # noqa: F821
    facts: Mapped[list["Fact"]] = relationship(back_populates="case", cascade="all, delete-orphan")  # noqa: F821
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="case", cascade="all, delete-orphan")  # noqa: F821
    arguments: Mapped[list["Argument"]] = relationship(back_populates="case", cascade="all, delete-orphan")  # noqa: F821
    debate_rounds: Mapped[list["DebateRound"]] = relationship(back_populates="case", cascade="all, delete-orphan")  # noqa: F821
    ruling: Mapped["Ruling | None"] = relationship(back_populates="case", uselist=False, cascade="all, delete-orphan")  # noqa: F821
    outcome: Mapped["Outcome | None"] = relationship(back_populates="case", uselist=False, cascade="all, delete-orphan")  # noqa: F821
    checkpoints: Mapped[list["HilCheckpoint"]] = relationship(back_populates="case", cascade="all, delete-orphan")  # noqa: F821
    training_sessions: Mapped[list["TrainingSession"]] = relationship(back_populates="case", cascade="all, delete-orphan")  # noqa: F821
