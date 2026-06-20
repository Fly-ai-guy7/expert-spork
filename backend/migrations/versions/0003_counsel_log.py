"""advisory counsel call log

Revision ID: 0003_counsel_log
Revises: 0002_judicial_council
Create Date: 2026-06-20 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_counsel_log"
down_revision: Union[str, None] = "0002_judicial_council"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "counsel_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("training_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("training_sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("checkpoint_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("hil_checkpoints.id", ondelete="SET NULL"), nullable=True),
        sa.Column("trainee_role", sa.String(32), nullable=False),
        sa.Column("draft_ar", sa.Text(), nullable=True),
        sa.Column("draft_en", sa.Text(), nullable=True),
        sa.Column("citations", postgresql.JSONB(), nullable=True),
        sa.Column("advice", postgresql.JSONB(), nullable=False),
        sa.Column("llm_used", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_counsel_logs_session", "counsel_logs", ["training_session_id"])
    op.create_index("ix_counsel_logs_case", "counsel_logs", ["case_id"])


def downgrade() -> None:
    op.drop_index("ix_counsel_logs_case", table_name="counsel_logs")
    op.drop_index("ix_counsel_logs_session", table_name="counsel_logs")
    op.drop_table("counsel_logs")
