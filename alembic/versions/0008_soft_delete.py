"""0008 soft delete for threads plus messages.

Delete sets deleted_at. Restore clears it within 10 seconds.
A future purge job removes old soft-deleted rows. Revises 0007
(non-vector branch).

Revision ID: 0008
Revises: 0007
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "threads",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "messages",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_threads_owner_deleted_updated",
        "threads",
        ["owner_id", "deleted_at", "updated_at"],
    )
    op.create_index(
        "ix_messages_thread_deleted_created",
        "messages",
        ["thread_id", "deleted_at", "created_at", "id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_messages_thread_deleted_created", table_name="messages"
    )
    op.drop_index(
        "ix_threads_owner_deleted_updated", table_name="threads"
    )
    op.drop_column("messages", "deleted_at")
    op.drop_column("threads", "deleted_at")
