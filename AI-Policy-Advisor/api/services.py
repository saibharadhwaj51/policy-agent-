"""api/services.py — business logic layer between FastAPI routes and the RAG/agent core."""

from pathlib import Path

from config import settings
from rag.pipeline import ingest_document
from rag.retriever import retrieve_context, build_context_string
from agents.orchestrator import run_full_analysis
from tools.report_builder import build_pdf_report
from utils.llm import ask_gemini
from utils.logger import get_logger

logger = get_logger(__name__)


def ingest_uploaded_file(file_path: Path, category: str) -> str:
    return ingest_document(file_path, category=category)


def analyze_document(doc_id: str, category: str, topic_hint: str = "") -> dict:
    results = run_full_analysis(doc_id, category, topic_hint)

    report_path = settings.reports_dir / f"{doc_id}_report.pdf"
    build_pdf_report(doc_id, results, report_path)
    results["report_path"] = str(report_path)
    return results


def answer_question(doc_id: str, question: str) -> dict:
    """Direct RAG Q&A outside the full agent crew — for quick follow-up questions."""
    matches = retrieve_context(question, doc_id=doc_id, top_k=5)
    context = build_context_string(matches)
    prompt = (
        f"Answer the question using ONLY the context below. If the answer isn't "
        f"in the context, say so.\n\nCONTEXT:\n{context}\n\nQUESTION: {question}"
    )
    answer = ask_gemini(prompt)
    return {"answer": answer, "sources": [m["chunk_index"] for m in matches]}
