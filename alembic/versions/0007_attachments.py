"""0007 attachments for vision turns.

Images ride with a turn. Only vision models consume them; other
models get 422 model_no_vision. Revises 0006 (non-vector branch).

Revision ID: 0007
Revises: 0006
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None

MAX_BYTES = 5 * 1024 * 1024


def upgrade() -> None:
    op.create_table(
        "attachments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "thread_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("threads.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("mime", sa.String(127), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("data", postgresql.BYTEA(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_attachments_thread_created",
        "attachments",
        ["thread_id", "created_at", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_attachments_thread_created", table_name="attachments")
    op.drop_table("attachments")
