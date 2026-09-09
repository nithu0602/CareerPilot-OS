import json
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.models.job import JobRecord, JobProvenance
from app.services.job_fit_intelligence import analyze_job_fit, classify_sponsorship
from app.services.job_data import load_demo_jobs


def make_job(**overrides):
    data = {
        "job_id": "fit-test",
        "title": "Python Data Analyst",
        "company": "Demo Company",
        "required_skills": ["Python", "SQL"],
        "preferred_skills": ["Power BI"],
        "requirements": ["Bachelor's degree", "Python and SQL experience"],
        "provenance": JobProvenance(
            source_url="https://example.com/job",
            source_name="Example",
            retrieved_at=datetime.now(timezone.utc),
        ),
    }
    data.update(overrides)
    return JobRecord.model_validate(data)


def profile():
    return {
        "name": "Alex",
        "contact": {},
        "education": "BSc Computer Science",
        "experience": "Data analyst using Python",
        "projects": "Analytics dashboard",
        "skills": ["python"],
        "certifications": "",
        "achievements": "",
    }


def test_fit_scoring_and_requirement_categories():
    result = analyze_job_fit("resume-1", profile(), make_job())
    assert 0 <= result.fit_score <= 100
    assert sum(item.weight for item in result.score_breakdown) == 100
    assert any(item.status == "matched" for item in result.matched_requirements)
    assert any(item.status == "missing" for item in result.missing_requirements)
    assert any("SQL" in item for item in result.why_not_100)
    assert any(gap.category == "missing required skill" and gap.skill == "SQL" for gap in result.skill_gaps)


def test_preferred_skill_detection_and_salary_deadline_preservation():
    job = make_job(salary="CAD 80,000", deadline="2026-12-01", preferred_skills=["Power BI"])
    result = analyze_job_fit("resume-1", profile(), job)
    assert result.salary == "CAD 80,000"
    assert result.deadline == "2026-12-01"
    assert any(gap.category == "missing preferred skill" for gap in result.skill_gaps)


def test_sponsorship_explicit_no_and_unclear():
    assert classify_sponsorship(make_job(sponsorship_information="We will sponsor eligible candidates.")).classification == "EXPLICIT"
    no = classify_sponsorship(make_job(eligibility="Candidates must have unrestricted right to work in Canada."))
    assert no.classification == "NO"
    assert no.evidence_quote
    unclear = classify_sponsorship(make_job())
    assert unclear.classification == "UNCLEAR"
    assert unclear.evidence_quote is None


def test_job_analysis_endpoint_persists_match(tmp_path, monkeypatch):
    analysis_dir = tmp_path / "analyses"
    jobs_dir = tmp_path / "jobs"
    monkeypatch.setenv("ANALYSIS_STORAGE_DIR", str(analysis_dir))
    monkeypatch.setenv("JOBS_CACHE_DIR", str(jobs_dir))
    from app.config import get_settings
    get_settings.cache_clear()
    analysis_dir.mkdir()
    resume_id = "resume-endpoint"
    (analysis_dir / f"{resume_id}.json").write_text(json.dumps({"profile": profile()}), encoding="utf-8")
    job = load_demo_jobs()[0]
    with TestClient(app) as client:
        response = client.post(f"/api/jobs/{job.job_id}/analyze", json={"resume_id": resume_id})
        assert response.status_code == 200
        assert response.json()["job_id"] == job.job_id
        retrieved = client.get(f"/api/jobs/{job.job_id}/match?resume_id={resume_id}")
        assert retrieved.status_code == 200
    get_settings.cache_clear()
