import json
from datetime import date
from pathlib import Path
from collections import Counter

from app.config import get_settings
from app.models.career import CareerAction, CareerActionsResponse, CareerDashboard, CareerPlanResponse
from app.models.interview import InterviewSession
from app.services.job_data import load_cached_live_jobs, load_demo_jobs
from app.models.job_fit import JobMatchAnalysis


def _read_json(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return None


def _resume(resume_id: str | None) -> dict | None:
    if not resume_id:
        return None
    return _read_json(Path(get_settings().analysis_storage_dir) / f"{resume_id}.json")


def _matches(resume_id: str | None) -> list[JobMatchAnalysis]:
    if not resume_id:
        return []
    directory = Path(get_settings().jobs_cache_dir) / "matches"
    if not directory.exists():
        return []
    records: list[JobMatchAnalysis] = []
    for path in directory.glob(f"{resume_id}_*.json"):
        data = _read_json(path)
        if data:
            try:
                records.append(JobMatchAnalysis.model_validate(data))
            except ValueError:
                continue
    return records


def _interviews(resume_id: str | None) -> list[InterviewSession]:
    if not resume_id:
        return []
    directory = Path(get_settings().jobs_cache_dir) / "interviews"
    if not directory.exists():
        return []
    records: list[InterviewSession] = []
    for path in directory.glob("*.json"):
        data = _read_json(path)
        if data and data.get("resume_id") == resume_id:
            try:
                records.append(InterviewSession.model_validate(data))
            except ValueError:
                continue
    return records


def _deadline_score(deadline: str | None) -> int:
    if not deadline:
        return 0
    try:
        days = (date.fromisoformat(deadline[:10]) - date.today()).days
    except ValueError:
        return 0
    return 25 if 0 <= days <= 14 else 10 if 15 <= days <= 30 else 0


def _priority(score: int) -> str:
    return "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"


def _action(action: str, score: int, title: str, reason: str, evidence: list[str], step: str,
            job_id: str | None = None, skill: str | None = None,
            interview_id: str | None = None) -> CareerAction:
    return CareerAction(
        action_id=f"{action.lower()}-{job_id or skill or interview_id or title.lower().replace(' ', '-')}",
        action=action, priority=_priority(score), priority_score=score,
        title=title, reason=reason, supporting_evidence=evidence,
        related_job_id=job_id, related_skill=skill, related_interview_id=interview_id,
        suggested_next_step=step,
    )


def generate_actions(resume_id: str | None) -> CareerActionsResponse:
    analysis = _resume(resume_id)
    matches = _matches(resume_id)
    interviews = _interviews(resume_id)
    actions: list[CareerAction] = []
    gaps: Counter[str] = Counter()
    gap_meta: dict[str, tuple[str, str, str, str]] = {}
    for match in matches:
        for gap in match.skill_gaps:
            if gap.category in {"missing required skill", "missing preferred skill", "weak evidence"}:
                gaps[gap.skill.lower()] += 1
                gap_meta.setdefault(gap.skill.lower(), (gap.skill, gap.category, gap.why_it_matters, gap.recommended_action))
    for key, frequency in gaps.items():
        skill, category, why, recommendation = gap_meta[key]
        required_bonus = 25 if category == "missing required skill" else 10
        score = 50 + required_bonus + min(20, frequency * 10)
        interview_bonus = 0
        for interview in interviews:
            if any(key in (turn.competency + " " + " ".join(turn.weaknesses)).lower() for turn in interview.turns):
                interview_bonus = 15
                break
        score += interview_bonus
        evidence = [f"Appears in {frequency} analyzed job match{'es' if frequency != 1 else ''}.", f"Gap category: {category}."]
        if interview_bonus:
            evidence.append("A completed interview also recorded a related weakness.")
        actions.append(_action("IMPROVE_SKILL", score, f"Strengthen {skill}", why, evidence, recommendation, skill=skill))
    for match in matches:
        if match.fit_score >= 70:
            urgency = _deadline_score(match.deadline)
            action_type = "APPLY" if match.sponsorship.classification in {"EXPLICIT", "NO"} else "REVIEW_JOB"
            reason = "This is a high-fit opportunity; verify source details before acting." if action_type == "REVIEW_JOB" else "This job has a strong transparent fit score."
            evidence = [f"Fit score: {match.fit_score}/100."]
            if match.deadline:
                evidence.append(f"Source deadline: {match.deadline}.")
            actions.append(_action(action_type, 55 + (match.fit_score - 70) + urgency, f"Review {match.job_id}", reason, evidence, "Open the job source and confirm requirements and eligibility.", job_id=match.job_id))
        if match.sponsorship.classification in {"UNCLEAR", "VERIFY"}:
            actions.append(_action("VERIFY_ELIGIBILITY", 55 + _deadline_score(match.deadline), f"Verify eligibility for {match.job_id}", "Sponsorship evidence is not confirmed.", [match.sponsorship.fact, match.sponsorship.inference], "Check the employer source for current work authorization and sponsorship information.", job_id=match.job_id))
    if analysis:
        for recommendation in analysis.get("recommendations", [])[:2]:
            actions.append(_action("IMPROVE_RESUME", 45, "Improve your resume", recommendation, [recommendation], "Update the resume, then rerun Resume Intelligence.",))
    for interview in interviews:
        if interview.status == "completed":
            weaknesses = [weak for turn in interview.turns for weak in turn.weaknesses]
            if weaknesses:
                weak = weaknesses[0]
                actions.append(_action("PRACTICE_INTERVIEW", 55, f"Practice {weak.lower()}", "Your latest completed interview identified a weakness to practice.", [weak, f"Interview session: {interview.interview_id}."], "Retry an adaptive interview with a concrete example.", interview_id=interview.interview_id))
    actions.sort(key=lambda item: (-item.priority_score, item.action_id))
    return CareerActionsResponse(
        resume_id=resume_id, actions=actions, next_best_action=actions[0] if actions else None,
        methodology="Deterministic prioritization uses required-vs-preferred gaps, frequency, fit, deadline urgency, interview weaknesses, and sponsorship uncertainty. It is a recommendation, not an objectively optimal decision.",
    )


def dashboard(resume_id: str | None) -> CareerDashboard:
    analysis = _resume(resume_id)
    matches = _matches(resume_id)
    interviews = _interviews(resume_id)
    jobs = [*load_demo_jobs(), *load_cached_live_jobs()]
    actions = generate_actions(resume_id)
    high_fit = [{"job_id": match.job_id, "fit_score": match.fit_score} for match in matches if match.fit_score >= 70]
    gap_counts = Counter(gap.skill for match in matches for gap in match.skill_gaps if gap.category != "strong match")
    notes = []
    if not analysis:
        notes.append("No resume analysis yet.")
    if not matches:
        notes.append("No job matches analyzed yet.")
    if not interviews:
        notes.append("No interview data yet.")
    return CareerDashboard(
        resume_id=resume_id, resume_score=analysis.get("ats_estimate") if analysis else None,
        job_count=len(jobs), high_fit_jobs=high_fit,
        active_interviews=sum(item.status == "active" for item in interviews),
        completed_interviews=sum(item.status == "completed" for item in interviews),
        top_skill_gaps=[{"skill": skill, "frequency": count} for skill, count in gap_counts.most_common(5)],
        next_best_action=actions.next_best_action, actions=actions.actions[:5], notes=notes,
    )


def plan(resume_id: str | None) -> CareerPlanResponse:
    actions = generate_actions(resume_id).actions
    return CareerPlanResponse(
        resume_id=resume_id, this_week=actions[:3], next=actions[3:6],
        explanation="This lightweight plan is ordered from the same deterministic evidence-based priorities shown in Next Actions.",
    )
