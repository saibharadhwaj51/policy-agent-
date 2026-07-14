"""
tools/ocr_reader.py
====================
OCR tool for scanned PDF pages, built on Tesseract OCR via pytesseract.

WHY THIS FILE EXISTS
---------------------
Only pages flagged `needs_ocr=True` by pdf_reader.py ever reach this file.
OCR is slow (hundreds of milliseconds to seconds per page) and imperfect,
so we only pay that cost when we actually have to.

This wraps pytesseract with sensible defaults and error handling so that
one corrupt/unreadable page doesn't crash the whole document pipeline —
it logs the failure and returns an empty string, letting the rest of the
document continue processing.
"""

from PIL import Image
import pytesseract

from utils.logger import get_logger

logger = get_logger(__name__)

# 'eng' = English. Add more language packs later for regional government
# circulars, e.g. "eng+hin" for English + Hindi, once tesseract-ocr-hin
# is installed on the system.
TESSERACT_LANG = "eng"


def ocr_image(image: Image.Image, page_number: int = 0) -> str:
    """
    Run OCR on a single page image and return the extracted text.

    Args:
        image: a PIL Image of the page (from pdf_reader.render_page_to_image).
        page_number: used only for logging context.

    Returns:
        Extracted text, or an empty string if OCR fails for this page.
    """
    try:
        text = pytesseract.image_to_string(image, lang=TESSERACT_LANG)
        logger.info("OCR extracted %d characters from page %d", len(text), page_number)
        return text.strip()
    except pytesseract.TesseractNotFoundError:
        logger.error(
            "Tesseract binary not found on this system. "
            "Install it: https://github.com/tesseract-ocr/tesseract#installing-tesseract"
        )
        raise
    except Exception as exc:
        logger.warning("OCR failed on page %d: %s — returning empty text", page_number, exc)
        return ""
