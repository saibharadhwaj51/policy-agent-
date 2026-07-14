"""api/schemas.py — Pydantic request/response models for the FastAPI layer."""

from typing import Optional

from pydantic import BaseModel


class IngestResponse(BaseModel):
    doc_id: str
    file_name: str
    category: str
    message: str


class AnalyzeRequest(BaseModel):
    doc_id: str
    category: str
    topic_hint: Optional[str] = ""


class AnalyzeResponse(BaseModel):
    doc_id: str
    reader: str
    summary: str
    comparison: str
    impact: str
    recommendations: str
    timeline: str
    faqs: str
    government_findings: str
    final_report: str


class QuestionRequest(BaseModel):
    doc_id: str
    question: str


class QuestionResponse(BaseModel):
    answer: str
    sources: list
