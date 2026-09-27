"""App config. Reads env only. No keys hardcoded."""

import os
from dataclasses import dataclass
from functools import lru_cache


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    database_url: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://opencode.ai/inference/openai/v1"
    meta_api_url: str = ""
    opencode_go_base_url: str = ""
    model_router: str = ""
    model_generator: str = ""
    embedding_model: str = "text-embedding-3-small"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=_env("DATABASE_URL"),
            openai_api_key=_env("OPENAI_API_KEY"),
            openai_base_url=_env(
                "OPENAI_BASE_URL", "https://opencode.ai/inference/openai/v1"
            ),
            meta_api_url=_env("META_API_URL"),
            opencode_go_base_url=_env("OPENCODE_GO_BASE_URL"),
            model_router=_env("MODEL_ROUTER"),
            model_generator=_env("MODEL_GENERATOR"),
            embedding_model=_env(
                "EMBEDDING_MODEL", "text-embedding-3-small"
            ),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
