"""tests/test_report_builder.py — verifies the PDF report builder produces a valid, non-empty PDF."""

from pathlib import Path

from tools.report_builder import build_pdf_report


def test_build_pdf_report_creates_file(tmp_path):
    sections = {
        "reader": "Document Type: Circular\nIssuing Authority: Test Ministry",
        "summary": "This is a test summary.",
        "impact": "Students: affected positively.",
    }
    output = tmp_path / "test_report.pdf"
    result_path = build_pdf_report("test_doc.pdf", sections, output)

    assert result_path.exists()
    assert result_path.stat().st_size > 1000  # a real PDF, not an empty stub
    assert result_path.read_bytes()[:4] == b"%PDF"  # valid PDF file signature


def test_build_pdf_report_skips_missing_sections(tmp_path):
    output = tmp_path / "partial_report.pdf"
    result_path = build_pdf_report("test_doc.pdf", {"summary": "Only summary present."}, output)
    assert result_path.exists()
