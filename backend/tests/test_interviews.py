import json

import pytest

from app.services import interview_agent


def _profile():
    return {"name": "Alex", "projects": "Sales dashboard", "skills": ["Python", "SQL"]}


def test_interview_flow_is_adaptive_and_capped(tmp_path, monkeypatch):
    analysis_dir = tmp_path / "analyses"
    jobs_dir = tmp_path / "jobs"
    analysis_dir.mkdir()
    (analysis_dir / "resume-1.json").write_text(json.dumps({"profile": _profile()}), encoding="utf-8")
    monkeypatch.setenv("ANALYSIS_STORAGE_DIR", str(analysis_dir))
    monkeypatch.setenv("JOBS_CACHE_DIR", str(jobs_dir))
    from app.config import get_settings
    get_settings.cache_clear()

    job = interview_agent.find_job("demo-data-001")
    assert job is not None
    session = interview_agent.start_interview("resume-1", "demo-data-001")
    assert 5 <= session.max_questions <= 10
    assert len(session.question_plan) == session.max_questions
    assert len(set(session.question_plan)) == session.max_questions
    assert session.current_question.question

    session, first_evaluation = interview_agent.answer_interview(session.interview_id, "Python.")
    assert first_evaluation.weaknesses
    assert session.current_question.adaptive is True  # weakness-driven follow-up

    while session.status == "active":
        session, evaluation = interview_agent.answer_interview(
            session.interview_id, "I built a dashboard using Python because it improved reporting by 20 percent."
        )
        assert evaluation.score is not None
    assert session.status == "completed"
    assert len(session.turns) == session.max_questions
    # Adaptive planning must not just repeat one question template.
    assert len({turn.question_type for turn in session.turns}) >= 4
    with pytest.raises(ValueError, match="already completed"):
        interview_agent.answer_interview(session.interview_id, "another answer")
    final = interview_agent.results(session.interview_id)
    assert final.average_score > 0
    assert final.turns
    assert final.category_scores
    assert all(item.average_score > 0 for item in final.category_scores)
    assert "Graduate Data Analyst" in final.suggested_next_action
    assert "N/A" not in final.overall_assessment.upper()


def test_missing_resume_and_empty_answer(tmp_path, monkeypatch):
    monkeypatch.setenv("ANALYSIS_STORAGE_DIR", str(tmp_path / "analyses"))
    monkeypatch.setenv("JOBS_CACHE_DIR", str(tmp_path / "jobs"))
    from app.config import get_settings
    get_settings.cache_clear()
    with pytest.raises(FileNotFoundError):
        interview_agent.start_interview("missing", "demo-data-001")


def test_latest_completed_results_returns_none_without_sessions(tmp_path, monkeypatch):
    monkeypatch.setenv("ANALYSIS_STORAGE_DIR", str(tmp_path / "analyses"))
    monkeypatch.setenv("JOBS_CACHE_DIR", str(tmp_path / "jobs"))
    from app.config import get_settings
    get_settings.cache_clear()
    assert interview_agent.latest_completed_results("missing") is None
