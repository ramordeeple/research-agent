import logging
import re

from src.agent.schemas import AgentStep
from src.schemas.chat import Source
from src.services.agent_service import get_agent

logger = logging.getLogger(__name__)


async def process_chat(user_message: str) -> tuple[str, list[Source]]:
    logger.info("Processing chat message: %d chars", len(user_message))

    agent = get_agent()
    result = await agent.run(user_message)

    sources = _extract_sources(result.steps)

    logger.info(
        "Chat response: %d chars, %d sources, stopped=%s, iterations=%d",
        len(result.answer), len(sources), result.stopped_reason, result.iterations_used,
    )
    return result.answer, sources


def _extract_sources(steps: list[AgentStep]) -> list[Source]:
    """Extract Source objects from rag_search tool observations in agent steps."""
    sources: list[Source] = []
    seen_texts: set[str] = set()

    for step in steps:
        if step.action != "rag_search":
            continue

        for source in _parse_rag_observation(step.observation):
            if source.text not in seen_texts:
                sources.append(source)
                seen_texts.add(source.text)

    return sources


_SOURCE_PATTERN = re.compile(
    r"\[\d+\]\s+Source:\s+(?P<source>.+?)\s+\(relevance:\s+(?P<score>[\d.]+)\)\n(?P<text>.+?)(?=\n\n\[\d+\]|\Z)",
    re.DOTALL,
)


def _parse_rag_observation(observation: str) -> list[Source]:
    """Parse the formatted output of RagSearchTool back into Source objects."""
    if "No relevant documents" in observation:
        return []

    sources: list[Source] = []
    for match in _SOURCE_PATTERN.finditer(observation):
        sources.append(
            Source(
                source=match.group("source").strip(),
                score=float(match.group("score")),
                text=match.group("text").strip(),
            )
        )
        
    return sources