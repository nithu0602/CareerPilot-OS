import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.config import get_settings
from app.models.job import JobRecord
from app.models.job_fit import (
    FitComponent,
    JobMatchAnalysis,
    RequirementEvidence,
    SkillGap,
    SponsorshipAssessment,
)
from app.services.job_data import load_demo_jobs


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9+#. ]", " ", value.lower()).strip()


def _resume_text(profile: dict[str, object]) -> str:
    return _normalize(" ".join(str(value) for value in profile.values()))


def _contains(text: str, term: str) -> bool:
    normalized_term = _normalize(term)
    return bool(normalized_term and normalized_term in text)


def classify_sponsorship(job: JobRecord) -> SponsorshipAssessment:
    source_text = " ".join(filter(None, [job.sponsorship_information, job.eligibility]))
    quote = next(
        (sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", source_text) if re.search(
            r"sponsor|visa|work authorization|right to work|immigration", sentence, re.IGNORECASE
        )),
        None,
    )
    if not quote:
        return SponsorshipAssessment(
            classification="UNCLEAR",
            source_url=job.source_url,
            reasoning="No direct sponsorship or work-authorization sentence was preserved from the job source.",
            fact="The job record contains no explicit sponsorship evidence.",
            inference="Sponsorship cannot be determined from the available source data.",
        )
    lowered = quote.lower()
    if re.search(r"\bwill sponsor\b|\bsponsorship available\b|\bprovide sponsorship\b", lowered):
        classification = "EXPLICIT"
        inference = "The source explicitly indicates sponsorship may be available."
    elif re.search(r"\bdo not sponsor\b|\bno sponsorship\b|\bmust have .*right to work\b|\bunrestricted right to work\b", lowered):
        classification = "NO"
        inference = "The source language indicates sponsorship is not offered or unrestricted work authorization is required."
    elif re.search(r"\bmay sponsor\b|\bconsider sponsorship\b", lowered):
        classification = "LIKELY"
        inference = "The source uses conditional sponsorship language, not a guarantee."
    else:
        classification = "VERIFY"
        inference = "The source mentions immigration or work authorization without establishing a sponsorship outcome."
    return SponsorshipAssessment(
        classification=classification,
        evidence_quote=quote,
        source_url=job.source_url,
        reasoning="Classification is based only on the preserved source sentence.",
        fact=f'Job source says: "{quote}"',
        inference=inference,
    )


def _requirement_evidence(requirements: list[str], resume_text: str, matched_skills: set[str]) -> list[RequirementEvidence]:
    evidence = []
    for requirement in requirements:
        normalized = _normalize(requirement)
        matched = any(_contains(resume_text, skill) for skill in matched_skills if _contains(normalized, skill))
        if matched or _contains(resume_text, requirement):
            status = "matched"
            candidate = f"Resume evidence contains relevant wording for: {requirement}."
        elif any(word in resume_text for word in normalized.split() if len(word) > 4):
            status = "partial"
            candidate = f"Resume contains some related wording, but not enough direct evidence for: {requirement}."
        else:
            status = "missing"
            candidate = "No direct evidence was detected in the analyzed resume."
        evidence.append(RequirementEvidence(requirement=requirement, status=status, candidate_evidence=candidate))
    return evidence


def analyze_job_fit(resume_id: str, profile: dict[str, object], job: JobRecord) -> JobMatchAnalysis:
    text = _resume_text(profile)
    resume_skills = {_normalize(skill) for skill in profile.get("skills", [])}
    required = [_normalize(skill) for skill in job.required_skills]
    preferred = [_normalize(skill) for skill in job.preferred_skills]
    matched_required = {skill for skill in required if skill in resume_skills or _contains(text, skill)}
    matched_preferred = {skill for skill in preferred if skill in resume_skills or _contains(text, skill)}
    required_score = round(len(matched_required) / len(required) * 100) if required else 50
    preferred_score = round(len(matched_preferred) / len(preferred) * 100) if preferred else 50
    experience_score = 100 if profile.get("experience") else 25
    education_score = 100 if profile.get("education") else 25
    title_score = 100 if any(word in text for word in _normalize(job.title).split() if len(word) > 3) else 25
    project_score = 100 if profile.get("projects") else 25
    components = [
        FitComponent(name="Required skill coverage", score=required_score, weight=40, explanation=f"{len(matched_required)} of {len(required)} required skills detected."),
        FitComponent(name="Preferred skill coverage", score=preferred_score, weight=15, explanation=f"{len(matched_preferred)} of {len(preferred)} preferred skills detected."),
        FitComponent(name="Experience alignment", score=experience_score, weight=15, explanation="Experience section evidence is present." if experience_score == 100 else "No experience section evidence was detected."),
        FitComponent(name="Education alignment", score=education_score, weight=10, explanation="Education section evidence is present." if education_score == 100 else "No education section evidence was detected."),
        FitComponent(name="Role/title alignment", score=title_score, weight=10, explanation="Resume language overlaps with the role title." if title_score == 100 else "Limited title-language overlap was detected."),
        FitComponent(name="Project/domain evidence", score=project_score, weight=10, explanation="Project evidence is present." if project_score == 100 else "No project section evidence was detected."),
    ]
    fit_score = round(sum(component.score * component.weight for component in components) / 100)
    all_evidence = _requirement_evidence(job.requirements, text, matched_required | matched_preferred)
    matched = [item for item in all_evidence if item.status == "matched"]
    partial = [item for item in all_evidence if item.status == "partial"]
    missing = [item for item in all_evidence if item.status == "missing"]
    gaps = []
    for skill in job.required_skills:
        normalized = _normalize(skill)
        if normalized in matched_required:
            category = "strong match"
            candidate = f"Resume skill signal: {skill}."
        else:
            category = "missing required skill"
            candidate = "No direct resume skill signal detected."
        gaps.append(SkillGap(skill=skill, category=category, why_it_matters="It is listed as a required skill for this job.", job_evidence=f"Required skill: {skill}.", candidate_evidence=candidate, recommended_action="Show a concrete project or work example using this skill." if category != "strong match" else "Prepare a concise impact example using this skill."))
    for skill in job.preferred_skills:
        if _normalize(skill) not in matched_preferred:
            gaps.append(SkillGap(skill=skill, category="missing preferred skill", why_it_matters="It is listed as a preferred skill and can strengthen the application.", job_evidence=f"Preferred skill: {skill}.", candidate_evidence="No direct resume skill signal detected.", recommended_action=f"Add evidence for {skill} if you have it; otherwise prioritize the required skills."))
    why_not = [f"Missing required skill: {skill}." for skill in job.required_skills if _normalize(skill) not in matched_required]
    why_not += [f"Preferred skill not demonstrated: {skill}." for skill in job.preferred_skills if _normalize(skill) not in matched_preferred]
    if not profile.get("experience"): why_not.append("Experience requirement is not fully demonstrated in the extracted resume.")
    if not profile.get("education"): why_not.append("Education evidence is not present in the extracted resume.")
    if not why_not: why_not.append("The score is below 100 because heuristic coverage is not a substitute for recruiter review.")
    why_match = [f"{len(matched_required)} required skill signals overlap with the resume.", "The job and resume share evidence that can be discussed in an application."] if matched_required else ["The job is available for review, but no direct required-skill overlap was detected."]
    return JobMatchAnalysis(
        match_id=str(uuid4()), resume_id=resume_id, job_id=job.job_id, analyzed_at=datetime.now(timezone.utc),
        fit_score=fit_score, score_breakdown=components, matched_requirements=matched,
        partially_matched_requirements=partial, missing_requirements=missing, skill_gaps=gaps,
        sponsorship=classify_sponsorship(job), salary=job.salary, salary_evidence=job.provenance.salary_source,
        deadline=job.deadline, deadline_evidence=job.provenance.deadline_source, why_this_match=why_match,
        why_not_100=why_not, recommended_next_step="Review the required-skill gaps and verify work authorization details on the source listing.",
    )


def _analysis_path(resume_id: str) -> Path:
    return Path(get_settings().analysis_storage_dir) / f"{resume_id}.json"


def _match_dir() -> Path:
    path = Path(get_settings().jobs_cache_dir) / "matches"
    path.mkdir(parents=True, exist_ok=True)
    return path


def analyze_and_persist(resume_id: str, job: JobRecord) -> JobMatchAnalysis:
    path = _analysis_path(resume_id)
    if not path.exists():
        raise FileNotFoundError("Resume analysis not found.")
    profile = json.loads(path.read_text(encoding="utf-8")).get("profile")
    if not isinstance(profile, dict):
        raise ValueError("Stored resume analysis has no usable profile.")
    result = analyze_job_fit(resume_id, profile, job)
    (_match_dir() / f"{result.match_id}.json").write_text(result.model_dump_json(indent=2), encoding="utf-8")
    (_match_dir() / f"{resume_id}_{job.job_id}.json").write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return result


def get_persisted_match(resume_id: str, job_id: str) -> JobMatchAnalysis:
    path = _match_dir() / f"{resume_id}_{job_id}.json"
    if not path.exists():
        raise FileNotFoundError("Job match not found.")
    return JobMatchAnalysis.model_validate_json(path.read_text(encoding="utf-8"))
