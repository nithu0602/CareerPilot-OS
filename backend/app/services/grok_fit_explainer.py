"""Grok (xAI) fit explanation layer.

The deterministic ``analyze_job_fit`` engine is the authoritative source of truth
for all measurable facts (fit score, skill coverage, sponsorship, etc.).

This module provides a Grok-powered natural-language *explanation* of those facts.
It does NOT override any deterministic result. If Grok is unavailable or the API
key is not configured, ``explain_fit`` returns ``None`` and the caller continues
with the deterministic-only result.

IMPORTANT: Only this module may call GrokClient for Fit Analysis. Do not use Groq
(GroqClient / api.groq.com) or Ollama for Fit Analysis.
"""

from __future__ import annotations

import json

from app.agents.providers import GrokClient, ProviderError
from app.config import get_settings
from app.models.job_fit import JobMatchAnalysis


_SYSTEM_INSTRUCTION = (
    "You are the Fit Critic for CareerPilot, an AI career operating system. "
    "Your role is to explain the job-fit analysis results in clear, grounded language. "
    "You MUST NOT invent job requirements, resume skills, salary information, or sponsorship facts. "
    "All facts below are verified by the deterministic CareerPilot engine. "
    "Your job is to explain WHY the score is what it is, and what the candidate should do. "
    "Be concise (3-5 sentences). Do not repeat numbers verbatim if you can phrase them clearly. "
    "Address the candidate directly as 'you'."
)


def explain_fit(analysis: JobMatchAnalysis) -> str | None:
    """Return a Grok-generated explanation of the deterministic fit analysis.

    Returns ``None`` if the xAI API key is not configured or the call fails.
    The deterministic score and all structured data remain authoritative.
    """
    settings = get_settings()
    if not settings.xai_api_key:
        return None

    # Build the grounded fact payload - Grok reasons over these, does NOT invent
    matched_required = [
        gap.skill for gap in analysis.skill_gaps if gap.category == "strong match"
    ]
    missing_required = [
        gap.skill for gap in analysis.skill_gaps if gap.category == "missing required skill"
    ]
    missing_preferred = [
        gap.skill for gap in analysis.skill_gaps if gap.category == "missing preferred skill"
    ]
    sponsorship = analysis.sponsorship

    facts = {
        "fit_score": analysis.fit_score,
        "matched_required_skills": matched_required,
        "missing_required_skills": missing_required,
        "missing_preferred_skills": missing_preferred,
        "sponsorship_classification": sponsorship.classification,
        "sponsorship_fact": sponsorship.fact,
        "why_not_100": analysis.why_not_100,
        "why_this_match": analysis.why_this_match,
        "recommended_next_step": analysis.recommended_next_step,
    }

    prompt = (
        f"{_SYSTEM_INSTRUCTION}\n\n"
        "Verified deterministic facts from the CareerPilot Fit Engine:\n"
        f"{json.dumps(facts, indent=2, ensure_ascii=False)}\n\n"
        "Explain this fit result to the candidate in 3-5 clear sentences. "
        "Focus on what the score means, the most important gaps, and the recommended next step."
    )

    try:
        grok = GrokClient(settings)
        return grok.complete_text(prompt)
    except ProviderError:
        return None
    except Exception:  # noqa: BLE001 - never surface raw exceptions to the caller
        return None
