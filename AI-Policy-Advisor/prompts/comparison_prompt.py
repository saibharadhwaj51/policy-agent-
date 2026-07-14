"""Prompt template for the Comparison Agent — old vs new policy diff."""

COMPARISON_PROMPT = """Compare the NEW policy against the PREVIOUS policy below.

PREVIOUS POLICY CONTENT:
{previous_context}

NEW POLICY CONTENT:
{new_context}

Return a markdown table with columns: Clause Area | Previous Policy | New Policy | Change Type (Added/Removed/Modified/Unchanged).
After the table, add a short "Summary of Changes" paragraph.
If no previous policy content was provided, state clearly that no prior
version was found and summarize the new policy's key provisions instead.
"""
