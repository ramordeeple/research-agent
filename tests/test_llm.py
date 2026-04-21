import pytest

from src.llm.client import complete
from src.llm.schemas import Message

@pytest.mark.asyncio
async def test_llm_response():
    messages = [Message.user("Reply with exactly one word: 'OK'")]
    answer = await complete(messages, temperature=0.0, max_tokens=10)

    assert answer
    assert len(answer) > 0