from unittest.mock import AsyncMock, patch

import pytest

from src.agent.agent import Agent
from src.agent.schemas import StoppedReason
from src.rag.schemas import Chunk, SearchResult
from src.tools.rag_search import RagSearchTool
from src.tools.registry import ToolRegistry


@pytest.fixture
def registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(RagSearchTool())
    return registry


def _make_llm(responses: list[str]) -> AsyncMock:
    """Create a mock LLM that returns predetermined responses sequentially."""
    mock = AsyncMock()
    mock.complete = AsyncMock(side_effect=responses)
    return mock


@pytest.mark.asyncio
async def test_agent_returns_final_answer_immediately(registry: ToolRegistry) -> None:
    """If the LLM returns Final Answer in iteration 1, agent stops immediately."""
    llm = _make_llm([
        "Thought: I know this directly.\nFinal Answer: The answer is 42.",
    ])

    agent = Agent(llm=llm, tools=registry)
    result = await agent.run("What is the meaning of life?")

    assert result.answer == "The answer is 42."
    assert result.iterations_used == 1
    assert result.stopped_reason == StoppedReason.FINAL_ANSWER
    assert len(result.steps) == 0


@pytest.mark.asyncio
async def test_agent_uses_tool_then_finishes(registry: ToolRegistry) -> None:
    """Agent searches documents, gets an observation, then gives a final answer."""
    llm = _make_llm([
        (
            "Thought: I need to search the study notes.\n"
            "Action: rag_search\n"
            'Action Input: {"query": "study duration", "top_k": 1}'
        ),
        "Thought: Got the result.\nFinal Answer: The study lasted 12 weeks.",
    ])
    search_result = SearchResult(
        chunk=Chunk(text="The study lasted 12 weeks.", index=0, source="notes.txt"),
        score=0.85,
    )

    agent = Agent(llm=llm, tools=registry)
    with patch("src.tools.rag_search.retrieve", return_value=[search_result]) as retrieve:
        result = await agent.run("How long did the study in my notes last?")

    retrieve.assert_called_once_with("study duration", top_k=1)
    assert result.answer == "The study lasted 12 weeks."
    assert result.iterations_used == 2
    assert result.stopped_reason == StoppedReason.FINAL_ANSWER
    assert len(result.steps) == 1
    assert result.steps[0].action == "rag_search"
    assert result.steps[0].observation == (
        "[1] Source: notes.txt (relevance: 0.85)\nThe study lasted 12 weeks."
    )


@pytest.mark.asyncio
async def test_agent_handles_unknown_tool(registry: ToolRegistry) -> None:
    """Agent receives observation about missing tool, then can recover."""
    llm = _make_llm([
        'Thought: Trying.\nAction: nonexistent_tool\nAction Input: {"x": 1}',
        "Thought: That didn't work, let me answer directly.\nFinal Answer: Done.",
    ])

    agent = Agent(llm=llm, tools=registry)
    result = await agent.run("test")

    assert result.stopped_reason == StoppedReason.FINAL_ANSWER
    assert "not found" in result.steps[0].observation


@pytest.mark.asyncio
async def test_agent_stops_at_max_iterations(registry: ToolRegistry) -> None:
    """Agent stops if no final answer within max_iterations."""
    llm = _make_llm([
        'Thought: trying\nAction: rag_search\nAction Input: {"query": "test query"}'
    ] * 10)

    agent = Agent(llm=llm, tools=registry, max_iterations=3)
    with patch("src.tools.rag_search.retrieve", return_value=[]):
        result = await agent.run("loop forever")

    assert result.stopped_reason == StoppedReason.MAX_ITERATIONS
    assert result.iterations_used == 3
    assert len(result.steps) == 3


@pytest.mark.asyncio
async def test_agent_handles_parse_error(registry: ToolRegistry) -> None:
    """If LLM violates format, agent gets observation and tries again."""
    llm = _make_llm([
        "I'm just going to write nonsense without proper format.",
        "Thought: Let me try again.\nFinal Answer: Got it.",
    ])

    agent = Agent(llm=llm, tools=registry)
    result = await agent.run("test")

    assert result.stopped_reason == StoppedReason.FINAL_ANSWER
    assert "Error" in result.steps[0].observation
