import logging

from src.llm.client import get_llm_provider
from src.llm.schemas import Message
from src.rag.retriever import retrieve
from src.schemas.chat import Source

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful research assistant.

Use the following context from documents to answer the user's question.
If the context doesn't contain the answer, say so honestly — don't make things up.
Cite the source filename when you use information from it.

Context:
{context}"""


async def process_chat(user_message: str) -> tuple[str, list[Source]]:
    logger.info("Processing chat message: %d chars", len(user_message))

    search_results = retrieve(user_message)

    context = _build_context(search_results)
    messages = [
        Message.system(SYSTEM_PROMPT.format(context=context)),
        Message.user(user_message),
    ]

    llm = get_llm_provider()
    answer = await llm.complete(messages)

    sources = [
        Source(text=r.chunk.text, source=r.chunk.source, score=r.score)
        for r in search_results
    ]

    logger.info("Chat response: %d chars, %d sources", len(answer), len(sources))
    return answer, sources


def _build_context(search_results) -> str:
    if not search_results:
        return "(no relevant documents found)"

    parts = []
    for i, result in enumerate(search_results, 1):
        parts.append(f"[{i}] From {result.chunk.source}:\n{result.chunk.text}")

    return "\n\n".join(parts)