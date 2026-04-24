from typing import Protocol

from src.core.constants import DEFAULT_LLM_MAX_TOKENS, DEFAULT_LLM_TEMPERATURE
from src.llm.schemas import Message


class LLMProvider(Protocol):
    """Protocol for any LLM provider. Implementations wrap concrete SDKs."""

    async def complete(
        self,
        messages: list[Message],
        temperature: float = DEFAULT_LLM_TEMPERATURE,
        max_tokens: int = DEFAULT_LLM_MAX_TOKENS,
    ) -> str: ...