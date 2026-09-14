import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.config import get_settings
from app.models.interview import (
    InterviewCategoryScore,
    InterviewResults,
    InterviewSession,
    InterviewTurn,
)
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


# Question bank categories. Each entry maps to a role/resume-personalised
# builder so questions always reference the actual selected job and the
# candidate's real resume evidence (never invented facts).
BANK_ORDER: list[str] = [
    "project",
    "technical",
    "sql_data",
    "communication",
    "behavioral",
    "problem_solving",
    "prioritisation",
    "business_insight",
    "motivation",
    "teamwork",
    "role_competency",
    "reflection",
]

CATEGORY_LABELS: dict[str, str] = {
    "behavioral": "Behavioural (STAR)",
    "technical": "Technical",
    "project": "Project experience",
    "situational": "Scenario",
    "sql_data": "SQL & data analysis",
    "communication": "Stakeholder communication",
    "role_competency": "Role competency",
    "motivation": "Motivation & role fit",
    "teamwork": "Teamwork",
    "scenario": "Scenario",
    "problem_solving": "Problem solving",
    "business_insight": "Business insight",
    "reflection": "Feedback & reflection",
    "prioritisation": "Prioritisation",
}

# Terms used to detect whether an answer engages with the question's target.
CATEGORY_TERMS: dict[str, list[str]] = {
    "sql_data": ["sql", "query", "table", "join", "data", "excel", "dashboard", "python", "pandas", "clean", "validate", "database"],
    "technical": ["build", "code", "test", "api", "system", "debug", "design", "implementation"],
    "project": ["project", "built", "designed", "created", "impact", "result", "delivered", "team", "learned"],
    "communication": ["explain", "stakeholder", "present", "communicate", "non-technical", "audience", "plain", "clear"],
    "behavioral": ["situation", "task", "action", "result", "star", "time", "learned", "challenge", "setback"],
    "problem_solving": ["approach", "step", "option", "trade", "decide", "fix", "solution", "assume", "first"],
    "prioritisation": ["priorit", "urgent", "deadline", "decide", "order", "plan", "task", "week", "communicate"],
    "business_insight": ["insight", "business", "value", "decision", "metric", "kpi", "revenue", "cost", "customer"],
    "motivation": ["why", "career", "goal", "passion", "interest", "company", "value", "learn", "growth", "six"],
    "teamwork": ["team", "colleague", "peer", "collaborate", "disagree", "feedback", "together", "role"],
    "role_competency": ["strength", "skill", "role", "requirement", "fit", "prove", "example"],
    "reflection": ["feedback", "act", "improve", "different", "change", "learned"],
    "situational": ["would", "if", "scenario", "decide", "approach"],
}
def _build_question(category: str, profile: dict, job, number: int) -> InterviewTurn:
    """Build a personalised question for one bank category against the real job/resume."""
    role = job.title or "this role"
    company = job.company or "our team"
    project = str(profile.get("projects") or "").strip()
    has_project = bool(project) and project.lower() not in ("none", "n/a", "not provided", "not provided.")
    skills = job.required_skills or job.preferred_skills or ["the core requirements"]
    skill = skills[number % len(skills)]

    if category == "project":
        if has_project:
            question = (
                f"Tell me about {project} from your resume and the impact you personally delivered. "
                f"What did you learn that would be useful in a {role} role?"
            )
        else:
            question = (
                f"Tell me about a project - from your degree, placement, volunteering, or personal work - "
                f"that shows how you work, and the impact you personally delivered."
            )
        competency = "project impact"
    elif category == "technical":
        question = f"How would you apply {skill} to a real piece of work in this {role} role at {company}?"
        competency = skill
    elif category == "sql_data":
        question = (
            f"In a {role} role you will often need to answer questions with data. Walk me through how you "
            f"would handle a request: clarifying the business question, preparing and validating the data, "
            f"and presenting the final result."
        )
        competency = "data analysis & SQL"
    elif category == "communication":
        question = (
            "Describe a time you had to explain a technical or analytical result to a non-technical "
            "stakeholder or teammate. What did you do to make it clear, and what happened?"
        )
        competency = "stakeholder communication"
    elif category == "behavioral":
        question = (
            "Tell me about a time you faced a difficult challenge or setback. Use the STAR format - "
            "Situation, Task, Action, Result - and finish with what you learned."
        )
        competency = "behavioural STAR"
    elif category == "problem_solving":
        question = (
            f"Imagine you are in a {role} role and a stakeholder needs an urgent analysis, but the data is "
            f"incomplete and the deadline is tight. Walk me through how you would handle that."
        )
        competency = "problem solving"
    elif category == "prioritisation":
        question = (
            f"You are a {role} with three deadlines in one week and your manager adds a fourth urgent "
            f"request. How would you prioritise, and what would you communicate to your team?"
        )
        competency = "prioritisation & scenario"
    elif category == "business_insight":
        question = (
            f"For a company like {company}, which one metric or business question would you want to "
            f"investigate in a {role} role, and why?"
        )
        competency = "business insight"
    elif category == "motivation":
        question = (
            f"Why do you want this {role} role at {company} specifically, and what do you hope to "
            f"achieve in your first six months?"
        )
        competency = "motivation & role fit"
    elif category == "teamwork":
        question = (
            "Describe a time you worked in a team to deliver something under pressure. What was your role, "
            "and how did you handle disagreement or a difference of opinion?"
        )
        competency = "teamwork & collaboration"
    elif category == "role_competency":
        question = (
            f"Which of your strengths maps most directly to the requirements of this {role} role, and how "
            f"would you prove it with a concrete example?"
        )
        competency = "role competency"
    else:  # reflection
        question = (
            "When you receive feedback that your analysis or explanation was hard to follow, what do you "
            "do? Give an example of a time you acted on feedback."
        )
        competency = "feedback & reflection"
    return InterviewTurn(question=question, question_type=category, competency=competency)
def _session_length(job_id: str) -> int:
    """Deterministic 5-10 question session length derived from the job id."""
    digest = int(hashlib.sha256(job_id.encode("utf-8")).hexdigest(), 16)
    return 5 + (digest % 6)


def _question_plan(job, count: int) -> list[str]:
    """Deterministic per-role ordering of the question bank, no repeated categories."""
    digest = int(hashlib.sha256(job.job_id.encode("utf-8")).hexdigest(), 16)
    start = digest % len(BANK_ORDER)
    ordered = BANK_ORDER[start:] + BANK_ORDER[:start]
    return ordered[:count]


def _adaptive_follow_up(previous: InterviewTurn, evaluation: InterviewTurn) -> InterviewTurn | None:
    """Return a targeted deepening follow-up when the last answer was weak."""
    if not evaluation.weaknesses or previous.adaptive:
        return None
    weakness = evaluation.weaknesses[0]
    if any(token in weakness.lower() for token in ("brief", "evidence", "detail", "concrete")):
        return InterviewTurn(
            question=(
                f"Good start. For the competency '{previous.competency}', give me a specific example: "
                f"what exactly you did, the tools or methods you used, and the measurable result."
            ),
            question_type=previous.question_type,
            competency=previous.competency,
            adaptive=True,
        )
    return None


def _next_question(session: InterviewSession, profile: dict, job) -> InterviewTurn:
    """Adaptive planner: deepen a weak area first, otherwise the next planned category."""
    if session.turns:
        follow_up = _adaptive_follow_up(session.current_question, session.turns[-1])
        if follow_up is not None:
            return follow_up
    plan = session.question_plan or BANK_ORDER[: session.max_questions]
    covered = {turn.question_type for turn in session.turns}
    for category in plan:
        if category not in covered:
            return _build_question(category, profile, job, session.question_number)
    return _build_question("reflection", profile, job, session.question_number)


def start_interview(resume_id: str, job_id: str) -> InterviewSession:
    profile = _resume_profile(resume_id)
    job = find_job(job_id)
    if job is None:
        raise FileNotFoundError("Job not found.")
    now = datetime.now(timezone.utc)
    max_questions = _session_length(job.job_id)
    plan = _question_plan(job, max_questions)
    first = _build_question(plan[0], profile, job, 1)
    session = InterviewSession(
        interview_id=str(uuid4()), resume_id=resume_id, job_id=job_id,
        job_title=job.title, company=job.company, status="active",
        question_number=1, max_questions=max_questions, question_plan=plan,
        current_question=first, created_at=now, updated_at=now,
    )
    _save(session)
    return session


def evaluate_answer(answer: str, question: InterviewTurn, job) -> InterviewTurn:
    words = re.findall(r"\b[\w+#.-]+\b", answer)
    lower = answer.lower()
    evidence = bool(re.search(r"\d|%|percent|because|result|impact|example|built|improved", lower))
    signals = [question.competency, job.title, *job.required_skills, *job.preferred_skills]
    signal_hits = sum(1 for term in signals if term and term.lower() in lower)
    type_terms = CATEGORY_TERMS.get(question.question_type, [])
    type_hits = sum(1 for term in type_terms if term in lower)
    relevance = 70 if (signal_hits or type_hits) else 45
    depth = min(100, 35 + len(words) * 2 + (15 if evidence else 0))
    clarity = 80 if len(words) >= 12 else 45
    score = round((relevance + depth + clarity) / 3)
    strengths = ["Answer addresses the selected role." if relevance >= 70 else "Answer provides a starting point."]
    if evidence:
        strengths.append("Includes a concrete example, result, or rationale.")
    if score >= 75:
        strengths.append("Clear, evidence-backed structure.")
    weaknesses = []
    if len(words) < 12:
        weaknesses.append("Answer is brief and needs more supporting detail.")
    if not evidence:
        weaknesses.append("No concrete evidence, result, or rationale was detected.")
    if relevance < 55 and len(words) >= 12:
        weaknesses.append("Answer is not tightly tied to the question's competency.")
    if score >= 70:
        feedback = "Strong role-relevant answer with useful evidence."
    elif evidence:
        feedback = "Relevant answer; make the action and result crisper and more specific."
    else:
        feedback = "Relevant start; add a specific action, rationale, and measurable result."
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
    profile = _resume_profile(session.resume_id)
    session.question_number = len(session.turns) + 1
    session.current_question = _next_question(session, profile, job)
    session.updated_at = datetime.now(timezone.utc)
    _save(session)
    return session, evaluation


# Targeted improvement advice per evaluated category, used in the final report.
CATEGORY_ADVICE: dict[str, str] = {
    "sql_data": "Practice a SQL join-and-validate exercise, then explain your approach out loud.",
    "communication": "Rehearse explaining one project in plain English to a non-technical friend.",
    "technical": "Deepen the highest-priority skill for the role with a small applied example.",
    "behavioral": "Prepare two STAR stories (a success and a setback) before the interview.",
    "project": "Add measurable impact figures to each project talking point.",
    "motivation": "Research the employer and prepare a 60-second 'why this role' answer.",
    "teamwork": "Prepare a specific example of resolving disagreement or a difference of opinion.",
    "problem_solving": "Practice a structured 3-step approach for ambiguous requests.",
    "prioritisation": "Prepare a clear framework for juggling competing deadlines.",
    "business_insight": "Prepare one metric-driven insight about the business.",
    "role_competency": "Map your top three strengths to the role requirements in writing.",
    "reflection": "Prepare an example of a time you acted on feedback.",
    "situational": "Walk through two or three scenario responses using a STAR-light structure.",
}

CATEGORY_NEXT_ACTION: dict[str, str] = {
    "sql_data": "Complete a short SQL/data exercise and bring the output to your next practice round.",
    "communication": "Re-record one answer targeting a non-technical audience and tighten the jargon.",
    "technical": "Run a mini project or coding exercise on the biggest missing technical skill.",
    "behavioral": "Write out two full STAR stories and practise them aloud under a timer.",
    "project": "Quantify the impact of your best project with numbers before applying.",
    "motivation": "Prepare a specific 'why this role and company' answer grounded in their work.",
    "teamwork": "Practise a concrete collaboration story with a clear conflict and resolution.",
    "problem_solving": "Rehearse walking through an ambiguous problem in clear, ordered steps.",
    "prioritisation": "Practise prioritising a realistic week of competing deadlines out loud.",
    "business_insight": "Research the business and prepare one data-driven observation about it.",
    "role_competency": "Draft a mapping of your strengths to the posted role requirements.",
    "reflection": "Prepare a before/after example of acting on feedback.",
    "situational": "Rehearse two scenario responses with a clear action-and-outcome structure.",
}


def results(interview_id: str) -> InterviewResults:
    session = load_session(interview_id)
    if session.status != "completed":
        raise ValueError("Interview is not complete yet.")
    scores = [turn.score or 0 for turn in session.turns]
    strongest = max(session.turns, key=lambda turn: turn.score or 0)
    weakest = min(session.turns, key=lambda turn: turn.score or 0)
    weaknesses = sorted({item for turn in session.turns for item in turn.weaknesses})
    strengths = sorted({item for turn in session.turns for item in turn.strengths})
    competencies = sorted({turn.competency for turn in session.turns})

    by_category: dict[str, list[InterviewTurn]] = {}
    for turn in session.turns:
        by_category.setdefault(turn.question_type, []).append(turn)
    category_scores = [
        InterviewCategoryScore(
            category=category,
            average_score=round(sum(turn.score or 0 for turn in turns) / len(turns)),
            question_count=len(turns),
        )
        for category, turns in sorted(by_category.items())
    ]

    improvements: list[str] = []
    ranked = sorted(
        by_category,
        key=lambda cat: (sum(turn.score or 0 for turn in by_category[cat]) / len(by_category[cat]), cat),
    )
    for category in ranked:
        average = round(sum(turn.score or 0 for turn in by_category[category]) / len(by_category[category]))
        if average < 70:
            tip = CATEGORY_ADVICE.get(category)
            if tip:
                improvements.append(f"({CATEGORY_LABELS.get(category, category.replace('_', ' '))}) {tip}")
    if not improvements:
        improvements = ["Continue practicing concise, evidence-based answers with concrete results."]

    weakest_category = min(category_scores, key=lambda item: item.average_score).category
    next_action = CATEGORY_NEXT_ACTION.get(
        weakest_category, "Review the weakest answer and practice one concrete example before applying."
    )
    if session.job_title:
        next_action = f"For {session.job_title}: {next_action}"

    return InterviewResults(
        interview_id=session.interview_id, resume_id=session.resume_id, job_id=session.job_id,
        status="completed", average_score=round(sum(scores) / len(scores)) if scores else 0,
        overall_assessment=(
            f"CareerPilot interview assessment for {session.job_title} at {session.company}. "
            "Scores come from a transparent rubric, not an objective hiring prediction."
        ),
        strengths=strengths, weaknesses=weaknesses,
        competencies_assessed=competencies,
        category_scores=category_scores,
        strongest_answer=strongest.answer or "", weakest_answer=weakest.answer or "",
        recommended_improvements=improvements,
        suggested_next_action=next_action,
        turns=session.turns,
    )


def latest_completed_results(resume_id: str, job_id: str | None = None) -> InterviewResults | None:
    """Return the newest completed practice result for Society context, if one exists."""
    candidates: list[InterviewSession] = []
    for path in _store_dir().glob("*.json"):
        try:
            session = InterviewSession.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if session.status == "completed" and session.resume_id == resume_id and (job_id is None or session.job_id == job_id):
            candidates.append(session)
    if not candidates:
        return None
    return results(max(candidates, key=lambda item: item.updated_at).interview_id)
