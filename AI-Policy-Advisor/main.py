"""
main.py
=======
CLI entry point for running a full analysis without the dashboard or API --
useful for scripting, testing, or batch-processing multiple documents.

Usage:
    python main.py path/to/policy.pdf --category education --topic "digital literacy"
"""

import argparse
from pathlib import Path

from api.services import ingest_uploaded_file, analyze_document
from utils.constants import POLICY_CATEGORIES
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="AI Policy Advisor — CLI analysis runner")
    parser.add_argument("pdf_path", type=str, help="Path to the policy PDF")
    parser.add_argument("--category", type=str, default="uncategorized", choices=POLICY_CATEGORIES)
    parser.add_argument("--topic", type=str, default="", help="Topic hint for government search")
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        logger.error("File not found: %s", pdf_path)
        return

    logger.info("Ingesting %s ...", pdf_path.name)
    doc_id = ingest_uploaded_file(pdf_path, args.category)

    logger.info("Running full agent analysis for doc_id=%s ...", doc_id)
    results = analyze_document(doc_id, args.category, args.topic)

    print("\n" + "=" * 60)
    print(f"ANALYSIS COMPLETE — doc_id: {doc_id}")
    print("=" * 60)
    print(f"Report saved to: {results['report_path']}")


if __name__ == "__main__":
    main()
