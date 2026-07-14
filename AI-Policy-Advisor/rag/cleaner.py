"""
rag/cleaner.py
===============
Text cleaning / preprocessing, run on the output of rag/parser.py.

WHY THIS FILE EXISTS
---------------------
Raw extracted text (whether from the PDF text layer or OCR) is messy:
- OCR introduces stray characters and inconsistent spacing
- PDFs often hyphenate words across line breaks: "govern-\nment"
- Repeated headers/footers ("Page 3 of 12", letterhead text) appear on
  every page and pollute chunk embeddings later if left in
- Multiple blank lines, tabs, and non-printable characters add noise
  without adding meaning

Cleaning this BEFORE chunking (Phase 3) matters because chunk boundaries
and embeddings are sensitive to noise — a chunk that's 20% repeated
header text produces a worse embedding than a clean chunk of pure content.
"""

import re
import unicodedata
from collections import Counter
from typing import List

from utils.logger import get_logger

logger = get_logger(__name__)


def _dehyphenate(text: str) -> str:
    """Join words that were hyphenated across a line break: 'govern-\nment' -> 'government'."""
    return re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)


def _normalize_unicode(text: str) -> str:
    """Normalize unicode (fixes weird OCR artifacts like ligatures, curly quotes)."""
    return unicodedata.normalize("NFKC", text)


def _collapse_whitespace(text: str) -> str:
    """Collapse multiple spaces/tabs into one, and 3+ blank lines into a single blank line."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _strip_non_printable(text: str) -> str:
    """Remove control characters that sometimes leak in from OCR/PDF encoding issues."""
    return "".join(ch for ch in text if ch.isprintable() or ch in "\n\t")


def _detect_and_remove_repeated_lines(pages_text: List[str], min_occurrences_ratio: float = 0.6) -> List[str]:
    """
    Detect lines (like headers/footers/letterhead) that repeat across most
    pages of a document, and strip them out.

    A line that appears on 60%+ of pages is almost certainly boilerplate
    (e.g. "Government of India — Ministry of Education") rather than
    actual policy content, so we remove it from every page.
    """
    if len(pages_text) < 2:
        return pages_text  # not enough pages to detect a repeating pattern

    line_counts: Counter = Counter()
    per_page_lines = []

    for page_text in pages_text:
        lines = [line.strip() for line in page_text.split("\n") if line.strip()]
        per_page_lines.append(lines)
        for line in set(lines):  # count each line once per page
            line_counts[line] += 1

    threshold = max(2, int(len(pages_text) * min_occurrences_ratio))
    boilerplate = {line for line, count in line_counts.items() if count >= threshold}

    if boilerplate:
        logger.info("Removing %d repeated header/footer lines found across pages", len(boilerplate))

    cleaned_pages = []
    for lines in per_page_lines:
        cleaned_pages.append("\n".join(line for line in lines if line not in boilerplate))

    return cleaned_pages


def clean_text(text: str) -> str:
    """
    Apply the full single-string cleaning pipeline: dehyphenate, normalize
    unicode, strip non-printables, collapse whitespace.

    Use this for cleaning one page or one arbitrary block of text.
    """
    text = _strip_non_printable(text)
    text = _normalize_unicode(text)
    text = _dehyphenate(text)
    text = _collapse_whitespace(text)
    return text


def clean_document_pages(pages_text: List[str]) -> List[str]:
    """
    Clean a full document's pages together, which additionally allows
    cross-page repeated-boilerplate detection (headers/footers).

    Args:
        pages_text: raw text for each page, in page order.

    Returns:
        Cleaned text for each page, in the same order.
    """
    pages_text = _detect_and_remove_repeated_lines(pages_text)
    cleaned = [clean_text(page) for page in pages_text]
    logger.info("Cleaned %d pages", len(cleaned))
    return cleaned
