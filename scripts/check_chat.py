import asyncio
import logging
import sys

from src.core.logger import setup_logging
from src.services.chat_service import process_chat


async def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    if len(sys.argv) < 2:
        logger.info("Usage: python scripts/check_chat.py 'your question'")
        return

    question = " ".join(sys.argv[1:])
    answer, sources = await process_chat(question)

    print(f"\n=== Question: {question!r} ===\n")
    print(f"Answer:\n{answer}\n")
    print(f"Sources ({len(sources)}):")
    for i, source in enumerate(sources, 1):
        print(f"  [{i}] {source.source} (score={source.score:.3f})")


if __name__ == "__main__":
    asyncio.run(main())