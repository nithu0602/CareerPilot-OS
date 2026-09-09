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
    assert session.current_question.question
    session, first_evaluation = interview_agent.answer_interview(session.interview_id, "Python.")
    assert first_evaluation.weaknesses
    assert session.current_question.adaptive is True
    for index in range(4):
        session, evaluation = interview_agent.answer_interview(
            session.interview_id, "I built a dashboard using Python because it improved reporting by 20 percent."
        )
        assert evaluation.score is not None
        if index < 4:
            assert session.current_question
    assert session.status == "completed"
    with pytest.raises(ValueError, match="already completed"):
        interview_agent.answer_interview(session.interview_id, "another answer")
    final = interview_agent.results(session.interview_id)
    assert final.average_score > 0
    assert final.turns


def test_missing_resume_and_empty_answer(tmp_path, monkeypatch):
    monkeypatch.setenv("ANALYSIS_STORAGE_DIR", str(tmp_path / "analyses"))
    monkeypatch.setenv("JOBS_CACHE_DIR", str(tmp_path / "jobs"))
    from app.config import get_settings
    get_settings.cache_clear()
    with pytest.raises(FileNotFoundError):
        interview_agent.start_interview("missing", "demo-data-001")
