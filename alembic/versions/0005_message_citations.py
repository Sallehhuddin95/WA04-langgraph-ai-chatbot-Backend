"""0005 messages.citations JSONB for streamed citation replay.

Assistant rows store [{chunk_id, document_id, quote}] so the SSE
stream endpoint can replay citation events on a later fetch.

Revises 0002 on purpose: this branch migrates on hosts without
pgvector. Hosts with pgvector upgrade to heads (0004 plus 0005).
Non-vector hosts upgrade to 0005.

Revision ID: 0005
Revises: 0002
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "messages",
        sa.Column(
            "citations",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("messages", "citations")
