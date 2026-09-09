import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.config import get_settings
from app.models.application import (
    Application,
    ApplicationPreparation,
    ApplicationQuestion,
    TalkingPoint,
)
from app.services.job_data import find_job
from app.services.job_fit_intelligence import get_persisted_match


def _directory() -> Path:
    path = Path(get_settings().jobs_cache_dir) / "applications"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _profile(resume_id: str) -> dict:
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


def _save(application: Application) -> None:
    (_directory() / f"{application.application_id}.json").write_text(
        application.model_dump_json(indent=2), encoding="utf-8"
    )


def _load(application_id: str) -> Application:
    path = _directory() / f"{application_id}.json"
    if not path.exists():
        raise FileNotFoundError("Application not found.")
    try:
        return Application.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("Stored application is malformed.") from exc


def list_applications() -> list[Application]:
    return [_load(path.stem) for path in _directory().glob("*.json")]


def create_application(resume_id: str, job_id: str) -> Application:
    _profile(resume_id)
    job = find_job(job_id)
    if job is None:
        raise FileNotFoundError("Job not found.")
    fit_score = None
    sponsorship = None
    try:
        match = get_persisted_match(resume_id, job_id)
        fit_score = match.fit_score
        sponsorship = match.sponsorship.classification
    except FileNotFoundError:
        pass
    now = datetime.now(timezone.utc)
    application = Application(
        application_id=str(uuid4()), resume_id=resume_id, job_id=job_id,
        job_title=job.title, company=job.company, application_url=job.source_url,
        state="SAVED", fit_score=fit_score, sponsorship_status=sponsorship,
        salary=job.salary, deadline=job.deadline, created_at=now, updated_at=now,
    )
    _save(application)
    return application


def prepare_application(application_id: str) -> Application:
    application = _load(application_id)
    profile = _profile(application.resume_id)
    job = find_job(application.job_id)
    if job is None:
        raise FileNotFoundError("Job not found.")
    skills = [str(item) for item in profile.get("skills", []) if item]
    required = job.required_skills or []
    relevant = [skill for skill in skills if any(skill.lower() in required_skill.lower() or required_skill.lower() in skill.lower() for required_skill in required)]
    project = str(profile.get("projects") or "").strip()
    experience = str(profile.get("experience") or "").strip()
    sections = [name for name in ("education", "experience", "projects", "skills", "certifications", "achievements") if str(profile.get(name) or "").strip()]
    recommendations = []
    if relevant:
        recommendations.append(f"Highlight demonstrated skills relevant to this role: {', '.join(relevant)}.")
    else:
        recommendations.append("No directly matching required skill evidence was detected; do not claim unsupported experience.")
    if project:
        recommendations.append("Emphasize the resume project evidence that connects to the role's responsibilities.")
    if not any("achievement" in item.lower() for item in sections):
        recommendations.append("Add quantified achievements only where they are supported by your actual experience.")
    questions = [
        ApplicationQuestion(
            question=f"Why are you interested in the {job.title} role?",
            relevant_evidence=job.description or "The job description was not provided.",
            key_points=[f"Connect your documented skills to {job.title}.", "Use only evidence from your resume."],
            missing_evidence_caution="Do not claim motivation, experience, or qualifications not present in the resume.",
        ),
    ]
    if relevant:
        skill = relevant[0]
        questions.append(ApplicationQuestion(
            question=f"Describe your experience with {skill}.",
            relevant_evidence=f"Resume skills include {skill}.",
            key_points=[f"Explain the context in which {skill} appears in your resume.", "Mention a concrete result only if documented."],
            missing_evidence_caution="The resume does not establish depth beyond the listed evidence.",
        ))
    else:
        skill = required[0] if required else "the required skills"
        questions.append(ApplicationQuestion(
            question=f"Describe your experience with {skill}.",
            relevant_evidence="No matching resume evidence was detected.",
            key_points=["Explain adjacent experience only if it is genuinely documented.", "Be transparent about any learning gap."],
            missing_evidence_caution=f"Do not claim experience with {skill} without resume evidence.",
        ))
    if project:
        questions.append(ApplicationQuestion(
            question="Describe a relevant project or experience.",
            relevant_evidence=project,
            key_points=["State your contribution.", "Explain the documented tools or outcome."],
            missing_evidence_caution="Avoid adding impact metrics that are not in the resume.",
        ))
    points = []
    if project:
        points.append(TalkingPoint(
            subject="Resume project", why_relevant="It is the candidate's documented project evidence.",
            skills_demonstrated=skills, talking_points=["Describe the project scope.", "Clarify your personal contribution.", "Use only documented outcomes."],
            evidence_source="Resume profile: projects",
        ))
    if experience:
        points.append(TalkingPoint(
            subject="Resume experience", why_relevant="It is the candidate's documented experience evidence.",
            skills_demonstrated=skills, talking_points=["Describe responsibilities relevant to the role.", "Give a concrete example from the resume."],
            evidence_source="Resume profile: experience",
        ))
    application.preparation = ApplicationPreparation(
        resume_recommendations=recommendations, sections_to_emphasize=sections,
        skills_to_highlight=relevant, likely_questions=questions, talking_points=points,
        evidence_note="Preparation is grounded in the stored resume profile and normalized job record. Missing evidence is explicitly flagged.",
    )
    application.state = "READY_TO_APPLY"
    application.updated_at = datetime.now(timezone.utc)
    _save(application)
    return application


def update_application(application_id: str, state: str) -> Application:
    application = _load(application_id)
    application.state = state
    application.updated_at = datetime.now(timezone.utc)
    _save(application)
    return application

