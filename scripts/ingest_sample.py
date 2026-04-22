import asyncio
import logging
from pathlib import Path

from src.core.logger import setup_logging
from src.rag.ingest import ingest_pdf


async def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    pdf_path = Path("data/sample.pdf")

    logger.info("Current working directory: %s", Path.cwd())
    logger.info("Looking for file at: %s", pdf_path.resolve())
    logger.info("File exists: %s", pdf_path.exists())

    if not pdf_path.exists():
        logger.error("No file at %s", pdf_path)
        return

    count = ingest_pdf(pdf_path)
    logger.info("Ingested %d pages", count)

if __name__ == "__main__":
    asyncio.run(main())