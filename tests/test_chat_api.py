from fastapi import status
from fastapi.testclient import TestClient

from src.core.constants import API_V1_PREFIX


def test_chat_empty_message_returns_422(client: TestClient) -> None:
    response = client.post(f"{API_V1_PREFIX}/chat", json={"message": ""})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_chat_missing_message_returns_422(client: TestClient) -> None:
    response = client.post(f"{API_V1_PREFIX}/chat", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_chat_too_long_message_returns_422(client: TestClient) -> None:
    long_message = "a" * 4000
    response = client.post(f"{API_V1_PREFIX}/chat", json={"message": long_message})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_chat_returns_answer(client: TestClient) -> None:
    response = client.post(f"{API_V1_PREFIX}/chat", json={"message": "Say 'OK'"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "answer" in data
    assert data["answer"]