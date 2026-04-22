import logging

from src.core.constants import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
from src.rag.schemas import Chunk

logger = logging.getLogger(__name__)

def chunk_text(
        text: str,
        source: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Chunk]:
    _validate_params(chunk_size, chunk_overlap)

    text = text.strip()
    if not text:
        return []

    boundaries = _compute_boundaries(text, chunk_size, chunk_overlap)
    chunks = _build_chunks(text, boundaries, source)

    logger.debug("Chunked text into %d chunks (source=%s)", len(chunks), source)


    return chunks

def _validate_params(chunk_size: int, chunk_overlap: int) -> None:
    if chunk_overlap >= chunk_size:
        raise ValueError(
            f"chunk_overlap ({chunk_overlap}) must be smaller than chunk size ({chunk_size})"
        )

def _compute_boundaries(
        text: str,
        chunk_size: int,
        chunk_overlap: int
) -> list[tuple[int, int]]:
    """Computes (start, end) for each chunk"""
    boundaries: list[tuple[int, int]] = []
    text_length = len(text)
    step = chunk_size - chunk_overlap

    start = 0
    while start < text_length:
        end = min(start + chunk_size, text_length)
        if end < text_length:
            end = _find_break_point(text, start, end)

        boundaries.append((start, end))
        start += step

    return boundaries


def _build_chunks(
        text: str,
        boundaries: list[tuple[int, int]],
        source: str,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    index = 0

    for start, end in boundaries:
        chunk_text_value = text[start:end].strip()
        if not chunk_text_value:
            continue

        chunks.append(
            Chunk(
                text=chunk_text_value,
                index=index,
                source=source,
            )
        )
        index += 1

    return chunks


def _find_break_point(text: str, start: int, preferred_end: int) -> int:
    """Looks for closest 'good' boundary for cut"""
    search_start = start + int((preferred_end - start) * 0.8)

    for separator in (". ", ".\n", "!\n", "?\n", "! ", "? ", "\n\n"):
        last_sep = text.rfind(separator, search_start, preferred_end)
        if last_sep != -1:
            return last_sep + len(separator)

    last_space = text.rfind(" ", search_start, preferred_end)
    if last_space != -1:
        return last_space + 1

    return preferred_end
