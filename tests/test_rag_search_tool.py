from unittest.mock import patch

import pytest

from src.rag.schemas import Chunk, SearchResult
from src.tools.rag_search import RagSearchInput, RagSearchTool


@pytest.fixture
def tool() -> RagSearchTool:
    return RagSearchTool()


def test_returns_no_results_message_when_empty(tool: RagSearchTool) -> None:
    with patch("src.tools.rag_search.retrieve", return_value=[]):
        result = tool.execute(RagSearchInput(query="anything"))

    assert "No relevant documents" in result


def test_formats_results_with_source_and_score(tool: RagSearchTool) -> None:
    fake_result = SearchResult(
        chunk=Chunk(text="Python is great", index=0, source="doc.pdf"),
        score=0.85,
    )

    with patch("src.tools.rag_search.retrieve", return_value=[fake_result]):
        result = tool.execute(RagSearchInput(query="python"))

    assert "doc.pdf" in result
    assert "Python is great" in result
    assert "0.85" in result


def test_name_and_description(tool: RagSearchTool) -> None:
    assert tool.name == "rag_search"
    assert "documents" in tool.description.lower()