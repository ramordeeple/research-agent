import logging
from functools import lru_cache

from fastembed import TextEmbedding

from src.core.config import get_settings

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_embedding_model() -> TextEmbedding:
    settings = get_settings()
    logger.info("Loading embedding model: %s", settings.embedding_model)
    model = TextEmbedding(model_name=settings.embedding_model)
    logger.info("Embedding model loaded")

    return model

def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    model = get_embedding_model()
    logger.debug("Embedding %d texts", len(texts))

    embeddings = list(model.embed(texts))

    result = [(emb.tolist()) for emb in embeddings]

    return result

def embed_query(query: str) -> list[float]:
    model = get_embedding_model()

    embedding = next(model.query_embed(query))

    return embedding.tolist()