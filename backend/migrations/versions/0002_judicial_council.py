"""judicial council: panel verdicts + ruling consensus columns

Revision ID: 0002_judicial_council
Revises: 0001_initial
Create Date: 2026-05-28 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_judicial_council"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rulings",
        sa.Column("council_size", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column("rulings", sa.Column("council_vote", postgresql.JSONB(), nullable=True))
    op.add_column("rulings", sa.Column("dissent_ar", sa.Text(), nullable=True))
    op.add_column("rulings", sa.Column("dissent_en", sa.Text(), nullable=True))

    op.create_table(
        "council_verdicts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ruling_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rulings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("member_llm", sa.String(64), nullable=False),
        sa.Column("llm_used", sa.String(64), nullable=True),
        sa.Column("plaintiff_success_prob", sa.Float(), nullable=False, server_default="0"),
        sa.Column("verdict", sa.String(32), nullable=False),
        sa.Column("override_flagged", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("reasoning_ar", sa.Text(), nullable=True),
        sa.Column("reasoning_en", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_council_verdicts_ruling", "council_verdicts", ["ruling_id"])


def downgrade() -> None:
    op.drop_index("ix_council_verdicts_ruling", table_name="council_verdicts")
    op.drop_table("council_verdicts")
    op.drop_column("rulings", "dissent_en")
    op.drop_column("rulings", "dissent_ar")
    op.drop_column("rulings", "council_vote")
    op.drop_column("rulings", "council_size")
