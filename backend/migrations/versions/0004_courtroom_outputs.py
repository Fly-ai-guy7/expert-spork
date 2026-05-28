"""add courtroom agent outputs to cases

Revision ID: 0004_courtroom
Revises: 0003_max_rounds
Create Date: 2025-01-04 00:00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_courtroom"
down_revision: str | None = "0003_max_rounds"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for col in ("docket", "expert_testimony", "mediation_proposal", "cassation_review"):
        op.add_column("cases", sa.Column(col, postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    for col in ("cassation_review", "mediation_proposal", "expert_testimony", "docket"):
        op.drop_column("cases", col)
