from datetime import datetime, timezone

from app.agents.providers import ProviderError, parse_json_object
from app.agents.society_orchestrator import SocietyOrchestrator
from app.schemas.society import SocietyContext


def _evidence(kind="FACT"):
    return [{"type": kind, "claim": "Python is listed.", "source": "resume"}]


def _resume():
    return {
        "profile": {"skills": ["python"], "education": "MSc Data Science"},
        "ats_estimate": 70,
    }


def _job():
    return {
        "job_id": "job-1",
        "title": "Data Analyst",
        "company": "Example",
        "deadline": None,
        "required_skills": ["Python"],
        "preferred_skills": [],
        "sponsorship_information": None,
    }


class FakeClient:
    provider = "Fake"
    model = "fake-model"

    def __init__(self, responses=None, error=False):
        self.responses = list(responses or [])
        self.error = error

    def complete_json(self, _prompt):
        if self.error:
            raise ProviderError("unavailable")
        return self.responses.pop(0)


def _reports(include_interview=True):
    resume = {
        "skills": ["Python"],
        "education": ["MSc Data Science"],
        "experience_project_evidence": _evidence(),
        "strengths": _evidence("INFERENCE"),
        "missing_uncertain_areas": _evidence("UNCERTAINTY"),
        "evidence": _evidence(),
    }
    fit = {
        "strong_evidence": _evidence(),
        "missing_evidence": _evidence("UNCERTAINTY"),
        "uncertainty": _evidence("UNCERTAINTY"),
        "not_perfect_reason": "Excel is not evidenced.",
        "fit_assessment": "Partial fit.",
        "sponsorship_assessment": {
            "type": "UNCERTAINTY",
            "claim": "Sponsorship is not explicit.",
            "source": "verified job record",
        },
        "evidence": _evidence(),
    }
    interview = {
        "question": "How would you validate a result?",
        "category": "technical",
        "evaluates": "Validation reasoning",
        "evidence": _evidence("RECOMMENDATION"),
    }
    strategy = {
        "decision": "Practice Excel",
        "next_best_action": "Practice Excel with a small dashboard.",
        "reasoning": "Excel is a verified gap.",
        "evidence_used": _evidence("RECOMMENDATION"),
        "confidence": 0.8,
    }
    return [resume, fit, interview, strategy] if include_interview else [resume, fit, strategy]


def _context(**kwargs):
    return SocietyContext(resume_analysis=_resume(), job_record=_job(), **kwargs)


def test_schema_json_parser_and_happy_path():
    assert parse_json_object("```json\n{\"ok\": true}\n```") == {"ok": True}
    reports = _reports()
    result = SocietyOrchestrator(
        groq=FakeClient([reports[0], reports[1], reports[3]]),
        ollama=FakeClient([reports[2]]),
    ).analyze(_context(interview_context={"question": "answer"}))
    assert result.status == "SUCCESS"
    assert result.next_best_action.startswith("Practice")
    assert len(result.agent_runs) == 4


def test_interview_is_skipped_without_context():
    reports = _reports(include_interview=False)
    result = SocietyOrchestrator(
        groq=FakeClient(reports),
        ollama=FakeClient(error=True),
    ).analyze(_context())
    assert result.status == "SUCCESS"
    assert result.interview_analysis is None
    assert any(run.status == "SKIPPED" for run in result.agent_runs)


def test_provider_failure_degrades_and_strategist_fallback(monkeypatch, tmp_path):
    monkeypatch.setenv("ANALYSIS_STORAGE_DIR", str(tmp_path / "analyses"))
    monkeypatch.setenv("JOBS_CACHE_DIR", str(tmp_path / "jobs"))
    from app.config import get_settings
    get_settings.cache_clear()
    result = SocietyOrchestrator(
        groq=FakeClient(error=True),
        ollama=FakeClient(error=True),
    ).analyze(_context(resume_id="missing"))
    assert result.status == "FALLBACK"
    assert result.career_strategy.confidence == 0
    assert any(run.status == "FAILED" for run in result.agent_runs)


def test_provider_error_is_controlled():
    try:
        raise ProviderError("safe failure")
    except ProviderError as exc:
        assert str(exc) == "safe failure"


def test_verified_sponsorship_cannot_be_overwritten():
    reports = _reports(include_interview=False)
    reports[1]["sponsorship_assessment"] = {
        "type": "INFERENCE",
        "claim": "Sponsorship appears likely.",
        "source": "model inference",
    }
    context = _context(
        deterministic_fit_analysis={
            "sponsorship": {
                "classification": "UNCLEAR",
                "evidence_quote": None,
            }
        }
    )
    result = SocietyOrchestrator(
        groq=FakeClient([reports[0], reports[1], reports[2]]),
        ollama=FakeClient(error=True),
    ).analyze(context)
    assert result.fit_analysis is not None
    assert result.fit_analysis.sponsorship_assessment.type == "FACT"
    assert "UNCLEAR" in result.fit_analysis.sponsorship_assessment.claim
