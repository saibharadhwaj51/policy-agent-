"""
app.py
=======
FastAPI application entry point (Phase 10).

Run with:  uvicorn app:app --host 0.0.0.0 --port 8000 --reload
Swagger UI available at:  http://localhost:8000/docs
"""

import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config import settings
from automation.watcher import start_watcher_loop
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="AI Policy Advisor API",
    description="Upload policy PDFs and get RAG + multi-agent analysis: summaries, "
                "comparisons, impact analysis, recommendations, FAQs, and timelines.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in real production deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    logger.info("AI Policy Advisor API starting on %s:%s", settings.api_host, settings.api_port)
    if settings.start_watcher:
        logger.info("Starting background automation watcher thread...")
        t = threading.Thread(target=start_watcher_loop, args=(10,), daemon=True)
        t.start()


@app.get("/")
def root():
    return {"message": "AI Policy Advisor API is running. See /docs for Swagger UI."}
