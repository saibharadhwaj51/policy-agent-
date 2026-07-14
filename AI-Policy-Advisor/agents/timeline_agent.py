"""agents/timeline_agent.py — Agent 6/10 — Timeline Agent."""

from crewai import Agent, Task

from utils.llm import crewai_model_string
from prompts.timeline_prompt import TIMELINE_PROMPT


def build_timeline_agent() -> Agent:
    return Agent(
        role="Policy Timeline Historian",
        goal="Reconstruct an accurate chronological timeline of a policy's issuance, "
             "amendments, and effective dates -- never inventing dates that aren't grounded in evidence.",
        backstory="You are an archivist who has spent a career tracing the legislative "
                   "history of regulations from first draft to final amendment.",
        llm=crewai_model_string(),
        verbose=True,
        allow_delegation=False,
    )


def build_timeline_task(agent: Agent, context: str, related_context: str) -> Task:
    return Task(
        description=TIMELINE_PROMPT.format(
            context=context,
            related_context=related_context or "(none found)",
        ),
        expected_output="A markdown Date | Event | Description timeline table.",
        agent=agent,
    )
