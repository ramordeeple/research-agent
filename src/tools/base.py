from abc import ABC, abstractmethod

from pydantic import BaseModel


class ToolError(Exception):
    """Raised when tool execution fails due to invalid input or runtime error."""


class Tool(ABC):
    """Base class for all agent tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier used by the LLM to invoke the tool."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable explanation for the LLM: what the tool does and when to use it."""

    @property
    @abstractmethod
    def input_schema(self) -> type[BaseModel]:
        """Pydantic model describing expected input parameters."""

    @abstractmethod
    def execute(self, input_data: BaseModel) -> str:
        """Run the tool with validated input and return a string result."""