"""
tools/report_builder.py
=========================
Builds the final downloadable PDF report from the orchestrator's results
dict, using ReportLab. This is deterministic Python (not an LLM call) --
the Report Generator Agent's LLM task only polishes text; THIS function
lays it out as an actual PDF.
"""

from pathlib import Path
from typing import Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
)

from utils.logger import get_logger

logger = get_logger(__name__)

SECTION_ORDER = [
    ("reader", "Document Overview"),
    ("summary", "Executive Summary"),
    ("comparison", "Comparison with Previous Policy"),
    ("impact", "Impact Analysis"),
    ("recommendations", "Recommendations & Action Items"),
    ("timeline", "Policy Timeline"),
    ("government_findings", "Related Government Sources"),
    ("faqs", "Frequently Asked Questions"),
]


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="SectionHeading", fontSize=16, spaceAfter=12, spaceBefore=18,
        textColor=colors.HexColor("#1a3c6e"), fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="ReportTitle", fontSize=24, spaceAfter=6,
        textColor=colors.HexColor("#0d2340"), fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="ReportBody", fontSize=10.5, leading=15, spaceAfter=8,
    ))
    return styles


def _text_to_paragraphs(text: str, styles) -> list:
    """Split agent output text into paragraphs, safely escaping for ReportLab."""
    flow = []
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        safe = (block.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        safe = safe.replace("\n", "<br/>")
        flow.append(Paragraph(safe, styles["ReportBody"]))
        flow.append(Spacer(1, 4))
    return flow


def build_pdf_report(
    doc_title: str,
    sections: Dict[str, str],
    output_path: Path,
) -> Path:
    """
    Build the final PDF report.

    Args:
        doc_title: title shown on the cover, e.g. the source PDF's filename.
        sections: dict keyed by the keys in SECTION_ORDER (missing keys are skipped).
        output_path: where to write the PDF.

    Returns:
        The output_path, for convenience.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = _styles()

    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
        topMargin=1 * inch, bottomMargin=0.9 * inch,
    )

    story = []
    story.append(Paragraph("AI Policy Advisor", styles["ReportTitle"]))
    story.append(Paragraph(f"Analysis Report: {doc_title}", styles["SectionHeading"]))
    story.append(Spacer(1, 20))

    for key, heading in SECTION_ORDER:
        content = sections.get(key)
        if not content:
            continue
        story.append(Paragraph(heading, styles["SectionHeading"]))
        story.extend(_text_to_paragraphs(content, styles))
        story.append(Spacer(1, 10))

    doc.build(story)
    logger.info("Built PDF report at %s", output_path)
    return output_path
