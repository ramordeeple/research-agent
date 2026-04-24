from pathlib import Path

import pytest

from src.core.config import get_settings
from src.rag.ingest import ingest_file
from src.rag.vector_client import get_qdrant_client


pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def _auto_isolate(isolated_qdrant_collection):
    """All tests in this module use an isolated test collection."""
    yield


def test_ingest_nonexistent_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.pdf"
    with pytest.raises(FileNotFoundError):
        ingest_file(missing)


def test_ingest_wrong_extension_raises(tmp_path: Path) -> None:
    unsupported = tmp_path / "file.xlsx"
    unsupported.write_text("hello")
    with pytest.raises(ValueError, match="Unsupported"):
        ingest_file(unsupported)


def test_ingest_file_with_text(tmp_path: Path) -> None:
    file_path = _create_text_pdf(tmp_path, "Machine learning is a subset of AI. " * 50)

    count = ingest_file(file_path)

    assert count > 0

    client = get_qdrant_client()
    settings = get_settings()
    info = client.get_collection(settings.qdrant_collection)
    assert info.points_count >= count


def _create_text_pdf(tmp_path: Path, text: str) -> Path:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    pdf_path = tmp_path / "test.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)

    y = 750
    for line in text.split(". "):
        c.drawString(50, y, line)
        y -= 20
        if y < 50:
            c.showPage()
            y = 750

    c.save()
    return pdf_path