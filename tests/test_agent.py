from unittest.mock import AsyncMock

import pytest

from src.agent.agent import Agent
from src.agent.schemas import StoppedReason
from src.tools.calculator import CalculatorTool
from src.tools.registry import ToolRegistry


@pytest.fixture
def registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(CalculatorTool())
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
    """Agent calls calculator, gets observation, then gives final answer."""
    llm = _make_llm([
        'Thought: I need to calculate.\nAction: calculator\nAction Input: {"expression": "5 * 7"}',
        "Thought: Got the result.\nFinal Answer: 5 times 7 equals 35.",
    ])

    agent = Agent(llm=llm, tools=registry)
    result = await agent.run("What is 5 times 7?")

    assert "35" in result.answer
    assert result.iterations_used == 2
    assert result.stopped_reason == StoppedReason.FINAL_ANSWER
    assert len(result.steps) == 1
    assert result.steps[0].action == "calculator"
    assert result.steps[0].observation == "35"


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
        'Thought: trying\nAction: calculator\nAction Input: {"expression": "1+1"}'
    ] * 10)

    agent = Agent(llm=llm, tools=registry, max_iterations=3)
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