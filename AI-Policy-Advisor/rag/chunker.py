"""
rag/chunker.py
================
Splits cleaned document text into overlapping chunks for embedding.

WHY OVERLAP MATTERS: if a sentence describing an important clause sits
exactly on a chunk boundary, a hard cut would split it across two chunks
and neither retrieval hit would carry the full meaning. A ~15% overlap
means boundary-spanning ideas always appear intact in at least one chunk.

Chunk size is measured in WORDS (not characters/tokens) for simplicity and
zero extra dependencies. ~250 words is a well-tested sweet spot for policy
documents: long enough to preserve a clause's context, short enough that
the embedding stays focused on one topic instead of blurring several.
"""

from dataclasses import dataclass
from typing import List

from utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_CHUNK_SIZE_WORDS = 250
DEFAULT_OVERLAP_WORDS = 40  # ~15% of chunk size


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    text: str
    chunk_index: int
    word_count: int


def chunk_text(
    text: str,
    doc_id: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE_WORDS,
    overlap: int = DEFAULT_OVERLAP_WORDS,
) -> List[Chunk]:
    """
    Split text into overlapping word-based chunks.

    Args:
        text: cleaned full document text.
        doc_id: identifier of the parent document, used to build chunk_id
                and later stored as metadata in the vector DB.
        chunk_size: target words per chunk.
        overlap: words shared between consecutive chunks.

    Returns:
        List of Chunk objects in order.
    """
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    if not words:
        logger.warning("chunk_text called with empty text for doc_id=%s", doc_id)
        return []

    chunks: List[Chunk] = []
    start = 0
    index = 0
    step = chunk_size - overlap

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_text_value = " ".join(chunk_words)

        chunks.append(
            Chunk(
                chunk_id=f"{doc_id}_chunk_{index}",
                doc_id=doc_id,
                text=chunk_text_value,
                chunk_index=index,
                word_count=len(chunk_words),
            )
        )

        index += 1
        start += step

        if end == len(words):
            break

    logger.info("Split doc_id=%s into %d chunks (size=%d, overlap=%d)",
                doc_id, len(chunks), chunk_size, overlap)
    return chunks
