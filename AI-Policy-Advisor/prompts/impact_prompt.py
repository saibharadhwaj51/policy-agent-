"""Prompt template for the Impact Analysis Agent."""

IMPACT_PROMPT = """Analyze the impact of the following policy on each stakeholder group.

DOCUMENT CONTENT:
{context}

For each relevant stakeholder group present in {stakeholders}, provide:
- How they are affected
- Pros (bullet list)
- Cons (bullet list)

Then provide an overall:
## Risk Analysis
(bullet list of risks, each tagged Low/Medium/High)

## Overall Benefits vs Drawbacks
(short balanced paragraph)
"""
