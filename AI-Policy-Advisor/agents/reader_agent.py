"""
agents/reader_agent.py
========================
Agent 1/10 — Reader Agent.

Role: first agent in the crew. Takes retrieved chunks for the uploaded
document and produces a structured breakdown (doc type, authority,
subject, effective date, key clauses) that every other agent builds on.
"""

from crewai import Agent, Task

from utils.llm import crewai_model_string
from prompts.reader_prompt import READER_PROMPT


def build_reader_agent() -> Agent:
    return Agent(
        role="Policy Document Reader",
        goal="Accurately extract and structure the core facts of a policy document "
             "without adding interpretation or opinion.",
        backstory=(
            "You are a meticulous government records analyst with 15 years of experience "
            "reading circulars, notifications, and institutional policies. You never guess — "
            "if a fact isn't in the text, you say so."
        ),
        llm=crewai_model_string(),
        verbose=True,
        allow_delegation=False,
    )


def build_reader_task(agent: Agent, context: str) -> Task:
    return Task(
        description=READER_PROMPT.format(context=context),
        expected_output="A structured breakdown with headers: Document Type, Issuing "
                         "Authority, Subject/Title, Effective Date, Key Clauses.",
        agent=agent,
    )
