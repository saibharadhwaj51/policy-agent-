"""
tools/pdf_reader.py
====================
Low-level PDF reading tool, built on PyMuPDF (imported as `fitz`).

WHY THIS FILE EXISTS
---------------------
This is intentionally "dumb" and single-purpose: it only knows how to open
a PDF and answer two questions per page — "what text is embedded here?" and
"is that text enough to trust, or does this look like a scanned image?".
It does NOT decide what to do about scanned pages (that's rag/parser.py's
job) and does NOT clean text (that's rag/cleaner.py's job). Keeping this
file narrow means it's easy to unit-test and easy to swap out later if you
ever need a different PDF engine.

MIN_CHARS_PER_PAGE is a heuristic: a real page of policy text almost always
has hundreds of characters. A page with, say, 10 extracted characters is
almost certainly a scanned image where PyMuPDF only picked up a stray
watermark or page number — so we treat it as "needs OCR".
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List

import fitz  # PyMuPDF

from utils.logger import get_logger

logger = get_logger(__name__)

MIN_CHARS_PER_PAGE = 30  # below this, we assume the page is scanned


@dataclass
class PageContent:
    """Represents one page's extraction result before OCR fallback is applied."""

    page_number: int          # 1-indexed, human-friendly
    raw_text: str              # whatever PyMuPDF could extract directly
    needs_ocr: bool            # True if raw_text is too short to trust
    width: float                # page width in points (used later for rendering)
    height: float               # page height in points


def read_pdf_pages(pdf_path: Path) -> List[PageContent]:
    """
    Open a PDF and extract raw text for every page.

    Args:
        pdf_path: path to the PDF file on disk.

    Returns:
        A list of PageContent, one per page, in page order.

    Raises:
        FileNotFoundError: if pdf_path doesn't exist.
        ValueError: if the file can't be opened as a PDF (corrupt/wrong format).
    """
    if not pdf_path.exists():
        logger.error("PDF not found: %s", pdf_path)
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:  # PyMuPDF raises its own exception types
        logger.error("Failed to open PDF %s: %s", pdf_path, exc)
        raise ValueError(f"Could not open '{pdf_path}' as a PDF: {exc}") from exc

    pages: List[PageContent] = []

    for index, page in enumerate(doc):
        text = page.get_text("text").strip()
        needs_ocr = len(text) < MIN_CHARS_PER_PAGE

        pages.append(
            PageContent(
                page_number=index + 1,
                raw_text=text,
                needs_ocr=needs_ocr,
                width=page.rect.width,
                height=page.rect.height,
            )
        )

        if needs_ocr:
            logger.info("Page %d of %s looks scanned (only %d chars) — will need OCR",
                        index + 1, pdf_path.name, len(text))

    doc.close()
    logger.info("Extracted %d pages from %s", len(pages), pdf_path.name)
    return pages


def render_page_to_image(pdf_path: Path, page_number: int, dpi: int = 300):
    """
    Render a single PDF page to a PIL Image, for pages that need OCR.

    Args:
        pdf_path: path to the PDF file.
        page_number: 1-indexed page number (matches PageContent.page_number).
        dpi: resolution to render at. 300 is the sweet spot for Tesseract
             accuracy vs. speed — going higher rarely improves OCR quality
             but slows things down a lot.

    Returns:
        A PIL.Image.Image object of the rendered page.
    """
    from PIL import Image
    import io

    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]

    zoom = dpi / 72  # PDF points are 72 per inch
    matrix = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=matrix)

    image = Image.open(io.BytesIO(pixmap.tobytes("png")))
    doc.close()
    return image
