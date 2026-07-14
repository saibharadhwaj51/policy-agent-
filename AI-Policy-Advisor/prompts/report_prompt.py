"""Prompt template for the Report Generator Agent — final assembly instructions."""

REPORT_ASSEMBLY_PROMPT = """You are assembling a final policy analysis report from the sections
below, produced by specialist agents. Do not invent new content — only
lightly edit for consistent tone and remove duplication between sections.

SUMMARY:
{summary}

COMPARISON:
{comparison}

IMPACT ANALYSIS:
{impact}

RECOMMENDATIONS:
{recommendations}

FAQS:
{faqs}

TIMELINE:
{timeline}

Return the polished final text for each section, in the same order, ready
to be placed into a PDF report.
"""
