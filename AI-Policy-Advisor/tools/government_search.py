"""
tools/government_search.py
=============================
CrewAI tool that lets the Government Search Agent look up official
circulars/notifications on the open web, for context not present in the
internal vector DB.

Uses a plain requests + DuckDuckGo HTML search (no API key required) so
this works out of the box. Swap in a paid search API later (Phase-level
improvement) for higher-quality results if needed.
"""

import requests
from bs4 import BeautifulSoup

from crewai.tools import tool
from utils.logger import get_logger

logger = get_logger(__name__)

SEARCH_URL = "https://html.duckduckgo.com/html/"
HEADERS = {"User-Agent": "Mozilla/5.0 (AI-Policy-Advisor research bot)"}


@tool("Search Government Circulars Online")
def search_government_sources(query: str, max_results: int = 5) -> str:
    """
    Search the open web for official government circulars/notifications
    related to `query`.

    Args:
        query: search terms, e.g. "Ministry of Education digital literacy circular 2026".
        max_results: how many results to return.

    Returns:
        A formatted string of "Title - URL - snippet" per result, or a
        message indicating no results / a network failure.
    """
    try:
        response = requests.post(
            SEARCH_URL, data={"q": query}, headers=HEADERS, timeout=10
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Government web search failed: %s", exc)
        return f"Web search unavailable ({exc}). Rely on internal document context only."

    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for result in soup.select(".result")[:max_results]:
        title_el = result.select_one(".result__title")
        snippet_el = result.select_one(".result__snippet")
        link_el = result.select_one(".result__url")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        url = link_el.get_text(strip=True) if link_el else ""
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
        results.append(f"- {title}\n  {url}\n  {snippet}")

    if not results:
        return "No government search results found for this query."

    return "\n".join(results)
