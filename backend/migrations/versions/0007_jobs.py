"""jobs table for async pipeline execution

Revision ID: 0007_jobs
Revises: 0006_auth
Create Date: 2025-01-07 00:00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_jobs"
down_revision: str | None = "0006_auth"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.Enum("SIMULATION", "TRAINEE_RESUME", name="job_kind"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("QUEUED", "RUNNING", "PAUSED", "COMPLETE", "FAILED", name="job_status"),
            nullable=False,
        ),
        sa.Column("task_id", sa.String(155), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_jobs_case", "jobs", ["case_id"])


def downgrade() -> None:
    op.drop_index("ix_jobs_case", table_name="jobs")
    op.drop_table("jobs")
