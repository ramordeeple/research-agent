from typing import Final

APP_NAME: Final[str] = "AI Research Agent"
APP_VERSION: Final[str] = "0.1.0"

DEFAULT_CHUNK_SIZE: Final[int] = 500
DEFAULT_CHUNK_OVERLAP: Final[int] = 50
DEFAULT_TOP_K: Final[int] = 5

MAX_AGENT_ITERATIONS: Final[int] = 10
MAX_AGENT_TIMEOUT_SECONDS: Final[int] = 60

DEFAULT_LLM_TEMPERATURE: Final[float] = 0.7
DEFAULT_LLM_MAX_TOKENS: Final[int] = 1024

EMBEDDING_DIM: Final[int] = 384

CHAT_MIN_LENGTH: Final[int] = 1
CHAT_MAX_LENGTH: Final[int] = 2000
