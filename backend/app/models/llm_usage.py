import uuid

from sqlalchemy import Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UuidCol


class LlmUsage(Base, TimestampMixin):
    """One row per LLM call. org_id/case_id are nullable because the
    orchestrator can run outside a tenant context (e.g. internal jobs)."""

    __tablename__ = "llm_usage"
    __table_args__ = (
        Index("ix_llm_usage_org_created", "org_id", "created_at"),
        Index("ix_llm_usage_case", "case_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID | None] = mapped_column(
        UuidCol(), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UuidCol(), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cached_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
