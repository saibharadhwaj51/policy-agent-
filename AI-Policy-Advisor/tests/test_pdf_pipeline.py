"""
tests/test_pdf_pipeline.py
============================
Tests for the Phase 2 PDF ingestion pipeline.

Run with:
    pytest tests/test_pdf_pipeline.py -v

These tests use the two sample PDFs in assets/:
- sample_text_policy.pdf     -> should extract via the text layer (fast path)
- sample_scanned_policy.pdf  -> has no text layer, must go through OCR
"""

from pathlib import Path

import pytest

from rag.parser import parse_pdf
from rag.cleaner import clean_text, clean_document_pages

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
TEXT_PDF = ASSETS_DIR / "sample_text_policy.pdf"
SCANNED_PDF = ASSETS_DIR / "sample_scanned_policy.pdf"


def test_text_pdf_uses_text_layer_not_ocr():
    """A normal digital PDF should be read via the fast text-layer path."""
    doc = parse_pdf(TEXT_PDF)
    assert doc.total_pages == 2
    assert doc.ocr_page_count == 0
    assert all(p.source == "text_layer" for p in doc.pages)
    assert "Digital Literacy" in doc.full_text


def test_scanned_pdf_falls_back_to_ocr():
    """A scanned PDF (no text layer) must be routed through OCR and still recover the content."""
    doc = parse_pdf(SCANNED_PDF)
    assert doc.total_pages == 1
    assert doc.ocr_page_count == 1
    assert doc.pages[0].source == "ocr"
    # OCR isn't pixel-perfect, but key terms should be recovered
    assert "Healthcare" in doc.full_text or "Health" in doc.full_text


def test_clean_text_dehyphenates():
    dirty = "This policy covers govern-\nment schools."
    assert "government schools" in clean_text(dirty)


def test_clean_text_collapses_whitespace():
    dirty = "Too    many     spaces\n\n\n\n\nand blank lines"
    cleaned = clean_text(dirty)
    assert "    " not in cleaned
    assert "\n\n\n" not in cleaned


def test_clean_document_pages_removes_repeated_headers():
    pages = [
        "GOVERNMENT OF INDIA — MINISTRY OF EDUCATION\nActual content for page one.",
        "GOVERNMENT OF INDIA — MINISTRY OF EDUCATION\nActual content for page two.",
        "GOVERNMENT OF INDIA — MINISTRY OF EDUCATION\nActual content for page three.",
    ]
    cleaned = clean_document_pages(pages)
    for page in cleaned:
        assert "GOVERNMENT OF INDIA" not in page
    assert "Actual content for page one." in cleaned[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
