"""
agents/report_agent.py — Agent 9/10 — Report Generator Agent.

Unlike the other agents, this one's real work is NOT an LLM call -- it's
assembling every other agent's output into a downloadable PDF. The LLM
task (light editing/formatting) is optional and best-effort; the PDF
build itself (tools/report_builder.py) is deterministic Python.
"""

from crewai import Agent, Task

from utils.llm import crewai_model_string
from prompts.report_prompt import REPORT_ASSEMBLY_PROMPT


def build_report_agent() -> Agent:
    return Agent(
        role="Report Assembly Editor",
        goal="Combine all specialist analyses into one coherent, well-formatted final report "
             "without introducing new claims or losing information.",
        backstory="You are a technical editor who finalizes multi-author government reports "
                   "before publication, ensuring consistent tone without altering facts.",
        llm=crewai_model_string(),
        verbose=True,
        allow_delegation=False,
    )


def build_report_task(agent: Agent, sections: dict) -> Task:
    return Task(
        description=REPORT_ASSEMBLY_PROMPT.format(
            summary=sections.get("summary", ""),
            comparison=sections.get("comparison", ""),
            impact=sections.get("impact", ""),
            recommendations=sections.get("recommendations", ""),
            faqs=sections.get("faqs", ""),
            timeline=sections.get("timeline", ""),
        ),
        expected_output="Polished final text for each section, same order, ready for the PDF report.",
        agent=agent,
    )
