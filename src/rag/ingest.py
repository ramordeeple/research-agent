import logging
import uuid
from pathlib import Path


from qdrant_client.models import PointStruct

from src.core.enums import ExitCode
from src.core.config import get_settings
from src.rag.chunking import chunk_text
from src.rag.embeddings import embed_texts
from src.rag.pdf_parser import extract_text_from_pdf
from src.rag.vector_client import ensure_collection_exists, get_qdrant_client
from src.rag.schemas import Chunk

logger = logging.getLogger(__name__)


def ingest_pdf(file_path: Path) -> int:
    """Ingest a PDF into Qdrant. Returns number of chunks indexed."""
    ensure_collection_exists()

    text = extract_text_from_pdf(file_path)
    if not text.strip():
        logger.warning("No text extracted from %s", file_path)
        return ExitCode.SUCCESS

    chunks = chunk_text(text, source=file_path.name)
    if not chunks:
        logger.warning("No chunks produced for %s", file_path)
        return ExitCode.SUCCESS

    logger.info("Embedding %d chunks from %s", len(chunks), file_path.name)
    embeddings = embed_texts([c.text for c in chunks])

    _upsert_chunks(chunks, embeddings)

    logger.info("Ingested %d chunks from %s", len(chunks), file_path.name)
    return len(chunks)


def _upsert_chunks(chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    client = get_qdrant_client()
    settings = get_settings()

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk.text,
                "source": chunk.source,
                "index": chunk.index,
            },
        )
        for chunk, embedding in zip(chunks, embeddings, strict=True)
    ]

    client.upsert(
        collection_name=settings.qdrant_collection,
        points=points,
    )