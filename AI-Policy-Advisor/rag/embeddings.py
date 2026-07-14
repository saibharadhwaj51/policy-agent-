"""
rag/embeddings.py
===================
Converts text chunks into vector embeddings using Sentence Transformers.

WHY THIS FILE EXISTS
---------------------
An embedding is a list of numbers (a vector) that represents the MEANING
of a piece of text, positioned in high-dimensional space such that
semantically similar text ends up close together. "school funding cut"
and "reduced education budget" land near each other even though they
share almost no words — that's what makes semantic search possible
(as opposed to plain keyword matching).

We use `all-MiniLM-L6-v2` by default: it's small (~80MB), fast on CPU,
and produces 384-dimensional vectors — a strong accuracy/speed tradeoff
for a self-hosted RAG pipeline that doesn't need a GPU.

The model is loaded ONCE (module-level singleton) because loading it is
slow (~1-2s) — we don't want to pay that cost on every chunk.
"""

from functools import lru_cache
from typing import List

import numpy as np

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _get_model():
    """Load and cache the SentenceTransformer model (only happens once per process)."""
    from sentence_transformers import SentenceTransformer
    logger.info("Loading embedding model: %s", settings.embedding_model)
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Embed a batch of texts into vectors.

    Args:
        texts: list of strings (e.g. chunk texts).

    Returns:
        numpy array of shape (len(texts), embedding_dim).
    """
    if not texts:
        return np.array([])

    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    logger.info("Embedded %d texts -> shape %s", len(texts), embeddings.shape)
    return embeddings


def embed_query(query: str) -> np.ndarray:
    """Embed a single query string (e.g. the user's question)."""
    return embed_texts([query])[0]


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors — used mainly for
    teaching/debugging; ChromaDB does this internally at scale in Phase 4.
    """
    denom = (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    if denom == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)
