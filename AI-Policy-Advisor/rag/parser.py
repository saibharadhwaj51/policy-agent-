"""
rag/parser.py
=============
The orchestrator for PDF ingestion. This is the file the rest of the app
actually calls — it hides the text-vs-OCR decision behind one simple
function: `parse_pdf(path) -> ParsedDocument`.

WHY THIS FILE EXISTS
---------------------
tools/pdf_reader.py and tools/ocr_reader.py each do one narrow job on
purpose (Single Responsibility Principle). Something has to combine them:
"for each page, use the fast path if possible, fall back to the slow path
if needed, and stitch the results into one document." That's this file.

Every later phase (chunker, embeddings, agents) will import ONLY this
file — they never need to know PyMuPDF or Tesseract exist.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from tools.pdf_reader import read_pdf_pages, render_page_to_image
from tools.ocr_reader import ocr_image
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedPage:
    """One page's final text, after the text-vs-OCR decision has been made."""

    page_number: int
    text: str
    source: str  # "text_layer" or "ocr" — useful for debugging extraction quality


@dataclass
class ParsedDocument:
    """The full parsed document: every page's text plus a convenience full-text field."""

    file_name: str
    pages: List[ParsedPage] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """All pages joined with a page-break marker, for chunking in Phase 3."""
        return "\n\n".join(f"[Page {p.page_number}]\n{p.text}" for p in self.pages)

    @property
    def total_pages(self) -> int:
        return len(self.pages)

    @property
    def ocr_page_count(self) -> int:
        return sum(1 for p in self.pages if p.source == "ocr")


def parse_pdf(pdf_path: Path) -> ParsedDocument:
    """
    Parse a PDF end-to-end: extract text directly where possible, OCR where
    necessary, and return one unified ParsedDocument.

    Args:
        pdf_path: path to the PDF on disk.

    Returns:
        ParsedDocument with per-page and full-document text.
    """
    pdf_path = Path(pdf_path)
    logger.info("Starting parse of %s", pdf_path.name)

    raw_pages = read_pdf_pages(pdf_path)
    parsed_pages: List[ParsedPage] = []

    for page in raw_pages:
        if not page.needs_ocr:
            parsed_pages.append(
                ParsedPage(page_number=page.page_number, text=page.raw_text, source="text_layer")
            )
            continue

        # Fallback path: render the page as an image and OCR it
        logger.info("Running OCR on page %d of %s", page.page_number, pdf_path.name)
        image = render_page_to_image(pdf_path, page.page_number)
        ocr_text = ocr_image(image, page_number=page.page_number)
        parsed_pages.append(
            ParsedPage(page_number=page.page_number, text=ocr_text, source="ocr")
        )

    document = ParsedDocument(file_name=pdf_path.name, pages=parsed_pages)
    logger.info(
        "Finished parsing %s: %d pages total, %d required OCR",
        pdf_path.name, document.total_pages, document.ocr_page_count,
    )
    return document
