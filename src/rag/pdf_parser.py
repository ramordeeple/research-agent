import logging
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    if file_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected .pdf file, got: {file_path.suffix}")

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