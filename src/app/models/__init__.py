"""ORM model registry. Import all models so metadata stays complete."""

from app.models.attachments import Attachment
from app.models.base import Base
from app.models.document_chunks import DocumentChunk
from app.models.messages import Message
from app.models.sessions import UserSession
from app.models.thread_checkpoints import ThreadCheckpoint
from app.models.threads import Thread
from app.models.users import User

__all__ = [
    "Attachment",
    "Base",
    "DocumentChunk",
    "Message",
    "Thread",
    "ThreadCheckpoint",
    "User",
    "UserSession",
]
