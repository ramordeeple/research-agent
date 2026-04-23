import logging

from qdrant_client.models import ScoredPoint

from src.core.config import get_settings
from src.core.constants import DEFAULT_TOP_K
from src.rag.embeddings import embed_query
from src.rag.schemas import SearchResult, Chunk
from src.rag.vector_client import get_qdrant_client, ensure_collection_exists

logger = logging.getLogger(__name__)


def retrieve(query: str, top_k: int = DEFAULT_TOP_K) -> list[SearchResult]:
    if not query or not query.strip():
        return []

    if top_k <= 0:
        raise ValueError(f"top_k must be >= 0, got {top_k}")

    ensure_collection_exists()

    query_embedding = embed_query(query)
    raw_points = _search_qdrant(query_embedding, top_k)
    results = _parse_results(raw_points)

    logger.info(
        "Retrieved %d results for query (top_k=%d, query_length=%d)",
        len(results), top_k, len(query),
    )

    return results

def _search_qdrant(query_embedding: list[float], top_k: int) -> list[ScoredPoint]:
    client = get_qdrant_client()
    settings = get_settings()

    return client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_embedding,
        limit=top_k,
        with_payload=True
    ).points

def _parse_results(raw_points) -> list[SearchResult]:
    results: list[SearchResult] = []

    for point in raw_points:
        payload = point.payload or {}

        try:
            chunk = Chunk(
                text=payload["text"],
                index=payload["index"],
                source=payload["source"],
            )
        except KeyError as e:
            logger.warning("Point %s missing field %s, skipping", point.id, e)
            continue

        results.append(SearchResult(chunk=chunk, score=float(point.score)))

    return results

