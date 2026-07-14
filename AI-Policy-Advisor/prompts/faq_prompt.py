"""Prompt template for the FAQ Agent."""

FAQ_PROMPT = """Based on the policy document below, generate a Frequently Asked Questions list
that a typical affected stakeholder (student, employee, citizen, etc.) would ask.

DOCUMENT CONTENT:
{context}

Return 6-10 Q&A pairs in this format:
**Q: <question>**
A: <answer, grounded only in the document content above>
"""
