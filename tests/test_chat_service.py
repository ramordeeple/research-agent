from src.agent.schemas import AgentStep
from src.llm import Message
from src.memory.store import MemoryStore
from src.services.chat_service import _extract_sources, _parse_rag_observation


def test_parse_rag_observation_with_results() -> None:
    observation = (
        "[1] Source: doc.pdf (relevance: 0.85)\n"
        "Python is a programming language.\n"
        "\n"
        "[2] Source: other.pdf (relevance: 0.72)\n"
        "Functions are first-class objects."
    )

    sources = _parse_rag_observation(observation)

    assert len(sources) == 2
    assert sources[0].source == "doc.pdf"
    assert sources[0].score == 0.85
    assert "Python is a programming language" in sources[0].text


def test_parse_rag_observation_with_no_results() -> None:
    observation = "No relevant documents found."

    sources = _parse_rag_observation(observation)

    assert sources == []


def test_extract_sources_skips_non_rag_steps() -> None:
    steps = [
        AgentStep(
            iteration=1,
            thought="thinking",
            action="calculator",
            action_input={"expression": "2+2"},
            observation="4",
        ),
    ]

    sources = _extract_sources(steps)

    assert sources == []


def test_extract_sources_deduplicates() -> None:
    """If agent calls rag_search twice with overlapping results, deduplicate."""
    obs = "[1] Source: doc.pdf (relevance: 0.85)\nSame text here."

    steps = [
        AgentStep(iteration=1, thought="t1", action="rag_search", action_input={"query": "x"}, observation=obs),
        AgentStep(iteration=2, thought="t2", action="rag_search", action_input={"query": "y"}, observation=obs),
    ]

    sources = _extract_sources(steps)

    assert len(sources) == 1


def test_memory_store_returns_empty_for_new_session():
    store = MemoryStore()
    assert store.get_messages("new-id") == []


def test_memory_store_appends_messages():
    store = MemoryStore()
    msg = Message.user("hello")
    store.append("session-1", [msg])

    assert store.get_messages("session-1") == [msg]


def test_memory_store_isolates_sessions():
    store = MemoryStore()
    store.append("a", [Message.user("from a")])
    store.append("b", [Message.user("from b")])

    assert len(store.get_messages("a")) == 1
    assert len(store.get_messages("b")) == 1