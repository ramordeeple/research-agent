import logging

from src.llm.client import complete
from src.llm.schemas import Message

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful research assistant."
    "Answer user questions clearly and concisely with polite charm"
)

async def process_chat(user_message: str) -> str:
    logger.info("Processing chat message: %d chars", len(user_message))

    messages = [
        Message.system(SYSTEM_PROMPT),
        Message.user(user_message)
    ]

    answer = await complete(messages)

    logger.info("Chat response generated: %d chars", len(answer))

    return answer