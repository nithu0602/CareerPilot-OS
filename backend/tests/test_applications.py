import json

from fastapi.testclient import TestClient

from app.main import app
from app.services.application_service import create_application, prepare_application


def test_application_preparation_is_grounded_and_state_is_manual(tmp_path, monkeypatch):
    analyses = tmp_path / "analyses"
    jobs = tmp_path / "jobs"
    analyses.mkdir()
    (analyses / "resume-1.json").write_text(json.dumps({
        "profile": {
            "skills": ["Python", "SQL"],
            "projects": "Built an analytics dashboard",
            "experience": "Data analyst intern",
            "education": "BSc Computer Science",
            "certifications": "",
            "achievements": "",
        }
    }), encoding="utf-8")
    monkeypatch.setenv("ANALYSIS_STORAGE_DIR", str(analyses))
    monkeypatch.setenv("JOBS_CACHE_DIR", str(jobs))
    from app.config import get_settings
    get_settings.cache_clear()

    application = create_application("resume-1", "demo-data-001")
    assert application.state == "SAVED"
    assert application.application_url
    prepared = prepare_application(application.application_id)
    assert prepared.state == "READY_TO_APPLY"
    assert prepared.preparation is not None
    assert all(question.label == "Likely application question" for question in prepared.preparation.likely_questions)
    assert "SQL" in prepared.preparation.skills_to_highlight
    assert any("resume" in point.evidence_source.lower() for point in prepared.preparation.talking_points)


def test_application_api_updates_state_and_handles_missing_inputs(tmp_path, monkeypatch):
    monkeypatch.setenv("ANALYSIS_STORAGE_DIR", str(tmp_path / "analyses"))
    monkeypatch.setenv("JOBS_CACHE_DIR", str(tmp_path / "jobs"))
    from app.config import get_settings
    get_settings.cache_clear()
    client = TestClient(app)
    missing = client.post("/api/applications", json={"resume_id": "missing", "job_id": "demo-data-001"})
    assert missing.status_code == 404
    assert client.get("/api/applications/not-found").status_code == 404
