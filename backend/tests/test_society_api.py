from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.routes import society as society_route
from app.models.job_fit import SponsorshipAssessment
from app.schemas.society import CareerStrategistReport, EvidenceItem, SocietyResult


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
