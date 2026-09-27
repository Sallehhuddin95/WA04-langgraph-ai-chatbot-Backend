"""0004 checkpoint tables via langgraph-checkpoint-postgres.

Tables (lib owned, ckpt_ prefix in code refs): checkpoints,
checkpoint_writes, checkpoint_blobs. No FK to threads.id so lib
upgrades stay safe; service joins on thread_id text.

This migration is a placeholder. Full DDL runs through the lib
setup call once graph wiring lands in the next task.

Revision ID: 0004
Revises: 0003
"""

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # TODO(next): invoke PostgresSaver setup DDL here.
    # Kept as no-op so the scaffold migrates offline without a live DB.
    pass


def downgrade() -> None:
    pass
