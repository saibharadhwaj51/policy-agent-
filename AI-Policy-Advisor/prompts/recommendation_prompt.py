"""Prompt template for the Recommendation Agent."""

RECOMMENDATION_PROMPT = """Based on the policy content and impact analysis below, generate actionable guidance.

DOCUMENT CONTENT:
{context}

IMPACT ANALYSIS:
{impact_analysis}

Return these sections:
## Recommendations
(numbered list, most important first)

## Best Practices
(bullet list for implementing organizations)

## Action Items
(checklist format: "- [ ] action item")

## Compliance Checklist
(checklist format: "- [ ] requirement")
"""
