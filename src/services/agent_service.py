from functools import lru_cache

from src.agent.agent import Agent
from src.llm.client import get_llm_provider
from src.tools.calculator import CalculatorTool
from src.tools.rag_search import RagSearchTool
from src.tools.registry import ToolRegistry


@lru_cache(maxsize=1)
def get_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(RagSearchTool())
    return registry


@lru_cache(maxsize=1)
def get_agent() -> Agent:
    return Agent(
        llm=get_llm_provider(),
        tools=get_tool_registry(),
    )