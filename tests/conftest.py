import uuid

import pytest
from fastapi.testclient import TestClient

from src.core.config import get_settings
from src.core.constants import EMBEDDING_DIM
from src.main import create_app
from src.rag.vector_client import get_qdrant_client
from qdrant_client.models import Distance, VectorParams


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


@pytest.fixture
def isolated_qdrant_collection(monkeypatch) -> str:
    """
    Create a unique test collection, override settings to use it,
    yield collection name, clean up after test.
    """
    collection_name = f"test_{uuid.uuid4().hex[:8]}"

    # Override the collection name in settings via env variable
    monkeypatch.setenv("QDRANT_COLLECTION", collection_name)

    # Clear the cached settings so the new env var is picked up
    get_settings.cache_clear()

    client = get_qdrant_client()
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
    )

    yield collection_name

    # Cleanup
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    get_settings.cache_clear()
