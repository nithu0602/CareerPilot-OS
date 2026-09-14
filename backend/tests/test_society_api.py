from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.routes import society as society_route
from app.models.job_fit import SponsorshipAssessment
from app.schemas.society import CareerStrategistReport, EvidenceItem, SocietyResult
from app.schemas.society import SocietyContext
from app.agents.providers import ProviderError
from app.agents.society_orchestrator import SocietyOrchestrator


client = TestClient(app)


def _resume_file(tmp_path, monkeypatch):
    analysis = tmp_path / "analyses"
    analysis.mkdir()
    (analysis / "resume-1.json").write_text(
        '{"resume_id":"resume-1","filename":"resume.pdf","status":"analyzed",'
        '"analyzed_at":"2026-09-01T00:00:00Z","extracted_text":"Python SQL",'
        '"profile":{"skills":["python"],"education":"MSc Data Science"},'
        '"ats_estimate":70,"score_breakdown":[],"strengths":[],"weaknesses":[],'
        '"recommendations":[],"skill_signals":["python"],"formatting_flags":[]}',
        encoding="utf-8",
    )
    monkeypatch.setenv("ANALYSIS_STORAGE_DIR", str(analysis))
    monkeypatch.setenv("JOBS_CACHE_DIR", str(tmp_path / "jobs"))
    from app.config import get_settings
    get_settings.cache_clear()


def _result():
    return SocietyResult(
        status="SUCCESS",
        career_strategy=CareerStrategistReport(
            decision="Practice",
            next_best_action="Practice SQL.",
            reasoning="The evidence supports practice.",
            evidence_used=[EvidenceItem(type="RECOMMENDATION", claim="Practice SQL.", source="test")],
            confidence=0.8,
        ),
        next_best_action="Practice SQL.",
    )


def test_resume_only_request(monkeypatch, tmp_path):
    _resume_file(tmp_path, monkeypatch)
    monkeypatch.setattr(society_route, "SocietyOrchestrator", lambda: type("O", (), {"analyze": lambda self, context: _result()})())
    response = client.post("/api/society/analyze", json={"resume_id": "resume-1"})
    assert response.status_code == 200
    assert response.json()["next_best_action"] == "Practice SQL."


def test_missing_resume(tmp_path, monkeypatch):
    _resume_file(tmp_path, monkeypatch)
    response = client.post("/api/society/analyze", json={"resume_id": "missing"})
    assert response.status_code == 404


def test_missing_job(tmp_path, monkeypatch):
    _resume_file(tmp_path, monkeypatch)
    response = client.post("/api/society/analyze", json={"resume_id": "resume-1", "job_id": "missing"})
    assert response.status_code == 404


def test_degraded_result_is_returned(monkeypatch, tmp_path):
    _resume_file(tmp_path, monkeypatch)
    degraded = _result().model_copy(update={"status": "DEGRADED"})
    monkeypatch.setattr(society_route, "SocietyOrchestrator", lambda: type("O", (), {"analyze": lambda self, context: degraded})())
    response = client.post("/api/society/analyze", json={"resume_id": "resume-1"})
    assert response.status_code == 200
    assert response.json()["status"] == "DEGRADED"


def test_resume_and_job_request_loads_verified_context(monkeypatch, tmp_path):
    _resume_file(tmp_path, monkeypatch)
    captured = {}
    job = type("Job", (), {"model_dump": lambda self, mode=None: {"job_id": "job-1"}})()
    fit = type(
        "Fit",
        (),
        {
            "skill_gaps": [],
            "model_dump": lambda self, mode=None: {
                "sponsorship": {
                    "classification": "UNCLEAR",
                    "evidence_quote": None,
                    "source_url": "https://example.test/job",
                    "reasoning": "No evidence.",
                    "fact": "No evidence.",
                    "inference": "Verify.",
                }
            },
        },
    )()
    monkeypatch.setattr(society_route, "find_job", lambda job_id: job)
    monkeypatch.setattr(society_route, "_load_match", lambda resume_id, job_id: fit)

    class Orchestrator:
        def analyze(self, context):
            captured["context"] = context
            return _result().model_copy(
                update={
                    "verified_sponsorship": SponsorshipAssessment(
                        classification="UNCLEAR",
                        source_url="https://example.test/job",
                        reasoning="No evidence.",
                        fact="No evidence.",
                        inference="Verify.",
                    )
                }
            )

    monkeypatch.setattr(society_route, "SocietyOrchestrator", Orchestrator)
    response = client.post(
        "/api/society/analyze",
        json={"resume_id": "resume-1", "job_id": "job-1"},
    )
    assert response.status_code == 200
    assert captured["context"].job_record == {"job_id": "job-1"}
    assert response.json()["verified_sponsorship"]["classification"] == "UNCLEAR"


def test_interview_context_is_loaded(monkeypatch, tmp_path):
    _resume_file(tmp_path, monkeypatch)
    interview = type(
        "Interview",
        (),
        {
            "resume_id": "resume-1",
            "job_id": "job-1",
            "model_dump": lambda self, mode=None: {"interview_id": "interview-1"},
        },
    )()
    captured = {}

    monkeypatch.setattr(society_route, "get_interview_results", lambda interview_id: interview)

    class Orchestrator:
        def analyze(self, context):
            captured["context"] = context
            return _result()

    monkeypatch.setattr(society_route, "SocietyOrchestrator", Orchestrator)
    response = client.post(
        "/api/society/analyze",
        json={"resume_id": "resume-1", "interview_id": "interview-1"},
    )
    assert response.status_code == 200
    assert captured["context"].interview_context == {"interview_id": "interview-1"}


def test_missing_interview(tmp_path, monkeypatch):
    _resume_file(tmp_path, monkeypatch)
    monkeypatch.setattr(
        society_route,
        "get_interview_results",
        lambda interview_id: (_ for _ in ()).throw(FileNotFoundError()),
    )
    response = client.post(
        "/api/society/analyze",
        json={"resume_id": "resume-1", "interview_id": "missing"},
    )
    assert response.status_code == 404


def test_strategist_fallback_response_is_returned(monkeypatch, tmp_path):
    _resume_file(tmp_path, monkeypatch)
    fallback = _result().model_copy(update={"status": "FALLBACK"})
    monkeypatch.setattr(
        society_route,
        "SocietyOrchestrator",
        lambda: type("O", (), {"analyze": lambda self, context: fallback})(),
    )
    response = client.post("/api/society/analyze", json={"resume_id": "resume-1"})
    assert response.status_code == 200
    assert response.json()["status"] == "FALLBACK"


def test_deliberate_with_user_challenge(monkeypatch, tmp_path):
    _resume_file(tmp_path, monkeypatch)
    job = type("Job", (), {"model_dump": lambda self, mode=None: {"job_id": "job-1", "title": "Data Analyst", "company": "Acme"}})()
    fit = type(
        "Fit",
        (),
        {
            "skill_gaps": [{"skill": "Power BI", "category": "missing required skill"}],
            "model_dump": lambda self, mode=None: {
                "fit_score": 75,
                "skill_gaps": [{"skill": "Power BI", "category": "missing required skill"}],
                "sponsorship": {"classification": "EXPLICIT", "fact": "Sponsors visas."},
            },
        },
    )()
    monkeypatch.setattr(society_route, "find_job", lambda job_id: job)
    monkeypatch.setattr(society_route, "_load_match", lambda resume_id, job_id: fit)

    response = client.post(
        "/api/society/deliberate",
        json={
            "resume_id": "resume-1",
            "job_id": "job-1",
            "message": "I know Tableau instead of Power BI. Does that change your recommendation?",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "Tableau" in data["reply"]
    assert len(data["specialist_perspectives"]) > 0
    assert data["next_best_action"] != ""


def test_deliberate_missing_resume(monkeypatch, tmp_path):
    _resume_file(tmp_path, monkeypatch)
    response = client.post(
        "/api/society/deliberate",
        json={"resume_id": "missing", "message": "Why not 100%?"},
    )
    assert response.status_code == 404


def test_selected_job_existing_fit_score_reaches_society(monkeypatch, tmp_path):
    _resume_file(tmp_path, monkeypatch)
    job = type("Job", (), {"model_dump": lambda self, mode=None: {
        "job_id": "job-1", "title": "Data Analyst", "company": "Acme",
        "location": "London", "required_skills": ["Excel"], "preferred_skills": [],
    }})()
    fit_payload = {
        "fit_score": 72,
        "score_breakdown": [{"name": "Required skill coverage", "score": 50, "weight": 40, "explanation": "1 of 2 requirements."}],
        "matched_requirements": [], "partially_matched_requirements": [],
        "missing_requirements": [{"requirement": "Excel", "status": "missing", "candidate_evidence": "No direct evidence."}],
        "skill_gaps": [{"skill": "Excel", "category": "missing required skill"}],
        "why_this_match": ["Python overlaps."], "why_not_100": ["Excel is missing."],
        "sponsorship": {"classification": "EXPLICIT", "fact": "Visa sponsorship is available."},
    }
    fit = type("Fit", (), {"skill_gaps": fit_payload["skill_gaps"], "model_dump": lambda self, mode=None: fit_payload})()
    monkeypatch.setattr(society_route, "find_job", lambda job_id: job)
    monkeypatch.setattr(society_route, "_load_match", lambda resume_id, job_id: fit)

    response = client.post("/api/society/deliberate", json={
        "resume_id": "resume-1", "job_id": "job-1", "message": "Why am I not a 100% match?",
    })

    assert response.status_code == 200
    assert "72/100" in response.json()["reply"]
    assert "Excel" in response.json()["reply"]


def test_provider_failure_fallback_answers_distinct_questions_from_evidence():
    class FailingProvider:
        provider = "Groq"
        model = "test-model"

        def complete_json(self, prompt):
            raise ProviderError("provider unavailable")

    context = SocietyContext(
        resume_id="resume-1",
        resume_analysis={
            "profile": {"skills": ["Python", "SQL"]},
            "weaknesses": ["Projects do not quantify impact."],
            "recommendations": ["Add measurable outcomes to the projects section."],
        },
        job_record={"title": "Data Analyst", "company": "Acme"},
        deterministic_fit_analysis={
            "fit_score": 72,
            "missing_requirements": [{"requirement": "Excel", "status": "missing"}],
            "partially_matched_requirements": [{"requirement": "Stakeholder communication", "status": "partial"}],
            "skill_gaps": [{"skill": "Excel", "category": "missing required skill"}],
            "sponsorship": {"classification": "EXPLICIT", "fact": "The listing says visa sponsorship is available."},
        },
        skill_gaps=[{"skill": "Excel", "category": "missing required skill"}],
    )
    society = SocietyOrchestrator(groq=FailingProvider(), ollama=FailingProvider())

    fix = society.deliberate(context, "What should I fix first?")
    apply = society.deliberate(context, "Should I apply anyway?")
    projects = society.deliberate(context, "What projects must I do?")
    fit = society.deliberate(context, "Why am I not a 100% match?")

    assert "measurable outcomes" in fix.reply.lower()
    assert "72/100" in apply.reply
    assert "sponsorship" in apply.reply.lower()
    assert "Excel" in projects.reply
    assert "Excel" in fit.reply and "Stakeholder communication" in fit.reply
    assert len({fix.reply, apply.reply, projects.reply, fit.reply}) == 4


def test_society_routes_learning_and_user_reported_evidence_without_changing_fit():
    class FailingProvider:
        provider = "Groq"
        model = "test-model"

        def complete_json(self, prompt):
            raise ProviderError("provider unavailable")

    context = SocietyContext(
        resume_analysis={"profile": {"skills": ["Python", "SQL"]}},
        job_record={"title": "Data Analyst", "company": "Acme"},
        deterministic_fit_analysis={
            "fit_score": 72,
            "skill_gaps": [{"skill": "Tableau", "category": "missing required skill"}],
            "sponsorship": {"classification": "EXPLICIT", "fact": "Visa sponsorship is available."},
        },
        skill_gaps=[{"skill": "Tableau", "category": "missing required skill"}],
    )
    society = SocietyOrchestrator(groq=FailingProvider(), ollama=FailingProvider())

    learning = society.deliberate(context, "If I want to learn Tableau suggest good resources")
    reported = society.deliberate(context, "I actually know Tableau. It just isn't on my CV.")

    assert "learning Tableau" in learning.reply
    assert "official beginner documentation" in learning.reply
    assert "user-reported" in reported.reply
    assert "does not change the deterministic score" in reported.reply


def test_society_never_formats_missing_fit_as_na_score():
    class FailingProvider:
        provider = "Groq"
        model = "test-model"

        def complete_json(self, prompt):
            raise ProviderError("provider unavailable")

    society = SocietyOrchestrator(groq=FailingProvider(), ollama=FailingProvider())
    context = SocietyContext(
        resume_analysis={"profile": {"skills": ["Python"]}},
        job_record={"title": "Data Analyst", "company": "Acme"},
    )
    response = society.deliberate(context, "Why am I not a 100% match?")

    assert "haven't calculated your fit" in response.reply
    assert "N/A/100" not in response.reply
    assert response.action_cta == "JOB_MATCH"

