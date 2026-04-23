import logging
import shutil
import tempfile
from pathlib import Path

from src.core.constants import SUPPORTED_FILE_EXTENSIONS
from src.rag.ingest import ingest_file

logger = logging.getLogger(__name__)


def process_upload(filename: str, file_stream) -> int:
    """Save uploaded file to a temp dir, ingest it, clean up. Returns chunk count."""
    _validate_filename(filename)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / filename

        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file_stream, f)

        logger.info("Ingesting uploaded file: %s", filename)
        return ingest_file(tmp_path)


def _validate_filename(filename: str) -> None:
    if not filename:
        raise ValueError("Filename is empty")

    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_FILE_EXTENSIONS:
        raise ValueError(
            f"Unsupported file extension: {suffix}. "
            f"Supported: {SUPPORTED_FILE_EXTENSIONS}"
        )