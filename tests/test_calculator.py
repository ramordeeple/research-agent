import pytest

from src.tools.base import ToolError
from src.tools.calculator import CalculatorInput, CalculatorTool


@pytest.fixture
def calc() -> CalculatorTool:
    return CalculatorTool()


def test_simple_addition(calc: CalculatorTool) -> None:
    result = calc.execute(CalculatorInput(expression="2 + 3"))
    assert result == "5"


def test_complex_expression(calc: CalculatorTool) -> None:
    result = calc.execute(CalculatorInput(expression="(1 + 2) * 3 - 4"))
    assert result == "5"


def test_unsafe_expression_raises(calc: CalculatorTool) -> None:
    """Calculator must reject non-arithmetic expressions for security."""
    with pytest.raises(ToolError):
        calc.execute(CalculatorInput(expression="__import__('os')"))


def test_name_and_description(calc: CalculatorTool) -> None:
    assert calc.name == "calculator"
    assert "arithmetic" in calc.description.lower()