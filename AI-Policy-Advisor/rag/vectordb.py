"""
rag/vectordb.py
=================
Wraps ChromaDB — the vector database that stores chunk embeddings and
lets us retrieve the most semantically relevant chunks for a query.

WHY A VECTOR DATABASE (vs. just a Python list + cosine similarity loop):
a naive loop is O(n) per query and re-embeds nothing — fine for a demo,
but ChromaDB adds persistence (survives restarts), metadata filtering
(e.g. "only search chunks from doc_id=X" or "only healthcare policies"),
and approximate-nearest-neighbor indexing that stays fast as the
document count grows into the thousands.

We use ONE persistent collection for the whole app and rely on metadata
(doc_id, category) to scope queries to a specific document or policy
category — simpler to operate than one collection per document.
"""

from typing import Dict, List, Optional

from config import settings
from rag.chunker import Chunk
from utils.logger import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "policy_documents"


def _get_client():
    import chromadb
    return chromadb.PersistentClient(path=str(settings.chroma_db_path))


def _get_collection():
    client = _get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def store_chunks(chunks: List[Chunk], embeddings, category: str = "uncategorized") -> None:
    """
    Store a document's chunks + their embeddings in ChromaDB.

    Args:
        chunks: list of Chunk objects (from rag/chunker.py).
        embeddings: numpy array aligned 1:1 with `chunks`.
        category: policy category (education, healthcare, ...) stored as
                  metadata so the Government Search / comparison agents
                  can filter by category later.
    """
    if not chunks:
        logger.warning("store_chunks called with no chunks — nothing to store")
        return

    collection = _get_collection()
    collection.upsert(
        ids=[c.chunk_id for c in chunks],
        embeddings=[e.tolist() for e in embeddings],
        documents=[c.text for c in chunks],
        metadatas=[
            {"doc_id": c.doc_id, "chunk_index": c.chunk_index, "category": category}
            for c in chunks
        ],
    )
    logger.info("Stored %d chunks for doc_id=%s (category=%s)",
                len(chunks), chunks[0].doc_id, category)


def query_similar(
    query_embedding,
    top_k: int = 5,
    doc_id: Optional[str] = None,
    category: Optional[str] = None,
) -> List[Dict]:
    """
    Retrieve the top_k most similar chunks to a query embedding.

    Args:
        query_embedding: embedding vector for the user's question.
        top_k: how many chunks to return.
        doc_id: if set, restrict search to this document only.
        category: if set, restrict search to this policy category only
                  (used by the Comparison/Government Search agents to find
                  related prior policies).

    Returns:
        List of dicts: {text, doc_id, chunk_index, distance}.
    """
    collection = _get_collection()

    where_filter = {}
    if doc_id:
        where_filter["doc_id"] = doc_id
    if category:
        where_filter["category"] = category

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
        where=where_filter or None,
    )

    matches = []
    for i in range(len(results["ids"][0])):
        matches.append({
            "text": results["documents"][0][i],
            "doc_id": results["metadatas"][0][i]["doc_id"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance": results["distances"][0][i],
        })

    logger.info("Retrieved %d matches for query (doc_id=%s, category=%s)",
                len(matches), doc_id, category)
    return matches


def delete_document(doc_id: str) -> None:
    """Remove all chunks belonging to a document (e.g. on re-upload)."""
    collection = _get_collection()
    collection.delete(where={"doc_id": doc_id})
    logger.info("Deleted all chunks for doc_id=%s", doc_id)
