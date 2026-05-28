"""add unverified_citations to arguments

Revision ID: 0005_unverified
Revises: 0004_courtroom
Create Date: 2025-01-05 00:00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_unverified"
down_revision: str | None = "0004_courtroom"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "arguments",
        sa.Column("unverified_citations", postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("arguments", "unverified_citations")
