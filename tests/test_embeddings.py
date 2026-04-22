from src.core.constants import EMBEDDING_DIM
from src.rag.embeddings import embed_query, embed_texts


def test_embed_texts_returns_correct_dimension() -> None:
    embeddings = embed_texts(["Hello world"])

    assert len(embeddings) == 1
    assert len(embeddings[0]) == EMBEDDING_DIM


def test_embed_texts_multiple() -> None:
    texts = ["first text", "second text", "third text"]
    embeddings = embed_texts(texts)

    assert len(embeddings) == 3
    for emb in embeddings:
        assert len(emb) == EMBEDDING_DIM


def test_embed_texts_empty_list() -> None:
    embeddings = embed_texts([])
    assert embeddings == []


def test_embed_query_returns_correct_dimension() -> None:
    embedding = embed_query("what is machine learning?")
    assert len(embedding) == EMBEDDING_DIM


def test_embeddings_are_different_for_different_texts() -> None:
    emb1 = embed_query("cats are animals")
    emb2 = embed_query("weather forecast")

    assert emb1 != emb2


def test_embeddings_are_similar_for_similar_texts() -> None:
    emb1 = embed_query("machine learning")
    emb2 = embed_query("ML algorithms")
    emb3 = embed_query("banana fruit")

    def dot(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    sim_ml = dot(emb1, emb2)
    sim_unrelated = dot(emb1, emb3)

    assert sim_ml > sim_unrelated