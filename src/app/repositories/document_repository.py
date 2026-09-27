"""Document repository. Owns vector recall over document_chunks."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_chunks import DocumentChunk


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def search_chunks(self, query_vector: list[float], limit: int = 5):
        stmt = (
            select(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())
