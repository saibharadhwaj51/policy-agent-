"""
rag/pipeline.py
=================
The single entry point that ties Phases 2-4 together:

    PDF -> parse -> clean -> chunk -> embed -> store in ChromaDB

Everything downstream (agents, API, dashboard) calls `ingest_document()`
once per uploaded file, then uses `rag/retriever.py` to ask questions.
"""

from pathlib import Path
from typing import Optional

from rag.parser import parse_pdf
from rag.cleaner import clean_document_pages
from rag.chunker import chunk_text
from rag.embeddings import embed_texts
from rag.vectordb import store_chunks
from utils.helpers import generate_doc_id
from utils.logger import get_logger

logger = get_logger(__name__)


def ingest_document(pdf_path: Path, category: str = "uncategorized") -> str:
    """
    Full ingestion pipeline for one PDF.

    Args:
        pdf_path: path to the uploaded PDF.
        category: one of utils.constants.POLICY_CATEGORIES.

    Returns:
        doc_id — use this to query/retrieve this document later.
    """
    pdf_path = Path(pdf_path)
    doc_id = generate_doc_id(pdf_path)
    logger.info("Ingesting %s as doc_id=%s (category=%s)", pdf_path.name, doc_id, category)

    parsed = parse_pdf(pdf_path)
    cleaned_pages = clean_document_pages([p.text for p in parsed.pages])
    full_clean_text = "\n\n".join(cleaned_pages)

    chunks = chunk_text(full_clean_text, doc_id=doc_id)
    if not chunks:
        logger.warning("No chunks produced for %s — document may be empty", pdf_path.name)
        return doc_id

    embeddings = embed_texts([c.text for c in chunks])
    store_chunks(chunks, embeddings, category=category)

    logger.info("Ingestion complete for doc_id=%s: %d chunks stored", doc_id, len(chunks))
    return doc_id
