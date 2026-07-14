"""agents/recommendation_agent.py — Agent 5/10 — Recommendation Agent."""

from crewai import Agent, Task

from utils.llm import crewai_model_string
from prompts.recommendation_prompt import RECOMMENDATION_PROMPT


def build_recommendation_agent() -> Agent:
    return Agent(
        role="Policy Implementation Advisor",
        goal="Turn analysis into concrete, actionable guidance that an organization can "
             "actually execute -- specific, prioritized, and realistic.",
        backstory="You are a management consultant specializing in regulatory compliance "
                   "rollouts, known for turning dense policy into simple checklists.",
        llm=crewai_model_string(),
        verbose=True,
        allow_delegation=False,
    )


def build_recommendation_task(agent: Agent, context: str, impact_analysis: str) -> Task:
    return Task(
        description=RECOMMENDATION_PROMPT.format(context=context, impact_analysis=impact_analysis),
        expected_output="Recommendations, Best Practices, Action Items, and Compliance Checklist sections.",
        agent=agent,
    )
