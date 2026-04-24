from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StepType(StrEnum):
    THOUGHT_ACTION = "thought_action"
    FINAL_ANSWER = "final_answer"
    PARSE_ERROR = "parse_error"


class ParsedResponse(BaseModel):
    """Result of parsing a single LLM response in the ReAct loop."""
    model_config = ConfigDict(frozen=True)

    step_type: StepType
    thought: str = ""
    action: str = ""
    action_input: dict[str, Any] = Field(default_factory=dict)
    final_answer: str = ""
    error: str = ""


class AgentStep(BaseModel):
    """One iteration of the ReAct loop, after tool execution."""
    model_config = ConfigDict(frozen=True)

    iteration: int = Field(..., ge=1)
    thought: str
    action: str
    action_input: dict[str, Any]
    observation: str


class StoppedReason(StrEnum):
    FINAL_ANSWER = "final_answer"
    MAX_ITERATIONS = "max_iterations"
    TIMEOUT = "timeout"


class AgentResult(BaseModel):
    """Final result of running the agent."""
    model_config = ConfigDict(frozen=True)

    answer: str
    steps: list[AgentStep] = Field(default_factory=list)
    iterations_used: int = Field(..., ge=0)
    stopped_reason: StoppedReason