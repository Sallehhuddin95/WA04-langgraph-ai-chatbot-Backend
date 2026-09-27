"""Per-turn model registry. Dropdown ids map to provider models.

Only deepseek-v4-flash-vision-exp consumes images. Muse runs on
the Go Responses API, the DeepSeek pair on chat completions.
"""

from __future__ import annotations

DEFAULT_MODEL = "deepseek-v4-flash"

MODELS: dict[str, dict] = {
    "deepseek-v4-flash": {
        "label": "DeepSeek V4 Flash",
        "provider_model": "deepseek-v4-flash",
        "api": "chat",
        "vision": False,
    },
    "deepseek-v4-flash-vision-exp": {
        "label": "DeepSeek V4 Flash Vision",
        "provider_model": "deepseek-v4-flash-vision-exp",
        "api": "chat",
        "vision": True,
    },
    "muse-spark-1.3": {
        "label": "Muse Spark 1.3",
        "provider_model": "muse-spark-1.3-contributor",
        "api": "responses",
        "vision": True,
    },
}


def is_known_model(model: str) -> bool:
    return model in MODELS


def supports_vision(model: str) -> bool:
    entry = MODELS.get(model)
    return bool(entry and entry["vision"])


def provider_model(model: str) -> str:
    entry = MODELS.get(model)
    if entry is None:
        raise ValueError(f"unknown model: {model}")
    return str(entry["provider_model"])


def model_api(model: str) -> str:
    entry = MODELS.get(model)
    if entry is None:
        raise ValueError(f"unknown model: {model}")
    return str(entry["api"])
