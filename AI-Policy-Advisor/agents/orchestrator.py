"""
agents/orchestrator.py — Agent 10/10 — Orchestrator Agent.

WHY THIS FILE EXISTS
---------------------
With 9 specialist agents, something has to decide the RUN ORDER (Comparison
needs the Reader's output; Recommendation needs the Impact analysis;
Report needs everyone) and pass context between them. CrewAI's own
`Process.sequential` handles execution order given a Task list, but we
still need one place that:

  1. Builds all 9 specialist agents + tasks in the correct dependency order
  2. Wires each task's context (which prior task outputs it depends on)
  3. Kicks off the Crew and returns a clean, structured result dict

This is the ONLY file main.py / api / dashboard should import to run a
full analysis.
"""

from typing import Dict

from crewai import Crew, Process

from agents.reader_agent import build_reader_agent, build_reader_task
from agents.summary_agent import build_summary_agent, build_summary_task
from agents.comparison_agent import build_comparison_agent, build_comparison_task
from agents.impact_agent import build_impact_agent, build_impact_task
from agents.recommendation_agent import build_recommendation_agent, build_recommendation_task
from agents.timeline_agent import build_timeline_agent, build_timeline_task
from agents.faq_agent import build_faq_agent, build_faq_task
from agents.government_agent import build_government_agent, build_government_task
from agents.report_agent import build_report_agent, build_report_task

from rag.retriever import retrieve_context, build_context_string
from tools.government_search import search_government_sources
from utils.constants import STAKEHOLDER_TYPES
from utils.logger import get_logger

logger = get_logger(__name__)


def run_full_analysis(doc_id: str, category: str, topic_hint: str = "") -> Dict[str, str]:
    """
    Run the entire 9-agent analysis crew (sequential process, orchestrated
    by this function acting as the 10th/manager agent) for one document.

    Args:
        doc_id: the ingested document's ID (from rag/pipeline.py).
        category: policy category, used to scope the Comparison Agent's
                  internal search and the Government Search Agent's query.
        topic_hint: short human-readable topic string, e.g. "digital literacy
                    education policy", used for the government web search.

    Returns:
        Dict with keys: reader, summary, comparison, impact, recommendations,
        timeline, faqs, government_findings, final_report.
    """
    logger.info("Orchestrator starting full analysis for doc_id=%s (category=%s)", doc_id, category)

    # Ground every agent in the document's own retrieved content
    matches = retrieve_context("summary of this policy document", doc_id=doc_id, top_k=8)
    context = build_context_string(matches)

    # ---- 1. Reader ----
    reader_agent = build_reader_agent()
    reader_task = build_reader_task(reader_agent, context)

    # ---- 2. Summary ----
    summary_agent = build_summary_agent()
    summary_task = build_summary_task(summary_agent, context)

    # ---- 3. Comparison (searches internal DB for a previous version itself, via its tool) ----
    comparison_agent = build_comparison_agent()
    comparison_task = build_comparison_task(comparison_agent, new_context=context, previous_context="")

    # ---- 4. Impact ----
    impact_agent = build_impact_agent()
    impact_task = build_impact_task(impact_agent, context, ", ".join(STAKEHOLDER_TYPES))

    # ---- 5. Recommendation (depends on Impact's output as extra grounding) ----
    recommendation_agent = build_recommendation_agent()
    recommendation_task = build_recommendation_task(recommendation_agent, context, impact_task.description)

    # ---- 6. Government Search (real web search happens here, before the LLM task) ----
    search_query = topic_hint or f"{category} policy circular notification"
    raw_search_results = search_government_sources.run(query=search_query)
    government_agent = build_government_agent()
    government_task = build_government_task(government_agent, topic=search_query, search_results=raw_search_results)

    # ---- 7. Timeline (uses government findings as extra context) ----
    timeline_agent = build_timeline_agent()
    timeline_task = build_timeline_task(timeline_agent, context, raw_search_results)

    # ---- 8. FAQ ----
    faq_agent = build_faq_agent()
    faq_task = build_faq_task(faq_agent, context)

    crew = Crew(
        agents=[
            reader_agent, summary_agent, comparison_agent, impact_agent,
            recommendation_agent, government_agent, timeline_agent, faq_agent,
        ],
        tasks=[
            reader_task, summary_task, comparison_task, impact_task,
            recommendation_task, government_task, timeline_task, faq_task,
        ],
        process=Process.sequential,
        verbose=True,
    )

    crew_output = crew.kickoff()
    task_outputs = {t.description[:30]: str(t.output) for t in crew.tasks}  # debug aid

    results = {
        "reader": str(reader_task.output),
        "summary": str(summary_task.output),
        "comparison": str(comparison_task.output),
        "impact": str(impact_task.output),
        "recommendations": str(recommendation_task.output),
        "government_findings": str(government_task.output),
        "timeline": str(timeline_task.output),
        "faqs": str(faq_task.output),
    }

    # ---- 9. Report Generator — final assembly ----
    report_agent = build_report_agent()
    report_task = build_report_task(report_agent, results)
    report_crew = Crew(agents=[report_agent], tasks=[report_task], process=Process.sequential, verbose=True)
    report_crew.kickoff()
    results["final_report"] = str(report_task.output)

    logger.info("Orchestrator finished full analysis for doc_id=%s", doc_id)
    return results
