import pytest

from src.tools.calculator import CalculatorTool
from src.tools.registry import ToolRegistry


def test_register_and_get() -> None:
    registry = ToolRegistry()
    tool = CalculatorTool()

    registry.register(tool)

    assert registry.get("calculator") is tool
    assert registry.has("calculator")


def test_get_nonexistent_raises() -> None:
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="not found"):
        registry.get("nonexistent")


def test_register_duplicate_raises() -> None:
    registry = ToolRegistry()
    registry.register(CalculatorTool())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(CalculatorTool())


def test_describe_all_includes_tool_info() -> None:
    registry = ToolRegistry()
    registry.register(CalculatorTool())

    description = registry.describe_all()

    assert "calculator" in description
    assert "expression" in description


def test_describe_all_empty() -> None:
    registry = ToolRegistry()
    assert "No tools" in registry.describe_all()