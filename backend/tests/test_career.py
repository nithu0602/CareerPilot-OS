import json

from fastapi.testclient import TestClient

from app.main import app
from app.services.career_strategist import generate_actions


def _match(job_id="job-a", fit_score=82, skill="SQL", category="missing required skill"):
    return {
        "match_id": f"match-{job_id}",
        "resume_id": "resume-1",
        "job_id": job_id,
        "analyzed_at": "2026-09-01T00:00:00Z",
        "fit_score": fit_score,
        "score_breakdown": [],
        "matched_requirements": [],
        "partially_matched_requirements": [],
        "missing_requirements": [],
        "skill_gaps": [{
            "skill": skill, "category": category, "why_it_matters": f"{skill} is used by the role.",
            "job_evidence": f"Required: {skill}", "candidate_evidence": "Limited evidence.",
            "recommended_action": f"Practice {skill}.",
        }],
        "sponsorship": {
            "classification": "UNCLEAR", "evidence_quote": None, "source_url": None,
            "reasoning": "No source evidence.", "fact": "No sponsorship statement was provided.",
            "inference": "Eligibility requires verification.",
        },
        "salary": None, "salary_evidence": None, "deadline": "2026-09-12",
        "deadline_evidence": "Source deadline.", "why_this_match": [], "why_not_100": [],
        "recommended_next_step": "Review the job.",
    }


def test_next_action_prioritizes_repeated_required_gaps(tmp_path, monkeypatch):
    analyses = tmp_path / "analyses"
    jobs = tmp_path / "jobs" / "matches"
    analyses.mkdir()
    jobs.mkdir(parents=True)
    (analyses / "resume-1.json").write_text(json.dumps({
        "ats_estimate": 68, "recommendations": ["Add quantified achievements."],
        "profile": {},
    }), encoding="utf-8")
    (jobs / "resume-1_job-a.json").write_text(json.dumps(_match()), encoding="utf-8")
    (jobs / "resume-1_job-b.json").write_text(json.dumps(_match("job-b", 75)), encoding="utf-8")
    monkeypatch.setenv("ANALYSIS_STORAGE_DIR", str(analyses))
    monkeypatch.setenv("JOBS_CACHE_DIR", str(tmp_path / "jobs"))
    from app.config import get_settings
    get_settings.cache_clear()

    response = generate_actions("resume-1")
    assert response.next_best_action is not None
    assert response.next_best_action.action == "IMPROVE_SKILL"
    assert response.next_best_action.related_skill == "SQL"
    assert any(action.action == "VERIFY_ELIGIBILITY" for action in response.actions)


def test_dashboard_endpoint_handles_missing_data():
    response = TestClient(app).get("/api/career/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert "next_best_action" in body
    assert body["resume_score"] is None
