import logging
import sys

from src.core.constants import DEFAULT_TOP_K
from src.core.logger import setup_logging
from src.rag.retriever import retrieve

PREVIEW_LENGTH = 200

def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    if len(sys.argv) < 2:
        logger.info("Usage: python scripts/check_retriever.py 'your query here'")
        return

    query = " ".join(sys.argv[1:])
    results = retrieve(query, top_k=DEFAULT_TOP_K)

    if not results:
        logger.info("No results found")
        return

    print(f"\n=== Top {len(results)} results for: {query!r} ===\n")
    for i, result in enumerate(results, 1):
        print(f"[{i}] score={result.score:.4f} source={result.chunk.source}")
        print(f"    {result.chunk.text[:PREVIEW_LENGTH]}...")
        print()


if __name__ == "__main__":
    main()