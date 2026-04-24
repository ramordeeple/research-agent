import logging

from src.tools.base import Tool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Stores and provides access to available tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        self._tools[tool.name] = tool
        logger.debug("Registered tool: %s", tool.name)

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")

        return self._tools[name]

    def has(self, name: str) -> bool:
        return name in self._tools

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def describe_all(self) -> str:
        """Format all tools for inclusion in the system prompt."""
        if not self._tools:
            return "No tools available."

        lines = []
        for tool in self._tools.values():
            schema = tool.input_schema.model_json_schema()
            properties = schema.get("properties", {})
            params_desc = ", ".join(
                f'"{name}": {info.get("type", "any")}'
                for name, info in properties.items()
            )
            lines.append(
                f"- {tool.name}: {tool.description}\n"
                f"  Input: {{{params_desc}}}"
            )

        return "\n".join(lines)
