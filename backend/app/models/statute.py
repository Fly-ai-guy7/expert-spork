import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from app.models.base import JsonCol, UuidCol
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin


class Statute(Base, TimestampMixin):
    __tablename__ = "statutes"
    __table_args__ = (UniqueConstraint("law_number", "year", name="uq_statute_law_year"),)

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    law_number: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    short_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    title_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    title_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain_tags: Mapped[list | None] = mapped_column(JsonCol(), nullable=True)

    articles: Mapped[list["StatuteArticle"]] = relationship(
        back_populates="statute", cascade="all, delete-orphan"
    )


class StatuteArticle(Base, TimestampMixin):
    __tablename__ = "statute_articles"
    __table_args__ = (
        UniqueConstraint("statute_id", "article_number", name="uq_article_statute_num"),
        Index("ix_articles_statute", "statute_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    statute_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("statutes.id", ondelete="CASCADE"), nullable=False
    )
    article_number: Mapped[str] = mapped_column(String(32), nullable=False)
    text_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list | None] = mapped_column(JsonCol(), nullable=True)

    statute: Mapped[Statute] = relationship(back_populates="articles")
