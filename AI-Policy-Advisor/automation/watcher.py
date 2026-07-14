"""
automation/watcher.py
=====================
Poller/Watcher that detects new PDFs in `uploads/auto_ingest`, automatically
ingests them via the RAG pipeline, runs the multi-agent CrewAI analysis,
and archives the processed PDFs.
"""

import shutil
import time
from pathlib import Path
from typing import Optional

from config import settings
from api.services import ingest_uploaded_file, analyze_document
from utils.constants import POLICY_CATEGORIES
from utils.logger import get_logger

logger = get_logger(__name__)


def detect_category_from_filename(filename: str) -> str:
    """
    Attempt to guess the policy category from the file name.
    Matches against POLICY_CATEGORIES (case-insensitive).
    Defaults to 'uncategorized' if no match is found.
    """
    fn_lower = filename.lower()
    for cat in POLICY_CATEGORIES:
        if cat.lower() in fn_lower:
            return cat
    return "uncategorized"


def process_single_file(file_path: Path) -> bool:
    """
    Process a single policy PDF file.
    1. Ingests it to Chroma DB.
    2. Runs the multi-agent analysis to generate reports.
    3. Moves the file to the processed directory on success or failed directory on failure.

    Returns:
        bool: True if processing succeeded, False otherwise.
    """
    logger.info("Automation: Found new file to process: %s", file_path.name)
    category = detect_category_from_filename(file_path.name)
    logger.info("Automation: Detected category '%s' for '%s'", category, file_path.name)

    # Make a copy in the standard upload folder as if it was uploaded via API
    dest_path = settings.upload_dir / file_path.name
    try:
        shutil.copy2(file_path, dest_path)
    except Exception as e:
        logger.error("Automation: Failed to copy %s to upload_dir: %s", file_path.name, e)
        # Move to failed
        move_file_to_archive(file_path, settings.failed_dir)
        return False

    try:
        # Step 1: Ingest document
        logger.info("Automation: Ingesting %s...", file_path.name)
        doc_id = ingest_uploaded_file(dest_path, category)
        logger.info("Automation: Ingestion complete. doc_id = %s", doc_id)

        # Step 2: Run multi-agent analysis
        logger.info("Automation: Running CrewAI analysis for doc_id=%s...", doc_id)
        results = analyze_document(doc_id, category)
        logger.info("Automation: Analysis complete. Report saved to: %s", results.get("report_path"))

        # Step 3: Archive successful run
        move_file_to_archive(file_path, settings.processed_dir)
        logger.info("Automation: Successfully processed and archived %s", file_path.name)
        return True

    except Exception as e:
        logger.error("Automation: Error processing file %s: %s", file_path.name, e, exc_info=True)
        move_file_to_archive(file_path, settings.failed_dir)
        return False


def move_file_to_archive(file_path: Path, archive_dir: Path) -> None:
    """Safe helper to move processed/failed files to archive directory."""
    try:
        if not file_path.exists():
            return
        dest = archive_dir / file_path.name
        # Resolve potential name conflict
        if dest.exists():
            timestamp = int(time.time())
            dest = archive_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        shutil.move(str(file_path), str(dest))
        logger.info("Automation: Moved %s to %s", file_path.name, dest.parent.name)
    except Exception as e:
        logger.error("Automation: Failed to archive %s: %s", file_path.name, e)


def scan_and_process() -> int:
    """
    Scans the auto_ingest directory once for PDFs and processes them.
    Returns:
        int: Number of files processed.
    """
    if not settings.auto_ingest_dir.exists():
        settings.ensure_directories()

    pdf_files = list(settings.auto_ingest_dir.glob("*.pdf"))
    if not pdf_files:
        return 0

    logger.info("Automation: Found %d PDF(s) to process in %s", len(pdf_files), settings.auto_ingest_dir)
    processed_count = 0
    for pdf_file in pdf_files:
        if process_single_file(pdf_file):
            processed_count += 1
    return processed_count


def start_watcher_loop(interval_seconds: int = 10) -> None:
    """Infinite loop that scans and processes policies in a background poller."""
    logger.info("Automation: Starting file watcher loop (interval=%ds, folder=%s)", 
                interval_seconds, settings.auto_ingest_dir.absolute())
    try:
        while True:
            scan_and_process()
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        logger.info("Automation: Watcher loop stopped by keyboard interrupt.")
    except Exception as e:
        logger.critical("Automation: Watcher loop crashed: %s", e, exc_info=True)
