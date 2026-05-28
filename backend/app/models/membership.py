import enum
import uuid

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UuidCol


class Role(str, enum.Enum):
    TRAINEE = "TRAINEE"
    INSTRUCTOR = "INSTRUCTOR"
    ADMIN = "ADMIN"


class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "org_id", name="uq_memberships_user_org"),)

    id: Mapped[uuid.UUID] = mapped_column(UuidCol(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UuidCol(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[Role] = mapped_column(Enum(Role, name="membership_role"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="memberships")  # noqa: F821
    organization: Mapped["Organization"] = relationship(back_populates="memberships")  # noqa: F821
