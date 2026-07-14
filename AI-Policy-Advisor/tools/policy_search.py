"""
tools/policy_search.py
========================
CrewAI tool that lets the Comparison Agent search the internal vector DB
for a PREVIOUS version of a policy, scoped by category, so it can compare
old vs new even when the user only uploaded the new document.
"""

from crewai.tools import tool

from rag.retriever import retrieve_context, build_context_string


@tool("Search Previous Policy Versions")
def search_previous_policy(topic: str, category: str, exclude_doc_id: str = "") -> str:
    """
    Search previously ingested documents in the given policy category for
    content related to `topic`, excluding the current document itself.

    Args:
        topic: what to search for, e.g. "digital literacy education policy".
        category: one of the POLICY_CATEGORIES (education, healthcare, ...).
        exclude_doc_id: doc_id of the currently-analyzed document, so we
                        don't just match it against itself.
    """
    matches = retrieve_context(topic, category=category, top_k=5)
    matches = [m for m in matches if m["doc_id"] != exclude_doc_id]

    if not matches:
        return "No related previous policy found in the internal database for this category."

    return build_context_string(matches)
