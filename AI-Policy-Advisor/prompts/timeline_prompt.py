"""Prompt template for the Timeline Agent."""

TIMELINE_PROMPT = """Build a chronological timeline from the policy content and any related
circulars/amendments found below.

DOCUMENT CONTENT:
{context}

RELATED DOCUMENTS / CIRCULARS FOUND:
{related_context}

Return a markdown table: Date | Event | Description.
Include the original policy's issue date, any amendment dates mentioned,
and the effective date. If exact dates aren't available, use relative
markers (e.g. "Upon issuance", "60 days after issuance") instead of
inventing a specific date.
"""
