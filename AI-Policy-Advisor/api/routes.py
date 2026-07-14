"""api/routes.py — FastAPI endpoints for the AI Policy Advisor."""

import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from config import settings
from api.schemas import (
    AnalyzeRequest, AnalyzeResponse, IngestResponse, QuestionRequest, QuestionResponse,
)
from api.services import ingest_uploaded_file, analyze_document, answer_question
from utils.constants import POLICY_CATEGORIES
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/categories")
def list_categories():
    return {"categories": POLICY_CATEGORIES}


@router.post("/upload", response_model=IngestResponse)
async def upload_pdf(file: UploadFile = File(...), category: str = "uncategorized"):
    if category not in POLICY_CATEGORIES:
        raise HTTPException(400, f"category must be one of {POLICY_CATEGORIES}")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    dest = settings.upload_dir / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        doc_id = ingest_uploaded_file(dest, category)
    except Exception as exc:
        logger.error("Ingestion failed for %s: %s", file.filename, exc)
        raise HTTPException(500, f"Failed to process PDF: {exc}") from exc

    return IngestResponse(
        doc_id=doc_id, file_name=file.filename, category=category,
        message="Document ingested successfully. Call /analyze next.",
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    try:
        results = analyze_document(request.doc_id, request.category, request.topic_hint)
    except Exception as exc:
        logger.error("Analysis failed for doc_id=%s: %s", request.doc_id, exc)
        raise HTTPException(500, f"Analysis failed: {exc}") from exc

    return AnalyzeResponse(doc_id=request.doc_id, **{
        k: v for k, v in results.items() if k != "report_path"
    })


@router.post("/ask", response_model=QuestionResponse)
async def ask(request: QuestionRequest):
    result = answer_question(request.doc_id, request.question)
    return QuestionResponse(**result)


@router.get("/report/{doc_id}")
async def download_report(doc_id: str):
    report_path = settings.reports_dir / f"{doc_id}_report.pdf"
    if not report_path.exists():
        raise HTTPException(404, "Report not found. Run /analyze first.")
    return FileResponse(report_path, media_type="application/pdf", filename=report_path.name)
