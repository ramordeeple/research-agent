import io
from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.core.constants import API_V1_PREFIX


def test_ingest_no_file_returns_422(client: TestClient) -> None:
    response = client.post(f"{API_V1_PREFIX}/ingest")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_ingest_unsupported_extension_returns_400(client: TestClient) -> None:
    fake_file = io.BytesIO(b"not a pdf")

    response = client.post(
        f"{API_V1_PREFIX}/ingest",
        files={"file": ("image.jpg", fake_file, "image/jpeg")},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Unsupported" in response.json()["detail"]


def test_ingest_empty_filename_returns_400(client: TestClient) -> None:
    fake_file = io.BytesIO(b"content")

    response = client.post(
        f"{API_V1_PREFIX}/ingest",
        files={"file": ("", fake_file, "text/plain")},
    )

    assert response.status_code in (
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


@pytest.mark.integration
def test_ingest_txt_file_returns_count(client: TestClient, tmp_path: Path) -> None:
    """Upload a real text file, verify chunks are indexed."""
    content = "Machine learning is amazing. " * 100
    txt_path = tmp_path / "test.txt"
    txt_path.write_text(content)

    with open(txt_path, "rb") as f:
        response = client.post(
            f"{API_V1_PREFIX}/ingest",
            files={"file": ("test.txt", f, "text/plain")},
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["chunks_indexed"] > 0