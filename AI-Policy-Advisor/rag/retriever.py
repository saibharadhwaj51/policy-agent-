"""
rag/retriever.py
==================
High-level retrieval API — the ONLY file agents/tools should import for
"give me relevant context for this question." Hides embeddings + vectordb
plumbing behind one function.
"""

from typing import Dict, List, Optional

from rag.embeddings import embed_query
from rag.vectordb import query_similar
from utils.logger import get_logger

logger = get_logger(__name__)


def retrieve_context(
    question: str,
    doc_id: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = 5,
) -> List[Dict]:
    """
    Retrieve the most relevant chunks for a natural-language question.

    Args:
        question: the user's (or an agent's) question.
        doc_id: restrict to one document, or None to search everything.
        category: restrict to one policy category, or None.
        top_k: number of chunks to retrieve.

    Returns:
        List of {text, doc_id, chunk_index, distance} dicts, most relevant first.
    """
    query_vec = embed_query(question)
    matches = query_similar(query_vec, top_k=top_k, doc_id=doc_id, category=category)
    return matches


def build_context_string(matches: List[Dict], max_chars: int = 6000) -> str:
    """
    Concatenate retrieved chunks into one context string for an LLM prompt,
    capped at max_chars so we don't blow the model's context window.
    """
    parts = []
    total = 0
    for m in matches:
        chunk = f"[Source chunk {m['chunk_index']} of {m['doc_id']}]\n{m['text']}\n"
        if total + len(chunk) > max_chars:
            break
        parts.append(chunk)
        total += len(chunk)
    return "\n".join(parts)
