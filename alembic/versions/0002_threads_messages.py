"""0002 threads plus messages with FKs and checks.

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "threads",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(120), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_threads_owner_updated",
        "threads",
        ["owner_id", sa.text("updated_at DESC")],
    )

    op.create_table(
        "messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("thread_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("intent_category", sa.String(32), nullable=True),
        sa.Column("is_grounded", sa.Boolean(), nullable=True),
        sa.Column("trace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["thread_id"], ["threads.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "role IN ('user', 'assistant', 'system')", name="ck_messages_role"
        ),
        sa.CheckConstraint(
            "intent_category IS NULL OR intent_category IN "
            "('simple_chat', 'rag_search', 'complex_task')",
            name="ck_messages_intent_category",
        ),
    )
    op.create_index(
        "ix_messages_thread_created",
        "messages",
        ["thread_id", "created_at", "id"],
    )
    op.create_index("ix_messages_trace", "messages", ["trace_id"])
    op.create_index(
        "uq_messages_thread_idem",
        "messages",
        ["thread_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_messages_thread_idem", table_name="messages")
    op.drop_index("ix_messages_trace", table_name="messages")
    op.drop_index("ix_messages_thread_created", table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_threads_owner_updated", table_name="threads")
    op.drop_table("threads")
