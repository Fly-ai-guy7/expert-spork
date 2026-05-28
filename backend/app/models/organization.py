import uuid

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UuidCol


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    monthly_token_budget: Mapped[int | None] = mapped_column(Integer, nullable=True)

    memberships: Mapped[list["Membership"]] = relationship(  # noqa: F821
        back_populates="organization", cascade="all, delete-orphan"
    )
