"""
mcp_server.py
=============
Model Context Protocol (MCP) server for the AI Policy Advisor.
Exposes tools to ingest, analyze, query, and list policies.
"""

import os
from pathlib import Path

# Try to import FastMCP from either package layout
try:
    from fastmcp import FastMCP
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        raise ImportError(
            "Could not import FastMCP. Make sure the 'mcp' or 'fastmcp' package is installed."
        )

from config import settings
from api.services import ingest_uploaded_file, analyze_document, answer_question
from utils.constants import POLICY_CATEGORIES
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize FastMCP Server
mcp = FastMCP("AI Policy Advisor")


@mcp.tool()
def ingest_policy(pdf_path: str, category: str = "uncategorized") -> str:
    """
    Ingest a PDF policy document into the RAG vector database.

    Args:
        pdf_path: The absolute or relative path to the PDF policy document.
        category: The category of the policy (e.g. education, healthcare, environment, agriculture, cybersecurity, hr, college, government).

    Returns:
        Confirmation message with the generated doc_id.
    """
    if category not in POLICY_CATEGORIES:
        return f"Error: Category must be one of {POLICY_CATEGORIES}."

    path = Path(pdf_path)
    if not path.is_absolute():
        path = Path(os.getcwd()) / path

    if not path.exists() or not path.is_file():
        return f"Error: File not found at path '{path}'."

    if not path.name.lower().endswith(".pdf"):
        return "Error: Only PDF files are supported."

    # Make a copy in the uploads folder
    dest = settings.upload_dir / path.name
    try:
        import shutil
        if path.resolve() != dest.resolve():
            shutil.copy2(path, dest)
    except Exception as e:
        return f"Error copying PDF to upload directory: {e}"

    try:
        doc_id = ingest_uploaded_file(dest, category)
        return f"Successfully ingested '{path.name}'. Generated Doc ID: {doc_id}. You can now run analyze_policy with this Doc ID."
    except Exception as e:
        logger.error("MCP ingest_policy failed: %s", e)
        return f"Error during ingestion pipeline: {e}"


@mcp.tool()
def analyze_policy(doc_id: str, category: str, topic_hint: str = "") -> str:
    """
    Run the full 10-agent CrewAI crew analysis on an ingested document.

    Args:
        doc_id: The document ID (returned from ingestion).
        category: The category of the policy.
        topic_hint: Optional topic hint for external government circular searches.

    Returns:
        The analysis report summary and report file path.
    """
    if category not in POLICY_CATEGORIES:
        return f"Error: Category must be one of {POLICY_CATEGORIES}."

    # Check if report directory exists
    settings.ensure_directories()

    try:
        logger.info("MCP analyze_policy starting for doc_id=%s...", doc_id)
        results = analyze_document(doc_id, category, topic_hint)
        report_path = results.get("report_path", "")

        output = f"=== ANALYSIS COMPLETE FOR DOC ID: {doc_id} ===\n"
        output += f"Report Saved to: {report_path}\n\n"
        output += "--- EXECUTIVE SUMMARY ---\n"
        output += results.get("summary", "No summary generated.") + "\n\n"
        output += "--- KEY RECOMMENDATIONS ---\n"
        output += results.get("recommendations", "No recommendations generated.") + "\n"

        return output
    except Exception as e:
        logger.error("MCP analyze_policy failed for doc_id=%s: %s", doc_id, e)
        return f"Error during CrewAI analysis execution: {e}"


@mcp.tool()
def query_policy(doc_id: str, query: str) -> str:
    """
    Query the ingested policy document using RAG (Retrieval-Augmented Generation) for quick answers.

    Args:
        doc_id: The document ID of the policy to query.
        query: The question or query search term.

    Returns:
        The text answer generated from document context, along with source chunk indexes.
    """
    try:
        result = answer_question(doc_id, query)
        answer = result.get("answer", "")
        sources = result.get("sources", [])

        output = f"Answer:\n{answer}\n\nSources (Chunk Indexes): {sources}"
        return output
    except Exception as e:
        logger.error("MCP query_policy failed for doc_id=%s: %s", doc_id, e)
        return f"Error querying policy document: {e}"


@mcp.tool()
def list_policies() -> str:
    """
    List all ingested policy documents in the Chroma vector database, uploaded files, and reports.

    Returns:
        A list of policy document IDs, upload file names, and generated PDF report paths.
    """
    settings.ensure_directories()

    # Retrieve unique doc_ids from ChromaDB
    unique_docs = {}
    try:
        from rag.vectordb import _get_collection
        collection = _get_collection()
        # Fetch metadatas to find unique doc_ids
        data = collection.get(include=["metadatas"])
        if data and data.get("metadatas"):
            for meta in data["metadatas"]:
                doc_id = meta.get("doc_id")
                category = meta.get("category")
                if doc_id:
                    unique_docs[doc_id] = category
    except Exception as e:
        logger.warning("Could not read from ChromaDB: %s", e)
        unique_docs = {"ChromaDB Error": str(e)}

    # Read from folders
    uploads = [f.name for f in settings.upload_dir.glob("*.pdf")]
    reports = [f.name for f in settings.reports_dir.glob("*.pdf")]

    output = "=== INGESTED DOCUMENTS (ChromaDB) ===\n"
    if unique_docs:
        for doc_id, cat in unique_docs.items():
            output += f"- Doc ID: {doc_id} (Category: {cat})\n"
    else:
        output += "No documents found in ChromaDB.\n"

    output += "\n=== UPLOADED PDFs ===\n"
    if uploads:
        for u in uploads:
            output += f"- {u}\n"
    else:
        output += "No uploads.\n"

    output += "\n=== GENERATED PDF REPORTS ===\n"
    if reports:
        for r in reports:
            output += f"- {r}\n"
    else:
        output += "No reports.\n"

    return output


if __name__ == "__main__":
    logger.info("Starting AI Policy Advisor MCP Server...")
    mcp.run()
