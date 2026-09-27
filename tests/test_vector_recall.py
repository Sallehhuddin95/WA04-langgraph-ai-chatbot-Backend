"""Vector recall wiring. Prefetch wins, stub stays as fallback."""

from __future__ import annotations

from app.services.embeddings import embed_query, is_embedding_configured
from app.services.graph.retriever import retrieve_docs


def test_no_key_means_no_embedding() -> None:
    # conftest strips OPENAI_API_KEY, so the mock path stays hermetic.
    assert is_embedding_configured() is False
    assert embed_query("refund policy") is None


def test_prefetched_docs_win_over_stub() -> None:
    state = {
        "messages": [{"role": "user", "text": "refund policy"}],
        "intent_category": "rag_search",
        "prefetched_docs": [
            {
                "chunk_id": "c1",
                "document_id": "d1",
                "score": 1.0,
                "text": "vector doc",
            }
        ],
    }
    out = retrieve_docs(state)  # type: ignore[arg-type]
    assert out["retrieved_docs"] == state["prefetched_docs"]


def test_stub_fallback_without_prefetch() -> None:
    state = {
        "messages": [{"role": "user", "text": "what is the refund policy?"}],
        "intent_category": "rag_search",
    }
    out = retrieve_docs(state)  # type: ignore[arg-type]
    assert len(out["retrieved_docs"]) >= 1


def test_simple_chat_skips_prefetch() -> None:
    state = {
        "messages": [{"role": "user", "text": "hi"}],
        "intent_category": "simple_chat",
        "prefetched_docs": [
            {
                "chunk_id": "c1",
                "document_id": "d1",
                "score": 1.0,
                "text": "vector doc",
            }
        ],
    }
    out = retrieve_docs(state)  # type: ignore[arg-type]
    assert out["retrieved_docs"] == []
