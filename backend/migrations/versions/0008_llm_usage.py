"""llm_usage table for cost governance

Revision ID: 0008_llm_usage
Revises: 0007_jobs
Create Date: 2025-01-08 00:00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008_llm_usage"
down_revision: str | None = "0007_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "llm_usage",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("org_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="SET NULL"), nullable=True),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("model", sa.String(128), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cached_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_llm_usage_org_created", "llm_usage", ["org_id", "created_at"])
    op.create_index("ix_llm_usage_case", "llm_usage", ["case_id"])


def downgrade() -> None:
    op.drop_index("ix_llm_usage_case", table_name="llm_usage")
    op.drop_index("ix_llm_usage_org_created", table_name="llm_usage")
    op.drop_table("llm_usage")
