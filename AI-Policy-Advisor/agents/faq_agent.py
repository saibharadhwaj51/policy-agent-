"""agents/faq_agent.py — Agent 7/10 — FAQ Agent."""

from crewai import Agent, Task

from utils.llm import crewai_model_string
from prompts.faq_prompt import FAQ_PROMPT


def build_faq_agent() -> Agent:
    return Agent(
        role="Public Communications FAQ Writer",
        goal="Anticipate the real questions affected people will have about this policy "
             "and answer them clearly, grounded strictly in the document content.",
        backstory="You run the public help-desk for a government ministry and have answered "
                   "thousands of citizen questions about new regulations.",
        llm=crewai_model_string(),
        verbose=True,
        allow_delegation=False,
    )


def build_faq_task(agent: Agent, context: str) -> Task:
    return Task(
        description=FAQ_PROMPT.format(context=context),
        expected_output="6-10 Q&A pairs in **Q:** / A: format.",
        agent=agent,
    )
