import asyncio
import logging
from pathlib import Path

from src.core.logger import setup_logging
from src.rag.ingest import ingest_file


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    file_path = Path("data/sample.pdf")

    if not file_path.exists():
        logger.error("No file at %s", file_path)
        return

    count = ingest_file(file_path)
    logger.info("Ingested %d chunks", count)

if __name__ == "__main__":
    main()