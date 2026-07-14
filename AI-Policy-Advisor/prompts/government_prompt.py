"""Prompt template for the Government Search Agent — summarizing external search results."""

GOVERNMENT_SEARCH_PROMPT = """The following are search results for prior versions, circulars, or
notifications related to this policy topic: "{topic}"

SEARCH RESULTS:
{search_results}

Summarize which of these (if any) appear to be genuinely related prior
policy versions or amendments, with their source and approximate date.
If none of the results are clearly relevant, say so plainly rather than
forcing a connection.
"""
