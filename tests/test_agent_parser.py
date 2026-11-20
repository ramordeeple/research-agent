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
        "Thought: I need to search the documents.\n"
        "Action: rag_search\n"
        'Action Input: {"query": "study duration"}'
    )

    result = parse_llm_response(text)

    assert result.step_type == StepType.THOUGHT_ACTION
    assert result.action == "rag_search"
    assert result.action_input == {"query": "study duration"}


def test_parse_missing_action() -> None:
    text = "Thought: I'm thinking but not deciding."

    result = parse_llm_response(text)

    assert result.step_type == StepType.PARSE_ERROR
    assert "Action" in result.error


def test_parse_invalid_json_input() -> None:
    text = (
        "Thought: I'll try to use a tool.\n"
        "Action: rag_search\n"
        "Action Input: {query: not valid json}"
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
        "Action: rag_search\n"
        'Action Input: {"query": "study duration"}\n'
        "Final Answer: The study lasted 12 weeks."
    )

    result = parse_llm_response(text)

    assert result.step_type == StepType.FINAL_ANSWER
    assert result.final_answer == "The study lasted 12 weeks."
