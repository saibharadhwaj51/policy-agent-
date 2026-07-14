"""Prompt template for the Reader Agent — structured document understanding."""

READER_PROMPT = """You are analyzing a policy document. Below is the retrieved content.

DOCUMENT CONTENT:
{context}

Extract and return a structured breakdown with these exact headers:
- Document Type (e.g. circular, notification, HR policy, act)
- Issuing Authority
- Subject / Title
- Effective Date (if mentioned)
- Key Clauses (bullet list, one line each)

Be factual. Only state what is explicitly present in the content above. If a
field isn't mentioned, write "Not specified" rather than guessing.
"""
