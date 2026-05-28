"""auth: users, organizations, memberships + org_id on cases

Revision ID: 0006_auth
Revises: 0005_unverified
Create Date: 2025-01-06 00:00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_auth"
down_revision: str | None = "0005_unverified"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False, unique=True),
        sa.Column("monthly_token_budget", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "memberships",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Enum("TRAINEE", "INSTRUCTOR", "ADMIN", name="membership_role"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "org_id", name="uq_memberships_user_org"),
    )

    op.add_column(
        "cases",
        sa.Column("org_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True),
    )
    op.add_column(
        "cases",
        sa.Column("created_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_cases_org", "cases", ["org_id"])


def downgrade() -> None:
    op.drop_index("ix_cases_org", table_name="cases")
    op.drop_column("cases", "created_by_user_id")
    op.drop_column("cases", "org_id")
    op.drop_table("memberships")
    op.drop_table("users")
    op.drop_table("organizations")
