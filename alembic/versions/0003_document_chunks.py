"""0003 vector extension plus document_chunks with vector(1536) HNSW index.

Embedding model: text-embedding-3-small, dim 1536, distance op <=>.
Owns CREATE EXTENSION vector so 0001 and 0002 migrate on hosts
without pgvector. Upgrade to this revision needs the extension.

Revision ID: 0003
Revises: 0002
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from pgvector.sqlalchemy import Vector

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
    op.create_table(
        "document_chunks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column(
            "meta",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "document_id", "chunk_index", name="uq_document_chunks_doc_chunk"
        ),
    )
    op.create_index(
        "ix_document_chunks_doc_chunk",
        "document_chunks",
        ["document_id", "chunk_index"],
    )
    op.create_index(
        "ix_document_chunks_embedding_hnsw",
        "document_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index(
        "ix_document_chunks_embedding_hnsw", table_name="document_chunks"
    )
    op.drop_index("ix_document_chunks_doc_chunk", table_name="document_chunks")
    op.drop_table("document_chunks")
