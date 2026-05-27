"""add specialist agent outputs to cases

Revision ID: 0002_specialist
Revises: 0001_initial
Create Date: 2025-01-02 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_specialist"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("cases", sa.Column("procedural_analysis", postgresql.JSONB(), nullable=True))
    op.add_column("cases", sa.Column("precedent_analysis", postgresql.JSONB(), nullable=True))
    op.add_column("cases", sa.Column("damages_estimate", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("cases", "damages_estimate")
    op.drop_column("cases", "precedent_analysis")
    op.drop_column("cases", "procedural_analysis")
