import logging
import shutil
import tempfile
from pathlib import Path

from src.core.constants import SUPPORTED_FILE_EXTENSIONS
from src.rag.ingest import ingest_file

logger = logging.getLogger(__name__)


def process_upload(filename: str, file_stream) -> int:
    """Save uploaded file to a temp location, ingest it, clean up. Returns chunk count."""
    _validate_filename(filename)

    with tempfile.NamedTemporaryFile(
        suffix=Path(filename).suffix,
        delete=False,
    ) as tmp:
        tmp_path = Path(tmp.name)
        shutil.copyfileobj(file_stream, tmp)

    try:
        logger.info("Ingesting uploaded file: %s (temp: %s)", filename, tmp_path)
        chunks_indexed = ingest_file(tmp_path)
        return chunks_indexed
    finally:
        tmp_path.unlink(missing_ok=True)


def _validate_filename(filename: str) -> None:
    if not filename:
        raise ValueError("Filename is empty")

    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_FILE_EXTENSIONS:
        raise ValueError(
            f"Unsupported file extension: {suffix}. "
            f"Supported: {SUPPORTED_FILE_EXTENSIONS}"
        )