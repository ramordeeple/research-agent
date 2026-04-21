import pytest
from starlette.testclient import TestClient

from src.main import create_app

@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)