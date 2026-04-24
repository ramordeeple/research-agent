import pytest

from src.llm.client import get_llm_provider
from src.llm.schemas import Message


@pytest.mark.integration
@pytest.mark.asyncio
async def test_llm_provider_responds() -> None:
    llm = get_llm_provider()
    messages = [Message.user("Reply with exactly one word: 'OK'")]

    answer = await llm.complete(messages, temperature=0.0, max_tokens=10)

    assert answer
    assert len(answer) > 0