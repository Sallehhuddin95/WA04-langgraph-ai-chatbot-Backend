"""Query embeddings. Pluggable provider with safe fallback.

Opencode inference lists no embeddings endpoint today, so this module
tries the configured OpenAI-compatible base and returns None when
embeddings are unavailable. Callers must fall back to keyword recall
instead of failing the turn.
"""

from __future__ import annotations

from app.core.config import get_settings

EMBEDDING_DIM = 1536


def is_embedding_configured() -> bool:
    settings = get_settings()
    return bool(settings.openai_api_key and settings.embedding_model)


def embed_query(text: str) -> list[float] | None:
    """Embed one query. Returns None when unavailable or invalid."""
    cleaned = (text or "").strip()
    if not cleaned:
        return None
    settings = get_settings()
    if not settings.openai_api_key or not settings.embedding_model:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=(
                settings.meta_api_url
                or settings.opencode_go_base_url
                or settings.openai_base_url
            ),
            timeout=10.0,
        )
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=cleaned,
        )
        vector = list(response.data[0].embedding or [])
    except Exception:
        return None
    if len(vector) != EMBEDDING_DIM:
        return None
    if not all(isinstance(value, (int, float)) for value in vector):
        return None
    return [float(value) for value in vector]
