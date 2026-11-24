import pytest

from src.services.agent_service import get_tool_registry
from src.tools.rag_search import RagSearchTool
from src.tools.registry import ToolRegistry


def test_register_and_get() -> None:
    registry = ToolRegistry()
    tool = RagSearchTool()

    registry.register(tool)

    assert registry.get("rag_search") is tool
    assert registry.has("rag_search")


def test_get_nonexistent_raises() -> None:
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="not found"):
        registry.get("nonexistent")


def test_register_duplicate_raises() -> None:
    registry = ToolRegistry()
    registry.register(RagSearchTool())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(RagSearchTool())


def test_default_registry_describes_document_search() -> None:
    registry = get_tool_registry()

    description = registry.describe_all()

    assert [tool.name for tool in registry.list_tools()] == ["rag_search"]
    assert "rag_search" in description
    assert '"query": string' in description


def test_describe_all_empty() -> None:
    registry = ToolRegistry()
    assert "No tools" in registry.describe_all()
