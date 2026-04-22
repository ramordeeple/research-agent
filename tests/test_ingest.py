import uuid
from pathlib import Path

import pytest
from pypdf import PdfWriter

from qdrant_client.models import Distance, VectorParams

from src.core.config import get_settings
from src.core.constants import EMBEDDING_DIM
from src.rag.ingest import ingest_file
from src.rag.vector_client import get_qdrant_client


# pytestmark = pytest.mark.integration


@pytest.fixture
def qdrant_test_collection() -> str:
    """Create a unique test collection, yield its name, clean up after."""
    client = get_qdrant_client()
    collection_name = f"test_{uuid.uuid4().hex[:8]}"

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
    )

    yield collection_name

    client.delete_collection(collection_name)


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a minimal PDF file for testing."""
    file_path = tmp_path / "sample.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)

    with open(file_path, "wb") as f:
        writer.write(f)

    return file_path


def test_ingest_nonexistent_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.pdf"

    with pytest.raises(FileNotFoundError):
        ingest_file(missing)


def test_ingest_wrong_extension_raises(tmp_path: Path) -> None:
    unsupported = tmp_path / "file.xlsx"
    unsupported.write_text("hello")

    with pytest.raises(ValueError, match="Unsupported"):
        ingest_file(unsupported)


def test_ingest_file_with_text(tmp_path: Path, monkeypatch) -> None:
    """Create a PDF with actual text content and verify it's indexed."""

    # Create a simple text-based PDF via reportlab if available,
    # or use a fixture file. For now — test with real PDF reading:
    file_path = _create_text_pdf(tmp_path, "Machine learning is a subset of AI. " * 50)

    count = ingest_file(file_path)

    assert count > 0

    client = get_qdrant_client()
    settings = get_settings()
    info = client.get_collection(settings.qdrant_collection)
    assert info.points_count >= count


def _create_text_pdf(tmp_path: Path, text: str) -> Path:
    """Create a real text-bearing PDF for testing."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    file_path = tmp_path / "test.pdf"
    c = canvas.Canvas(str(file_path), pagesize=letter)

    y = 750
    for line in text.split(". "):
        c.drawString(50, y, line)
        y -= 20
        if y < 50:
            c.showPage()
            y = 750

    c.save()
    return file_path