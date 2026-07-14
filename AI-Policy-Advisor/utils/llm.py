"""
utils/llm.py
=============
Thin wrapper around Google Gemini, shared by every agent.

WHY THIS FILE EXISTS
---------------------
CrewAI agents can call an LLM via LiteLLM's model-string convention
(e.g. "gemini/gemini-1.5-pro"), which is what agents/*.py use directly.
This module additionally exposes a plain `ask_gemini()` function for any
code path that needs a direct model call WITHOUT going through a full
CrewAI Task (e.g. quick classification, or the FastAPI layer answering a
one-off question outside the crew).
"""

import google.generativeai as genai

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_configured = False


def _ensure_configured():
    global _configured
    if not _configured:
        genai.configure(api_key=settings.google_api_key)
        _configured = True


def ask_gemini(prompt: str, temperature: float = 0.3) -> str:
    """
    Send a single prompt to Gemini and return the text response.

    Args:
        prompt: full prompt text (already includes any retrieved context).
        temperature: lower = more deterministic (good for factual policy analysis).
    """
    _ensure_configured()
    model = genai.GenerativeModel(settings.gemini_model)
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=temperature),
        )
        return response.text
    except Exception as exc:
        logger.error("Gemini call failed: %s", exc)
        raise


def crewai_model_string() -> str:
    """The model identifier CrewAI/LiteLLM expects, e.g. 'gemini/gemini-1.5-pro'."""
    return f"gemini/{settings.gemini_model}"
