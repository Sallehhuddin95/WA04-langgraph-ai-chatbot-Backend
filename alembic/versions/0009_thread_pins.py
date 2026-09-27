"""0009 thread pin columns.

Pinned threads sort first by pin_order. At most 5 pinned per
owner, enforced in the service. Revises 0008 (non-vector branch).

Revision ID: 0009
Revises: 0008
"""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None

MAX_PINS = 5


def upgrade() -> None:
    op.add_column(
        "threads",
        sa.Column(
            "is_pinned",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "threads", sa.Column("pin_order", sa.Integer(), nullable=True)
    )
    op.create_index(
        "ix_threads_owner_pinned",
        "threads",
        ["owner_id", "is_pinned", "pin_order"],
    )


def downgrade() -> None:
    op.drop_index("ix_threads_owner_pinned", table_name="threads")
    op.drop_column("threads", "pin_order")
    op.drop_column("threads", "is_pinned")
