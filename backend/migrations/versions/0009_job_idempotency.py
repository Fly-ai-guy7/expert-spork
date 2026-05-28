"""add idempotency_key to jobs

Revision ID: 0009_job_idem
Revises: 0008_llm_usage
Create Date: 2025-01-09 00:00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_job_idem"
down_revision: str | None = "0008_llm_usage"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("idempotency_key", sa.String(255), nullable=True))
    op.create_index("ix_jobs_case_idem", "jobs", ["case_id", "idempotency_key"])


def downgrade() -> None:
    op.drop_index("ix_jobs_case_idem", table_name="jobs")
    op.drop_column("jobs", "idempotency_key")
