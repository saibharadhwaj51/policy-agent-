"""agents/impact_agent.py — Agent 4/10 — Impact Analysis Agent."""

from crewai import Agent, Task

from utils.llm import crewai_model_string
from prompts.impact_prompt import IMPACT_PROMPT


def build_impact_agent() -> Agent:
    return Agent(
        role="Stakeholder Impact Analyst",
        goal="Assess how this policy affects every relevant stakeholder group, balancing "
             "pros, cons, and risk level honestly -- never one-sided.",
        backstory="You are a public policy researcher who has authored impact assessments "
                   "for national ministries, trained to consider unintended consequences.",
        llm=crewai_model_string(),
        verbose=True,
        allow_delegation=False,
    )


def build_impact_task(agent: Agent, context: str, stakeholders: str) -> Task:
    return Task(
        description=IMPACT_PROMPT.format(context=context, stakeholders=stakeholders),
        expected_output="Per-stakeholder impact breakdown, a Risk Analysis section, and an "
                         "Overall Benefits vs Drawbacks paragraph.",
        agent=agent,
    )
