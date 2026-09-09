"""Isolated smoke test for the primary AI Society roles.

Run from the backend directory:
    python -m pytest tests/test_society_agents.py -s

This test does not call Gemini, OpenAI, Anakin, or any production CareerPilot code.
"""

import json
from pathlib import Path
from typing import Any

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderSettings(BaseSettings):
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-20b"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:4b"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


RESUME = (
    "Jane Doe\n"
    "MSc Data Science\n"
    "Python, SQL, pandas, scikit-learn\n"
    "Built a customer churn prediction project using Python and SQL."
)
CANDIDATE = "MSc Data Science student with Python, SQL, pandas, scikit-learn and a customer churn prediction project."
JOB = "Graduate Data Analyst requiring Python, SQL, Excel and communication."


def _short(value: object, limit: int = 500) -> str:
    text = " ".join(str(value).split())
    return text[:limit] + ("..." if len(text) > limit else "")


def _safe_error(error: Exception, secrets: tuple[str, ...]) -> str:
    message = str(error)
    for secret in secrets:
        if secret:
            message = message.replace(secret, "[REDACTED]")
    return _short(message)


def _json_from_text(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(
            line for line in cleaned.splitlines() if not line.strip().startswith("```")
        ).strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("provider response did not contain a JSON object")
        value = json.loads(cleaned[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("provider response JSON was not an object")
    return value


def _groq(settings: ProviderSettings, prompt: str) -> dict[str, Any]:
    response = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.groq_api_key}"},
        json={
            "model": settings.groq_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 1400,
            "response_format": {"type": "json_object"},
        },
        timeout=45,
    )
    if response.is_error:
        raise RuntimeError(f"Groq HTTP {response.status_code}: {_short(response.text)}")
    return _json_from_text(response.json()["choices"][0]["message"]["content"])


def _ollama(settings: ProviderSettings, prompt: str) -> dict[str, Any]:
    response = httpx.post(
        f"{settings.ollama_base_url.rstrip('/')}/api/chat",
        json={
            "model": settings.ollama_model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
        },
        timeout=60,
    )
    response.raise_for_status()
    return _json_from_text(response.json()["message"]["content"])


def _run_agent(
    name: str,
    provider: str,
    model: str,
    call: Any,
    prompt: str,
    secrets: tuple[str, ...],
    required_fields: tuple[str, ...],
) -> dict[str, Any] | None:
    try:
        result = call(prompt)
        missing = [field for field in required_fields if not result.get(field)]
        if missing:
            raise ValueError(f"provider response missing required fields: {missing}")
    except Exception as error:
        print(f"\n{name}: FAILURE")
        print(f"Short output: {_safe_error(error, secrets)}")
        return None
    print(f"\n{name}: SUCCESS")
    print(f"Short output: {_short(json.dumps(result, ensure_ascii=True))}")
    print(f"Provider: {provider}; Model: {model}")
    return result


def test_society_agents() -> None:
    settings = ProviderSettings()
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    resume_analyst = _run_agent(
        "Resume Analyst",
        "Groq",
        settings.groq_model,
        lambda prompt: _groq(settings, prompt),
        f"""Return only a JSON object with keys skills, education, experience_project_evidence,
strengths, and missing_or_uncertain_areas. Do not invent facts. Analyze:
{RESUME}""",
        (settings.groq_api_key,),
        (
            "skills",
            "education",
            "experience_project_evidence",
            "strengths",
            "missing_or_uncertain_areas",
        ),
    )

    fit_critic = _run_agent(
        "Fit Critic",
        "Groq",
        settings.groq_model,
        lambda prompt: _groq(settings, prompt),
        f"""Return only a JSON object with keys strong_evidence, missing_evidence,
uncertainty, and not_perfect_reason. Critically assess this fit without inventing facts.
Candidate: {CANDIDATE}
Job: {JOB}""",
        (settings.groq_api_key,),
        ("strong_evidence", "missing_evidence", "uncertainty", "not_perfect_reason"),
    )

    interview_agent = _run_agent(
        "Interview Agent",
        "Ollama",
        settings.ollama_model,
        lambda prompt: _ollama(settings, prompt),
        f"""Return only a JSON object with keys question and evaluates. Ask exactly one
realistic graduate Data Analyst interview question based on:
Candidate: {CANDIDATE}""",
        (),
        ("question", "evaluates"),
    )

    reports = {
        "resume_analyst": resume_analyst,
        "fit_critic": fit_critic,
        "interview_agent": interview_agent,
    }
    strategist = _run_agent(
        "Career Strategist",
        "Groq",
        settings.groq_model,
        lambda prompt: _groq(settings, prompt),
        f"""Return only a JSON object with keys decision, next_best_action, reasoning,
evidence_used, and confidence. Synthesize these reports and select exactly ONE next-best
career action. Do not invent facts.
Reports: {json.dumps(reports, ensure_ascii=True, separators=(',', ':'))}""",
        (settings.groq_api_key,),
        ("decision", "next_best_action", "reasoning", "evidence_used", "confidence"),
    )

    assert all(
        output is not None
        for output in (resume_analyst, fit_critic, interview_agent, strategist)
    ), "One or more primary Society agents failed or returned unusable output"
