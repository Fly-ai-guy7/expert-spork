import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UuidCol


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    memberships: Mapped[list["Membership"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
