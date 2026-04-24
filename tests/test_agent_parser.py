from src.agent.parser import parse_llm_response
from src.agent.schemas import StepType


def test_parse_final_answer() -> None:
    text = "Thought: I know the answer.\nFinal Answer: The capital of France is Paris."

    result = parse_llm_response(text)

    assert result.step_type == StepType.FINAL_ANSWER
    assert result.thought == "I know the answer."
    assert result.final_answer == "The capital of France is Paris."


def test_parse_tool_call() -> None:
    text = (
        "Thought: I need to calculate this.\n"
        "Action: calculator\n"
        'Action Input: {"expression": "2 + 3"}'
    )

    result = parse_llm_response(text)

    assert result.step_type == StepType.THOUGHT_ACTION
    assert result.action == "calculator"
    assert result.action_input == {"expression": "2 + 3"}


def test_parse_missing_action() -> None:
    text = "Thought: I'm thinking but not deciding."

    result = parse_llm_response(text)

    assert result.step_type == StepType.PARSE_ERROR
    assert "Action" in result.error


def test_parse_invalid_json_input() -> None:
    text = (
        "Thought: I'll try to use a tool.\n"
        "Action: calculator\n"
        "Action Input: {expression: not valid json}"
    )

    result = parse_llm_response(text)

    assert result.step_type == StepType.PARSE_ERROR
    assert "JSON" in result.error


def test_parse_handles_multiline_final_answer() -> None:
    text = (
        "Thought: Multiple paragraphs needed.\n"
        "Final Answer: Line one.\n"
        "Line two.\n"
        "Line three."
    )

    result = parse_llm_response(text)

    assert result.step_type == StepType.FINAL_ANSWER
    assert "Line one" in result.final_answer
    assert "Line three" in result.final_answer


def test_parse_prefers_final_answer_over_action() -> None:
    """If both Final Answer and Action present, Final Answer wins."""
    text = (
        "Thought: Done.\n"
        "Action: calculator\n"
        'Action Input: {"expression": "1+1"}\n'
        "Final Answer: The result is 2."
    )

    result = parse_llm_response(text)

    assert result.step_type == StepType.FINAL_ANSWER
    assert result.final_answer == "The result is 2."