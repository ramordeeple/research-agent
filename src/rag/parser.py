import logging
from pathlib import Path

from pypdf import PdfReader

from src.core.constants import SUPPORTED_FILE_EXTENSIONS

logger = logging.getLogger(__name__)


def extract_text(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix not in SUPPORTED_FILE_EXTENSIONS:
        raise ValueError(
            f"Unsupported file extension: {suffix}. "
            f"Supported: {SUPPORTED_FILE_EXTENSIONS}"
        )

    if suffix == ".pdf":
        return _extract_pdf(file_path)

    return _extract_plain_text(file_path)


def _extract_pdf(file_path: Path) -> str:
    logger.info("Reading PDF: %s", file_path)
    reader = PdfReader(str(file_path))

    pages_text: list[str] = []
    for page_num, page in enumerate(reader.pages):
        try:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        except Exception:
            logger.warning("Failed to extract text from page %d", page_num, exc_info=True)

    full_text = "\n\n".join(pages_text)
    logger.info("Extracted %d characters from %d pages", len(full_text), len(pages_text))
    return full_text


def _extract_plain_text(file_path: Path) -> str:
    logger.info("Reading text file: %s", file_path)
    text = file_path.read_text(encoding="utf-8")
    logger.info("Read %d characters", len(text))
    return text