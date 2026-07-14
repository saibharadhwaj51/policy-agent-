"""Prompt templates for the Summary Agent — 2-line, 10-line, and detailed summaries."""

SUMMARY_PROMPT = """Based on the following policy document content, produce three summaries.

DOCUMENT CONTENT:
{context}

Return exactly these three sections:

## 2-Line Summary
(Maximum 2 sentences, capturing only the single most important point.)

## 10-Line Summary
(Up to 10 lines, covering purpose, key changes, and effective date.)

## Detailed Summary
(3-5 paragraphs covering purpose, scope, key provisions, and stakeholders affected.)
"""
