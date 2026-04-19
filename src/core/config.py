from typing import Final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from torch.fx.experimental.symbolic_shapes import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    log_level: Final[str] = "INFO"

    llm_api_key: Final[str] = Field(..., description="API key for LLM")
    llm_base_url: Final[str] = Field("https://generativelanguage.googleapis.com/v1beta/openai/")
    llm_model: Final[str] = "gemini-2.0-flash"

    qdrant_url: Final[str] = "http://localhost:6333"
    qdrant_collection: Final[str] = "documents"

    embedding_model: Final[str] = "BAAI/bge-small-en-v1.5"

@lru_cache
def get_settings() -> Settings:
    return Settings()
