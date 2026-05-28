"""add max_rounds to cases

Revision ID: 0003_max_rounds
Revises: 0002_specialist
Create Date: 2025-01-03 00:00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_max_rounds"
down_revision: str | None = "0002_specialist"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("cases", sa.Column("max_rounds", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("cases", "max_rounds")
