
import pytest

from src.core.config import get_settings
from src.rag.ingest import ingest_file
from src.rag.retriever import retrieve
from src.rag.vector_client import ensure_collection_exists, get_qdrant_client

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def indexed_document(tmp_path_factory) -> None:
    client = get_qdrant_client()
    settings = get_settings()

    existing = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection in existing:
        client.delete_collection(settings.qdrant_collection)

    ensure_collection_exists()

    tmp_path = tmp_path_factory.mktemp("retriever_test")
    doc_path = tmp_path / "ml_doc.txt"

    ml_section = (
        "Machine learning is a subset of artificial intelligence. "
        "It focuses on algorithms that learn from data without explicit programming. "
        "Common applications include image recognition, natural language processing, and recommendation systems. "
        "Supervised learning uses labeled data to train models. "
        "Unsupervised learning finds patterns in unlabeled data. "
        "Reinforcement learning teaches agents through rewards and penalties. "
    ) * 3

    dl_section = (
        "Deep learning uses neural networks with multiple layers. "
        "Neural networks are inspired by the human brain. "
        "Convolutional networks excel at image processing tasks. "
        "Recurrent networks handle sequential data like text and speech. "
        "Transformers revolutionized natural language understanding. "
        "Attention mechanisms allow models to focus on relevant parts of input. "
    ) * 3

    cooking_section = (
        "Cooking pasta requires boiling water and salt. "
        "You should not overcook spaghetti or it becomes mushy. "
        "Italian cuisine uses fresh ingredients and olive oil. "
        "Tomato sauce pairs well with many pasta shapes. "
        "Garlic and basil add traditional Italian flavor. "
        "Al dente means the pasta is firm to the bite. "
    ) * 3

    content = f"{ml_section}\n\n{dl_section}\n\n{cooking_section}"

    doc_path.write_text(content)
    ingest_file(doc_path)


def test_retrieve_empty_query_returns_empty() -> None:
    results = retrieve("")
    assert results == []


def test_retrieve_whitespace_query_returns_empty() -> None:
    results = retrieve("   \n  ")
    assert results == []


def test_retrieve_invalid_top_k_raises() -> None:
    with pytest.raises(ValueError, match="top_k"):
        retrieve("some query", top_k=0)


def test_retrieve_returns_results(indexed_document) -> None:
    results = retrieve("what is machine learning?", top_k=3)

    assert len(results) > 0
    assert len(results) <= 3

    for result in results:
        assert result.chunk.text
        assert result.chunk.source
        assert 0.0 <= result.score <= 1.0


def test_retrieve_finds_relevant_content(indexed_document) -> None:
    """Query about ML should prefer ML chunks over cooking chunks."""
    results = retrieve("neural networks and deep learning", top_k=3)

    # DEBUG — посмотрим что реально пришло
    for i, r in enumerate(results):
        print(f"[{i}] score={r.score:.3f} source={r.chunk.source}")
        print(f"    {r.chunk.text[:200]}")

    assert len(results) > 0
    top_result_text = results[0].chunk.text.lower()

    assert any(word in top_result_text for word in ("neural", "deep", "learning", "ai"))
    assert "pasta" not in top_result_text


def test_retrieve_respects_top_k(indexed_document) -> None:
    for k in (1, 2, 5):
        results = retrieve("machine learning", top_k=k)
        assert len(results) <= k


def test_retrieve_results_sorted_by_score(indexed_document) -> None:
    results = retrieve("artificial intelligence", top_k=5)

    if len(results) > 1:
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)