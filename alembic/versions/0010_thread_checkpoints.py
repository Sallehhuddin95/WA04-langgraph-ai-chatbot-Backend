"""0010 thread checkpoints for postgres resume.

Owns thread_checkpoints keyed by thread_id. Keeps last 50 per
thread or 30 days. Pruned by the maintenance job. No FK to
threads.id so checkpoint reads stay safe across deletes.

Revision ID: 0010
Revises: 0009
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "thread_checkpoints",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column("thread_id", UUID(as_uuid=True), nullable=False),
        sa.Column("trace_id", UUID(as_uuid=True), nullable=True),
        sa.Column("intent_category", sa.String(32), nullable=True),
        sa.Column("is_grounded", sa.Boolean(), nullable=True),
        sa.Column(
            "state",
            JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_thread_checkpoints_thread_created",
        "thread_checkpoints",
        ["thread_id", sa.text("created_at DESC"), "id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_thread_checkpoints_thread_created",
        table_name="thread_checkpoints",
    )
    op.drop_table("thread_checkpoints")
