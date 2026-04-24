import json
import re

from src.agent.schemas import ParsedResponse, StepType

FINAL_ANSWER_PATTERN = re.compile(r"Final Answer:\s*(.*)", re.DOTALL)
THOUGHT_PATTERN = re.compile(
    r"Thought:\s*(.*?)(?=Action:|Final Answer:|$)", re.DOTALL
)
ACTION_PATTERN = re.compile(r"Action:\s*([\w_]+)")
ACTION_INPUT_PATTERN = re.compile(r"Action Input:\s*(\{.*?\})", re.DOTALL)


def parse_llm_response(text: str) -> ParsedResponse:
    """Parse a single LLM response into a structured ParsedResponse."""
    thought = _match_first_group(THOUGHT_PATTERN, text)

    final_answer = _match_first_group(FINAL_ANSWER_PATTERN, text)
    if final_answer:
        return ParsedResponse(
            step_type=StepType.FINAL_ANSWER,
            thought=thought,
            final_answer=final_answer,
        )

    return _parse_tool_call(text, thought)


def _parse_tool_call(text: str, thought: str) -> ParsedResponse:
    """Parse the Action / Action Input pair, returning either a tool call or a parse error."""
    action = _match_first_group(ACTION_PATTERN, text)
    if not action:
        return _parse_error(thought, "Missing 'Action:' field. Please follow the response format.")

    raw_input = _match_first_group(ACTION_INPUT_PATTERN, text, strip=False)
    if not raw_input:
        return _parse_error(thought, f"Missing 'Action Input:' for action '{action}'.", action)

    parsed_input = _parse_json_object(raw_input)
    if isinstance(parsed_input, str):  # error message
        return _parse_error(thought, parsed_input, action)

    return ParsedResponse(
        step_type=StepType.THOUGHT_ACTION,
        thought=thought,
        action=action,
        action_input=parsed_input,
    )


def _match_first_group(pattern: re.Pattern, text: str, strip: bool = True) -> str:
    """Return the first capture group, optionally stripped. Empty string if no match."""
    match = pattern.search(text)
    if not match:
        return ""
    value = match.group(1)
    return value.strip() if strip else value


def _parse_json_object(raw: str) -> dict | str:
    """Parse JSON. Return dict on success, error message string on failure."""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        return f"Invalid JSON in Action Input: {e}"

    if not isinstance(parsed, dict):
        return "Action Input must be a JSON object."

    return parsed


def _parse_error(thought: str, error: str, action: str = "") -> ParsedResponse:
    """Build a PARSE_ERROR response with consistent fields."""
    return ParsedResponse(
        step_type=StepType.PARSE_ERROR,
        thought=thought,
        action=action,
        error=error,
    )