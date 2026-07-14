"""agents/comparison_agent.py — Agent 3/10 — Comparison Agent (old vs new policy diff)."""

from crewai import Agent, Task

from utils.llm import crewai_model_string
from prompts.comparison_prompt import COMPARISON_PROMPT
from tools.policy_search import search_previous_policy


def build_comparison_agent() -> Agent:
    return Agent(
        role="Policy Comparison Analyst",
        goal="Identify exactly what changed between the previous and new versions of a policy, "
             "using the internal document search tool to find prior versions when not directly provided.",
        backstory="You are a legislative analyst specializing in redlining — comparing bill "
                   "versions clause by clause and flagging every addition, removal, and modification.",
        tools=[search_previous_policy],
        llm=crewai_model_string(),
        verbose=True,
        allow_delegation=False,
    )


def build_comparison_task(agent: Agent, new_context: str, previous_context: str) -> Task:
    return Task(
        description=COMPARISON_PROMPT.format(
            previous_context=previous_context or "(none provided directly — use your search tool)",
            new_context=new_context,
        ),
        expected_output="A markdown comparison table plus a Summary of Changes paragraph.",
        agent=agent,
    )
