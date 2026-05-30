"""audit_events: append-only audit trail

Revision ID: 0010_audit
Revises: 0009_job_idem
Create Date: 2025-01-10 00:00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010_audit"
down_revision: str | None = "0009_job_idem"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("org_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_email", sa.String(320), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=True),
        sa.Column("resource_id", sa.String(64), nullable=True),
        sa.Column("before", sa.JSON(), nullable=True),
        sa.Column("after", sa.JSON(), nullable=True),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("request_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_org_created", "audit_events", ["org_id", "created_at"])
    op.create_index("ix_audit_actor", "audit_events", ["actor_user_id"])
    op.create_index("ix_audit_resource", "audit_events", ["resource_type", "resource_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_resource", table_name="audit_events")
    op.drop_index("ix_audit_actor", table_name="audit_events")
    op.drop_index("ix_audit_org_created", table_name="audit_events")
    op.drop_table("audit_events")
