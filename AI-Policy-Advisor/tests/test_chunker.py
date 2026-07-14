"""tests/test_chunker.py — verifies chunking logic, sizes, and overlap."""

from rag.chunker import chunk_text


def test_chunk_text_basic_split():
    text = " ".join([f"w{i}" for i in range(1000)])
    chunks = chunk_text(text, doc_id="doc1", chunk_size=250, overlap=40)
    assert len(chunks) > 1
    assert all(c.doc_id == "doc1" for c in chunks)
    assert chunks[0].word_count == 250


def test_chunk_text_overlap_is_correct():
    text = " ".join([f"w{i}" for i in range(600)])
    chunks = chunk_text(text, doc_id="doc1", chunk_size=250, overlap=40)
    last_words_chunk0 = chunks[0].text.split()[-40:]
    first_words_chunk1 = chunks[1].text.split()[:40]
    assert last_words_chunk0 == first_words_chunk1


def test_chunk_text_empty_input_returns_empty_list():
    assert chunk_text("", doc_id="doc1") == []


def test_chunk_text_rejects_overlap_ge_chunk_size():
    import pytest
    with pytest.raises(ValueError):
        chunk_text("some text here", doc_id="doc1", chunk_size=10, overlap=10)
