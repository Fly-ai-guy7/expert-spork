"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2025-01-01 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "statutes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("law_number", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("short_code", sa.String(32), nullable=False, unique=True),
        sa.Column("title_ar", sa.Text(), nullable=True),
        sa.Column("title_en", sa.Text(), nullable=True),
        sa.Column("domain_tags", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("law_number", "year", name="uq_statute_law_year"),
    )

    op.create_table(
        "statute_articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("statute_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("statutes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("article_number", sa.String(32), nullable=False),
        sa.Column("text_ar", sa.Text(), nullable=True),
        sa.Column("text_en", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("statute_id", "article_number", name="uq_article_statute_num"),
    )
    op.create_index("ix_articles_statute", "statute_articles", ["statute_id"])

    case_status = postgresql.ENUM(
        "DRAFT", "RUNNING", "PAUSED_HIL", "COMPLETE", "FAILED", name="case_status"
    )
    case_source = postgresql.ENUM("USER_AUTHORED", "AI_GENERATED", name="case_source")
    case_status.create(op.get_bind(), checkfirst=True)
    case_source.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title_ar", sa.Text(), nullable=True),
        sa.Column("title_en", sa.Text(), nullable=True),
        sa.Column("summary_ar", sa.Text(), nullable=True),
        sa.Column("summary_en", sa.Text(), nullable=True),
        sa.Column("jurisdiction", sa.String(64), nullable=False, server_default="EG"),
        sa.Column("status", case_status, nullable=False, server_default="DRAFT"),
        sa.Column("language_primary", sa.String(2), nullable=False, server_default="en"),
        sa.Column("source", case_source, nullable=False, server_default="USER_AUTHORED"),
        sa.Column("difficulty", sa.Integer(), nullable=True),
        sa.Column("area_of_law", sa.String(64), nullable=True),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_cases_status", "cases", ["status"])
    op.create_index("ix_cases_source_difficulty", "cases", ["source", "difficulty"])

    party_role = postgresql.ENUM("PLAINTIFF", "DEFENDANT", "THIRD_PARTY", name="party_role")
    party_kind = postgresql.ENUM("NATURAL", "LEGAL", name="party_kind")
    party_role.create(op.get_bind(), checkfirst=True)
    party_kind.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "parties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", party_role, nullable=False),
        sa.Column("kind", party_kind, nullable=False, server_default="NATURAL"),
        sa.Column("name_ar", sa.Text(), nullable=True),
        sa.Column("name_en", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    evidence_kind = postgresql.ENUM("DOCUMENT", "WITNESS", "PHYSICAL", name="evidence_kind")
    evidence_kind.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", evidence_kind, nullable=False),
        sa.Column("title_ar", sa.Text(), nullable=True),
        sa.Column("title_en", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("missing", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "facts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text_ar", sa.Text(), nullable=True),
        sa.Column("text_en", sa.Text(), nullable=True),
        sa.Column("disputed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source_evidence_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "debate_rounds",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("round_no", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
        sa.Column("team_a_llm", sa.String(64), nullable=True),
        sa.Column("team_b_llm", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    agent_role = postgresql.ENUM("PROSECUTION", "DEFENSE", "JUDICIAL", "TRAINEE", name="agent_role")
    agent_role.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "arguments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("debate_round_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debate_rounds.id", ondelete="CASCADE"), nullable=True),
        sa.Column("agent", agent_role, nullable=False),
        sa.Column("round_no", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("content_ar", sa.Text(), nullable=True),
        sa.Column("content_en", sa.Text(), nullable=True),
        sa.Column("citations", postgresql.JSONB(), nullable=True),
        sa.Column("llm_used", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_arguments_case_round", "arguments", ["case_id", "round_no"])

    op.create_table(
        "scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("argument_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("arguments.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("factual", sa.Float(), nullable=False, server_default="0"),
        sa.Column("provable", sa.Float(), nullable=False, server_default="0"),
        sa.Column("unbiased", sa.Float(), nullable=False, server_default="0"),
        sa.Column("legal_law_based", sa.Float(), nullable=False, server_default="0"),
        sa.Column("overall", sa.Float(), nullable=False, server_default="0"),
        sa.Column("rationale_ar", sa.Text(), nullable=True),
        sa.Column("rationale_en", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "rulings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("plaintiff_success_prob", sa.Float(), nullable=False, server_default="0"),
        sa.Column("critical_evidence_gaps", postgresql.JSONB(), nullable=True),
        sa.Column("precedent_refs", postgresql.JSONB(), nullable=True),
        sa.Column("text_ar", sa.Text(), nullable=True),
        sa.Column("text_en", sa.Text(), nullable=True),
        sa.Column("override_applied", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "outcomes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("projected_prob", sa.Float(), nullable=False, server_default="0"),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("pretrial_resolution_ar", sa.Text(), nullable=True),
        sa.Column("pretrial_resolution_en", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    hil_stage = postgresql.ENUM(
        "POST_EVIDENCE", "POST_PROSECUTION", "PRE_DEFENSE_REBUTTAL", "PRE_RULING", "TRAINEE_TURN",
        name="hil_stage",
    )
    hil_status = postgresql.ENUM(
        "PENDING", "APPROVED", "MODIFIED", "HALTED", "SUBMITTED", name="hil_status"
    )
    hil_stage.create(op.get_bind(), checkfirst=True)
    hil_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "hil_checkpoints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage", hil_stage, nullable=False),
        sa.Column("status", hil_status, nullable=False, server_default="PENDING"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("modified_payload", postgresql.JSONB(), nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_hil_case_status", "hil_checkpoints", ["case_id", "status"])

    trainee_role = postgresql.ENUM("PROSECUTION", "DEFENSE", name="trainee_role")
    trainee_role.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "training_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("trainee_role", trainee_role, nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_score", sa.Float(), nullable=True),
        sa.Column("coaching_report", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_training_user_completed", "training_sessions", ["user_id", "completed_at"])


def downgrade() -> None:
    op.drop_table("training_sessions")
    op.drop_table("hil_checkpoints")
    op.drop_table("outcomes")
    op.drop_table("rulings")
    op.drop_table("scores")
    op.drop_table("arguments")
    op.drop_table("debate_rounds")
    op.drop_table("facts")
    op.drop_table("evidence")
    op.drop_table("parties")
    op.drop_table("cases")
    op.drop_table("statute_articles")
    op.drop_table("statutes")
    for enum_name in [
        "case_status", "case_source", "party_role", "party_kind",
        "evidence_kind", "agent_role", "hil_stage", "hil_status", "trainee_role",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
