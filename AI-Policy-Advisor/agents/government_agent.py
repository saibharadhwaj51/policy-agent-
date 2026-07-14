"""agents/government_agent.py — Agent 8/10 — Government Search Agent."""

from crewai import Agent, Task

from utils.llm import crewai_model_string
from prompts.government_prompt import GOVERNMENT_SEARCH_PROMPT
from tools.government_search import search_government_sources


def build_government_agent() -> Agent:
    return Agent(
        role="Government Records Researcher",
        goal="Find official prior circulars, notifications, and policy versions related to "
             "the document under analysis, using web search, and report only genuinely relevant findings.",
        backstory="You are a research librarian specializing in government archives, "
                   "skilled at separating genuinely relevant official sources from noise.",
        tools=[search_government_sources],
        llm=crewai_model_string(),
        verbose=True,
        allow_delegation=False,
    )


def build_government_task(agent: Agent, topic: str, search_results: str) -> Task:
    return Task(
        description=GOVERNMENT_SEARCH_PROMPT.format(topic=topic, search_results=search_results),
        expected_output="A short assessment of which search results are genuinely related "
                         "prior policy versions/amendments, with source and date if available.",
        agent=agent,
    )
