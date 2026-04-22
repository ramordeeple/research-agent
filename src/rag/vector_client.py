import logging
from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from src.core.config import get_settings
from src.core.constants import EMBEDDING_DIM

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    settings = get_settings()
    logger.info("Initializing Qdrant client: url=%s", settings.qdrant_url)
    return QdrantClient(url=settings.qdrant_url)


def ensure_collection_exists() -> None:
    """Create collection if it doesn't exist."""
    client = get_qdrant_client()
    settings = get_settings()
    collection_name = settings.qdrant_collection

    existing = [c.name for c in client.get_collections().collections]

    if collection_name in existing:
        logger.debug("Collection '%s' already exists", collection_name)
        return

    logger.info("Creating Qdrant collection: %s", collection_name)
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
    )