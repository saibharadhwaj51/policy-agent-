"""agents/summary_agent.py — Agent 2/10 — Summary Agent (2-line/10-line/detailed summaries)."""

from crewai import Agent, Task

from utils.llm import crewai_model_string
from prompts.summary_prompt import SUMMARY_PROMPT


def build_summary_agent() -> Agent:
    return Agent(
        role="Policy Summarization Specialist",
        goal="Produce clear, accurate summaries at three levels of detail so any reader "
             "-- from a busy executive to a detail-oriented compliance officer -- gets what they need.",
        backstory="You are a policy communications expert who has spent years translating "
                   "dense government language into plain English without losing accuracy.",
        llm=crewai_model_string(),
        verbose=True,
        allow_delegation=False,
    )


def build_summary_task(agent: Agent, context: str) -> Task:
    return Task(
        description=SUMMARY_PROMPT.format(context=context),
        expected_output="Three clearly headed sections: 2-Line Summary, 10-Line Summary, Detailed Summary.",
        agent=agent,
    )
