import ast
import operator

from pydantic import BaseModel, Field

from src.tools.base import Tool, ToolError


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class CalculatorInput(BaseModel):
    expression: str = Field(
        ...,
        description="Arithmetic expression, e.g. '2 + 3 * 4' or '(10 - 2) / 4'",
    )


class CalculatorTool(Tool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return (
            "Performs arithmetic calculations. "
            "Use for computing numerical results. "
            "Supported: +, -, *, /, %, **, parentheses, negative numbers."
        )

    @property
    def input_schema(self) -> type[BaseModel]:
        return CalculatorInput

    def execute(self, input_data: BaseModel) -> str:
        if not isinstance(input_data, CalculatorInput):
            raise ToolError(f"Expected CalculatorInput, got {type(input_data).__name__}")

        try:
            result = self._safe_eval(input_data.expression)
            return str(result)
        except (ValueError, ZeroDivisionError, SyntaxError) as e:
            raise ToolError(f"Calculation failed: {e}") from e

    def _safe_eval(self, expression: str) -> float:
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as e:
            raise SyntaxError(f"Invalid expression: {expression}") from e

        return self._eval_node(tree.body)

    def _eval_node(self, node: ast.AST) -> float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in _ALLOWED_OPERATORS:
                raise ValueError(f"Operator not allowed: {op_type.__name__}")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return _ALLOWED_OPERATORS[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in _ALLOWED_OPERATORS:
                raise ValueError(f"Unary operator not allowed: {op_type.__name__}")
            operand = self._eval_node(node.operand)
            return _ALLOWED_OPERATORS[op_type](operand)

        raise ValueError(f"Unsupported expression node: {type(node).__name__}")