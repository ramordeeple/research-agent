import pytest

from src.rag.chunking import (
    _compute_boundaries,
    _find_break_point,
    chunk_text,
)


def test_chunk_empty_text() -> None:
    chunks = chunk_text("", source="test.txt")
    assert chunks == []


def test_chunk_whitespace_only() -> None:
    chunks = chunk_text("   \n\n   ", source="test.txt")
    assert chunks == []


def test_chunk_short_text_fits_in_one_chunk() -> None:
    text = "This is a short text."
    chunks = chunk_text(text, source="test.txt", chunk_size=500)

    assert len(chunks) == 1
    assert chunks[0].text == text
    assert chunks[0].index == 0
    assert chunks[0].source == "test.txt"


def test_chunk_long_text_splits() -> None:
    text = "a" * 1500
    chunks = chunk_text(text, source="test.txt", chunk_size=500, chunk_overlap=50)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.text) <= 500


def test_chunk_preserves_order() -> None:
    text = "Word " * 500
    chunks = chunk_text(text, source="test.txt", chunk_size=500, chunk_overlap=50)

    indexes = [c.index for c in chunks]
    assert indexes == list(range(len(chunks)))


def test_chunk_source_is_preserved() -> None:
    chunks = chunk_text("Some text", source="my-document.pdf")
    assert all(c.source == "my-document.pdf" for c in chunks)


def test_chunk_uses_defaults() -> None:
    """Default parameters should work without errors."""
    chunks = chunk_text("short text", source="test.txt")
    assert len(chunks) == 1


def test_chunk_overlap_greater_than_size_raises() -> None:
    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_text("some text", source="test.txt", chunk_size=100, chunk_overlap=200)


def test_chunk_overlap_equal_to_size_raises() -> None:
    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_text("some text", source="test.txt", chunk_size=100, chunk_overlap=100)


def test_chunk_respects_sentence_boundary() -> None:
    """Chunks should end at sentence boundaries when possible."""
    sentences = [
        "First sentence here.",
        "Second sentence follows.",
        "Third one is here.",
        "Fourth adds more content.",
        "Fifth and final example.",
    ]
    text = " ".join(sentences * 10)

    chunks = chunk_text(text, source="test.txt", chunk_size=200, chunk_overlap=30)

    ends_on_sentence = sum(
        1 for c in chunks if c.text.rstrip().endswith((".", "!", "?"))
    )
    assert ends_on_sentence >= len(chunks) // 2


def test_compute_boundaries_single_chunk() -> None:
    boundaries = _compute_boundaries("short", chunk_size=100, chunk_overlap=10)
    assert boundaries == [(0, 5)]


def test_compute_boundaries_multiple_chunks() -> None:
    text = "a" * 250
    boundaries = _compute_boundaries(text, chunk_size=100, chunk_overlap=20)

    assert boundaries[0][0] == 0
    assert boundaries[-1][1] == 250

    # Overlap works: each next chunk starts (chunk_size - overlap) further
    for i in range(len(boundaries) - 1):
        expected_step = 100 - 20
        actual_step = boundaries[i + 1][0] - boundaries[i][0]
        assert actual_step == expected_step




def test_find_break_point_falls_back_to_space() -> None:
    # No sentence endings, but spaces are available
    # preferred_end=30, search_start=24
    # Should find a space in range [24, 30)
    text = "no sentences here just words and more words"
    result = _find_break_point(text, start=0, preferred_end=30)

    assert text[result - 1] == " "


def test_find_break_point_falls_back_to_raw_cut() -> None:
    text = "a" * 100  # no spaces, no sentence endings
    result = _find_break_point(text, start=0, preferred_end=50)

    assert result == 50