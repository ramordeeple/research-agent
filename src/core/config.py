from enum import StrEnum
from typing import Final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from torch.fx.experimental.symbolic_shapes import lru_cache

class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    log_level: LogLevel = LogLevel.INFO

    llm_api_key: str = Field(..., description="API key for LLM")
    llm_base_url: str = Field("https://generativelanguage.googleapis.com/v1beta/openai/")
    llm_model: str = "gemini-2.0-flash"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "documents"

    embedding_model: str = "BAAI/bge-small-en-v1.5"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
