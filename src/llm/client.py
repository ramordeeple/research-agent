import logging
from functools import lru_cache

from openai import AsyncOpenAI

from src.core.config import get_settings
from src.core.constants import DEFAULT_LLM_TEMPERATURE, DEFAULT_LLM_MAX_TOKENS
from src.llm.schemas import Message

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_llm_client() -> AsyncOpenAI:
    settings = get_settings()
    logger.info("Initializing LLM client: model = %s", settings.llm_model)

    return AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url
    )

async def complete(
        messages: list[Message],
        temperature = DEFAULT_LLM_TEMPERATURE,
        max_tokens = DEFAULT_LLM_MAX_TOKENS
) -> str:
    settings = get_settings()
    client = get_llm_client()

    logger.debug("LLM request: %d messages", len(messages))

    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[m.model_dump() for m in messages],
        temperature=temperature,
        max_tokens=max_tokens
    )

    content = response.choices[0].message.content or ""

    logger.debug("LLM response: %d chars", len(content))

    return content