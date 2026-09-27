"""LLM client for opencode endpoints (OpenAI-compatible).

Base URL precedence: META_API_URL, then OPENCODE_GO_BASE_URL, then
OPENAI_BASE_URL. Caller auth is always the opencode key in
OPENAI_API_KEY. Reads settings only. No keys hardcoded, no keys
logged. Raises builtin TimeoutError on timeouts so the service maps
them to 504, and RuntimeError on other failures so the service maps
them to 502.
"""

from __future__ import annotations

from app.core.config import get_settings


def is_configured() -> bool:
    settings = get_settings()
    return bool(settings.openai_api_key)


APP_USER_AGENT = "langgraph-ai-chatbot/0.1"


def chat_text(
    model: str,
    messages: list[dict],
    timeout_s: float = 20.0,
    max_tokens: int = 512,
    session_id: str | None = None,
) -> str:
    from openai import APIConnectionError, APITimeoutError, OpenAI

    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    if not model:
        raise RuntimeError("model name is not set")
    headers = {"User-Agent": APP_USER_AGENT}
    if session_id:
        headers["x-opencode-session"] = session_id
    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=(
            settings.meta_api_url
            or settings.opencode_go_base_url
            or settings.openai_base_url
        ),
        timeout=timeout_s,
        default_headers=headers,
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
        )
    except APITimeoutError as exc:
        raise TimeoutError(f"model timeout: {exc}") from exc
    except APIConnectionError as exc:
        raise TimeoutError(f"model connection failed: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"model call failed: {type(exc).__name__}") from exc
    content = response.choices[0].message.content or ""
    return content.strip()


def responses_text(
    model: str,
    input_text: str,
    timeout_s: float = 30.0,
    session_id: str | None = None,
    images: list[str] | None = None,
) -> str:
    """Call the Go Responses API. Used by models without chat support."""
    import httpx

    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    if not model:
        raise RuntimeError("model name is not set")
    base = (
        settings.meta_api_url
        or settings.opencode_go_base_url
        or settings.openai_base_url
    ).rstrip("/")
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
        "User-Agent": APP_USER_AGENT,
    }
    if session_id:
        headers["x-opencode-session"] = session_id
    content: object = input_text
    if images:
        parts: list[dict] = [
            {"type": "input_text", "text": input_text}
        ]
        parts.extend(
            {"type": "input_image", "image_url": url} for url in images[:5]
        )
        content = [{"role": "user", "content": parts}]
    try:
        with httpx.Client(timeout=timeout_s) as client:
            response = client.post(
                f"{base}/responses",
                headers=headers,
                json={"model": model, "input": content},
            )
            response.raise_for_status()
            data = response.json()
    except httpx.TimeoutException as exc:
        raise TimeoutError(f"model timeout: {exc}") from exc
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"model call failed: HTTP {exc.response.status_code}"
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"model call failed: {type(exc).__name__}") from exc
    parts: list[str] = []
    for item in data.get("output") or []:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for block in item.get("content") or []:
            if isinstance(block, dict) and isinstance(
                block.get("text"), str
            ):
                parts.append(block["text"])
    return "\n".join(parts).strip()
