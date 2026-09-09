import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.config import get_settings
from app.models.interview import InterviewResults, InterviewSession, InterviewTurn
from app.services.job_data import find_job


def _store_dir() -> Path:
    path = Path(get_settings().jobs_cache_dir) / "interviews"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _resume_profile(resume_id: str) -> dict:
    path = Path(get_settings().analysis_storage_dir) / f"{resume_id}.json"
    if not path.exists():
        raise FileNotFoundError("Resume analysis not found.")
    try:
        profile = json.loads(path.read_text(encoding="utf-8")).get("profile")
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Stored resume analysis is malformed.") from exc
    if not isinstance(profile, dict):
        raise ValueError("Stored resume analysis has no usable profile.")
    return profile


def _save(session: InterviewSession) -> None:
    (_store_dir() / f"{session.interview_id}.json").write_text(
        session.model_dump_json(indent=2), encoding="utf-8"
    )


def load_session(interview_id: str) -> InterviewSession:
    path = _store_dir() / f"{interview_id}.json"
    if not path.exists():
        raise FileNotFoundError("Interview session not found.")
    try:
        return InterviewSession.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("Stored interview session is malformed.") from exc


def _question(profile: dict, job, number: int, weakness: str | None = None) -> InterviewTurn:
    skills = job.required_skills or job.preferred_skills or ["the core requirements"]
    skill = skills[(number - 1) % len(skills)]
    project = str(profile.get("projects") or "a project from your resume")
    if weakness:
        return InterviewTurn(
            question=f"Your previous answer needed more detail on {weakness}. What specific approach, evidence, or result would you add?",
            question_type="technical",
            competency=weakness,
            adaptive=True,
        )
    templates = [
        (f"Tell me about {project} and the impact you personally delivered.", "project", "project impact"),
        (f"How would you use {skill} to approach a problem in this {job.title} role?", "technical", skill),
        (f"Describe a time you had to explain a technical result to a teammate or stakeholder.", "behavioral", "communication"),
        (f"What trade-off would you consider first when delivering work for a {job.title} team?", "situational", "decision-making"),
        (f"How would you validate that your solution meets the requirements for this role?", "technical", "requirements validation"),
    ]
    text, qtype, competency = templates[(number - 1) % len(templates)]
    return InterviewTurn(question=text, question_type=qtype, competency=competency)


def start_interview(resume_id: str, job_id: str) -> InterviewSession:
    profile = _resume_profile(resume_id)
    job = find_job(job_id)
    if job is None:
        raise FileNotFoundError("Job not found.")
    now = datetime.now(timezone.utc)
    session = InterviewSession(
        interview_id=str(uuid4()), resume_id=resume_id, job_id=job_id,
        job_title=job.title, company=job.company, status="active",
        question_number=1, current_question=_question(profile, job, 1),
        created_at=now, updated_at=now,
    )
    _save(session)
    return session


def evaluate_answer(answer: str, question: InterviewTurn, job) -> InterviewTurn:
    words = re.findall(r"\b[\w+#.-]+\b", answer)
    lower = answer.lower()
    evidence = bool(re.search(r"\d|because|result|impact|example|built|improved", lower))
    relevance = 70 if any(term.lower() in lower for term in [question.competency, job.title, *job.required_skills]) else 45
    depth = min(100, 35 + len(words) * 2 + (15 if evidence else 0))
    clarity = 80 if len(words) >= 12 else 45
    score = round((relevance + depth + clarity) / 3)
    strengths = ["Answer addresses the selected role." if relevance >= 70 else "Answer provides a starting point."]
    if evidence:
        strengths.append("Includes a concrete example, result, or rationale.")
    weaknesses = []
    if len(words) < 12:
        weaknesses.append("Answer is brief and needs more supporting detail.")
    if not evidence:
        weaknesses.append("No concrete evidence, result, or rationale was detected.")
    feedback = "Strong role-relevant answer with useful evidence." if score >= 70 else "Relevant start; add a specific action, rationale, and measurable result."
    return question.model_copy(update={
        "answer": answer, "score": score, "strengths": strengths,
        "weaknesses": weaknesses, "feedback": feedback,
        "evidence": "Assessment uses answer length, role terms, and concrete-example signals.",
    })


def answer_interview(interview_id: str, answer: str) -> tuple[InterviewSession, InterviewTurn]:
    if not answer.strip():
        raise ValueError("Answer cannot be empty.")
    session = load_session(interview_id)
    if session.status == "completed":
        raise ValueError("Interview session is already completed.")
    job = find_job(session.job_id)
    if job is None:
        raise FileNotFoundError("Job not found.")
    evaluation = evaluate_answer(answer.strip(), session.current_question, job)
    session.turns.append(evaluation)
    if len(session.turns) >= session.max_questions:
        session.status = "completed"
        session.updated_at = datetime.now(timezone.utc)
        _save(session)
        return session, evaluation
    weakness = evaluation.weaknesses[0] if evaluation.weaknesses else None
    profile = _resume_profile(session.resume_id)
    session.question_number = len(session.turns) + 1
    session.current_question = _question(profile, job, session.question_number, weakness)
    session.updated_at = datetime.now(timezone.utc)
    _save(session)
    return session, evaluation


def results(interview_id: str) -> InterviewResults:
    session = load_session(interview_id)
    if session.status != "completed":
        raise ValueError("Interview is not complete yet.")
    scores = [turn.score or 0 for turn in session.turns]
    strongest = max(session.turns, key=lambda turn: turn.score or 0)
    weakest = min(session.turns, key=lambda turn: turn.score or 0)
    weaknesses = sorted({item for turn in session.turns for item in turn.weaknesses})
    strengths = sorted({item for turn in session.turns for item in turn.strengths})
    improvements = [f"Practice: {item}" for item in weaknesses] or ["Continue practicing concise, evidence-based answers."]
    return InterviewResults(
        interview_id=session.interview_id, resume_id=session.resume_id, job_id=session.job_id,
        status="completed", average_score=round(sum(scores) / len(scores)) if scores else 0,
        overall_assessment="CareerPilot interview assessment based on a transparent rubric, not an objective hiring prediction.",
        strengths=strengths, weaknesses=weaknesses,
        competencies_assessed=sorted({turn.competency for turn in session.turns}),
        strongest_answer=strongest.answer or "", weakest_answer=weakest.answer or "",
        recommended_improvements=improvements,
        suggested_next_action="Review the weakest answer and practice one concrete example before applying.",
        turns=session.turns,
    )
