import logging
from functools import lru_cache

from openai import AsyncOpenAI

from src.core.config import get_settings
from src.core.constants import DEFAULT_LLM_MAX_TOKENS, DEFAULT_LLM_TEMPERATURE
from src.llm.base import LLMProvider
from src.llm.schemas import Message

logger = logging.getLogger(__name__)


class OpenAICompatibleLLM:
    """LLM provider using OpenAI-compatible API (works with Gemini, Grok, etc.)."""

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        logger.info("LLM provider initialized: model=%s", model)

    async def complete(
        self,
        messages: list[Message],
        temperature: float = DEFAULT_LLM_TEMPERATURE,
        max_tokens: int = DEFAULT_LLM_MAX_TOKENS,
    ) -> str:
        logger.debug("LLM request: %d messages", len(messages))

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[m.model_dump() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content or ""
        logger.debug("LLM response: %d chars", len(content))
        return content


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    return OpenAICompatibleLLM(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
    )