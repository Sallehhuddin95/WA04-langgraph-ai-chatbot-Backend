"""Scaffold import test. Checks layer wiring without a live DB."""

from app.core.config import get_settings
from app.main import app
from app.repositories.checkpoint_adapter import CheckpointAdapter
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.document_repository import DocumentRepository
from app.routes.chat import router
from app.schemas.chat import (
    CitationResponse,
    CreateThreadRequest,
    CreateTurnRequest,
    CreateTurnResponse,
)
from app.services.graph import state


def test_scaffold_imports() -> None:
    assert app.title == "LangGraph AI Chatbot Backend"
    assert any(r.path == "/api/chat/health" for r in router.routes)
    assert state.ChatState.__annotations__["intent_category"]
    assert get_settings().embedding_model == "text-embedding-3-small"
    for cls in (
        ConversationRepository,
        DocumentRepository,
        CheckpointAdapter,
    ):
        assert cls.__name__
    for cls in (
        CreateThreadRequest,
        CreateTurnRequest,
        CreateTurnResponse,
        CitationResponse,
    ):
        assert cls.__name__
