"""case cancellation: cases.cancel_requested + CANCELLED status

Revision ID: 0011_case_cancel
Revises: 0010_audit
Create Date: 2025-01-11 00:00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011_case_cancel"
down_revision: str | None = "0010_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "cases",
        sa.Column("cancel_requested", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    # On Postgres, expand the case_status enum to include CANCELLED.
    # On SQLite the enum is stored as a string with a CHECK constraint that
    # SQLAlchemy enforces at the ORM layer; no DDL needed.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # ALTER TYPE ... ADD VALUE must run outside a transaction.
        with op.get_context().autocommit_block():
            op.execute("ALTER TYPE case_status ADD VALUE IF NOT EXISTS 'CANCELLED'")


def downgrade() -> None:
    op.drop_column("cases", "cancel_requested")
    # Removing an enum value is destructive on Postgres (rewrite the type +
    # rewrite every row); we don't do it automatically. Reversing the enum
    # add is a manual operation if you really need it.
