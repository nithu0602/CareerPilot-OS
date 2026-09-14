import json
from datetime import datetime, timezone
from time import monotonic
from typing import Any, Callable

from pydantic import ValidationError

from app.config import get_settings
from app.models.career import CareerActionsResponse
from app.services.career_strategist import generate_actions
from app.agents.providers import GroqClient, OllamaClient, ProviderError
from app.schemas.society import (
    AgentRunResult,
    CareerStrategistReport,
    ChatMessage,
    EvidenceItem,
    FitCriticReport,
    InterviewAgentReport,
    ResumeAgentReport,
    SocietyContext,
    SocietyDeliberateResponse,
    SocietyResult,
    SpecialistPerspective,
)
from app.models.job_fit import SponsorshipAssessment


def _prompt(label: str, payload: object) -> str:
    return (
        f"You are the {label} in CareerPilot. Return only a concise JSON object "
        "matching the requested fields. Do not invent facts. Distinguish FACT, "
        "INFERENCE, RECOMMENDATION, and UNCERTAINTY in evidence items. "
        f"Input: {json.dumps(payload, ensure_ascii=True, separators=(',', ':'))}"
    )


def _run(
    agent: str,
    provider: str,
    model: str,
    call: Callable[[], Any],
    runs: list[AgentRunResult],
    warnings: list[str],
) -> Any | None:
    started = datetime.now(timezone.utc)
    timer = monotonic()
    try:
        result = call()
    except (ProviderError, ValidationError, ValueError) as exc:
        finished = datetime.now(timezone.utc)
        runs.append(AgentRunResult(
            agent=agent, provider=provider, model=model, status="FAILED",
            started_at=started, finished_at=finished,
            duration_ms=round((monotonic() - timer) * 1000),
            error=str(exc),
        ))
        warnings.append(f"{agent} failed; its output was excluded.")
        return None
    finished = datetime.now(timezone.utc)
    runs.append(AgentRunResult(
        agent=agent, provider=provider, model=model, status="SUCCESS",
        started_at=started, finished_at=finished,
        duration_ms=round((monotonic() - timer) * 1000),
    ))
    return result


def _fallback_strategy(context: SocietyContext) -> CareerStrategistReport:
    action: CareerActionsResponse | None = None
    if context.resume_id:
        action = generate_actions(context.resume_id)
    next_action = action.next_best_action if action else None
    if next_action:
        return CareerStrategistReport(
            decision="Use deterministic CareerPilot recommendation.",
            next_best_action=next_action.suggested_next_step,
            reasoning=next_action.reason,
            evidence_used=[
                EvidenceItem(type="FACT", claim=item, source="CareerPilot deterministic strategy")
                for item in next_action.supporting_evidence
            ],
            confidence=0.5,
        )
    return CareerStrategistReport(
        decision="Review available evidence before choosing an action.",
        next_best_action="Review the resume and job evidence.",
        reasoning="The AI strategist was unavailable and no deterministic action was available.",
        evidence_used=[],
        confidence=0,
    )


def _verified_sponsorship(context: SocietyContext) -> EvidenceItem | None:
    sponsorship = (context.deterministic_fit_analysis or {}).get("sponsorship")
    if not isinstance(sponsorship, dict):
        return None
    classification = sponsorship.get("classification")
    if not isinstance(classification, str):
        return None
    quote = sponsorship.get("evidence_quote")
    claim = f"Verified sponsorship classification: {classification}."
    if isinstance(quote, str) and quote:
        claim += f' Source evidence: "{quote}"'
    return EvidenceItem(
        type="FACT",
        claim=claim,
        source="CareerPilot deterministic fit analysis",
    )


def _ensure_authoritative_metrics(response: SocietyDeliberateResponse, context: SocietyContext, message: str) -> SocietyDeliberateResponse:
    """Keep persisted deterministic values visible when the user explicitly asks about them."""
    lower = message.lower()
    fit_score = (context.deterministic_fit_analysis or {}).get("fit_score")
    asks_about_fit = any(term in lower for term in ("100%", "100 percent", "fit score", "match score", "why am i not", "why not 100"))
    if asks_about_fit and isinstance(fit_score, (int, float)) and f"{fit_score}/100" not in response.reply:
        response.reply = f"Your authoritative CareerPilot fit is {fit_score}/100.\n\n{response.reply}"
    return response


def _fallback_deliberation(context: SocietyContext, message: str) -> SocietyDeliberateResponse:
    lower = message.lower()
    fit = context.deterministic_fit_analysis or {}
    fit_score = fit.get("fit_score")
    skill_gaps = context.skill_gaps or fit.get("skill_gaps", [])
    missing_required = [
        gap.get("skill", "") for gap in skill_gaps if isinstance(gap, dict) and gap.get("category") == "missing required skill"
    ]
    missing_preferred = [
        gap.get("skill", "") for gap in skill_gaps if isinstance(gap, dict) and gap.get("category") == "missing preferred skill"
    ]
    all_missing = [s for s in [*missing_required, *missing_preferred] if s]
    missing_requirements = fit.get("missing_requirements", []) if isinstance(fit.get("missing_requirements"), list) else []
    partial_requirements = fit.get("partially_matched_requirements", []) if isinstance(fit.get("partially_matched_requirements"), list) else []
    requirement_gaps = [
        str(item.get("requirement"))
        for item in [*missing_requirements, *partial_requirements]
        if isinstance(item, dict) and item.get("requirement")
    ]

    sponsorship = fit.get("sponsorship") if isinstance(fit.get("sponsorship"), dict) else {}
    sponsorship_class = sponsorship.get("classification", "UNCLEAR")
    sponsorship_fact = sponsorship.get("fact", "Sponsorship details not verified.")
    sponsorship_quote = sponsorship.get("evidence_quote")

    interview = context.interview_results or {}
    interview_weaknesses = interview.get("weaknesses", []) if isinstance(interview, dict) else []
    interview_avg = interview.get("average_score") if isinstance(interview, dict) else None

    job_title = (context.job_record or {}).get("title", "this role")
    job_company = (context.job_record or {}).get("company", "the employer")

    # Resume profile data
    resume_profile = (context.resume_analysis or {}).get("profile", {})
    resume_skills = resume_profile.get("skills", []) if isinstance(resume_profile, dict) else []
    resume_strengths = (context.resume_analysis or {}).get("strengths", [])
    resume_weaknesses_list = (context.resume_analysis or {}).get("weaknesses", [])
    resume_recommendations = (context.resume_analysis or {}).get("recommendations", [])

    perspectives: list[SpecialistPerspective] = []
    evidence_used: list[EvidenceItem] = []
    warnings: list[str] = []
    reply = ""
    next_action = "Review the evidence before applying."
    reasoning = "Deterministic deliberation based on verified profile and job records."
    confidence = 0.85
    action_cta = None
    has_fit = isinstance(fit_score, (int, float))

    # Check for skill equivalence / substitution queries (e.g., Tableau, Power BI, Excel, etc.)
    bi_tools = ["tableau", "power bi", "looker", "qlik", "excel", "metabase"]
    mentioned_bi = [tool for tool in bi_tools if tool in lower]
    missing_skills_lower = {s.lower() for s in all_missing}
    candidate_tools = [tool for tool in mentioned_bi if tool not in missing_skills_lower]
    if not candidate_tools and mentioned_bi:
        candidate_tools = mentioned_bi

    if any(term in lower for term in ["why not 100", "100%", "score", "not 100", "why am i not"]):
        if not has_fit:
            reply = "I haven't calculated your fit for this role yet. Run Analyze Fit to get the deterministic score, requirement coverage, gaps, and sponsorship evidence before interpreting a match percentage."
            perspectives.append(SpecialistPerspective(
                agent="Fit Critic", perspective="No persisted deterministic fit analysis is available for this selected role.",
                status="NEUTRAL", evidence_type="UNCERTAINTY",
            ))
            next_action = f"Analyze Fit for {job_title}."
            action_cta = "JOB_MATCH"
            confidence = 1.0
            return SocietyDeliberateResponse(
                status="SUCCESS", reply=reply, specialist_perspectives=perspectives,
                next_best_action=next_action, reasoning="A score can only come from the deterministic Fit Engine.",
                confidence=confidence, action_cta=action_cta, evidence_used=evidence_used, warnings=warnings,
            )
        perspectives.append(SpecialistPerspective(
            agent="Fit Critic",
            perspective=f"Calculated match is {fit_score}/100. "
                        f"Gaps identified: {', '.join(all_missing) if all_missing else 'no direct skill gaps, but experience/education weights apply'}.",
            status="SUPPORTING",
            evidence_type="FACT",
        ))
        perspectives.append(SpecialistPerspective(
            agent="Resume Analyst",
            perspective="Verified resume signals cover core competencies, but missing explicit keyword alignment for required items.",
            status="SUPPORTING",
            evidence_type="FACT",
        ))
        reply = (
            f"You are scored at {fit_score}/100 because CareerPilot uses transparent evidence-based weighting. "
            f"The primary deductions are from missing or partial requirements: {', '.join(requirement_gaps or all_missing) if (requirement_gaps or all_missing) else 'heuristic coverage factors'}. "
            "Scores below 100 are normal and indicate areas to substantiate rather than reasons not to explore the role."
        )
        next_action = f"Highlight relevant project evidence for {all_missing[0]}." if all_missing else "Prepare application talking points."
        reasoning = "Fit score is grounded directly in demonstrated requirement overlap."
        action_cta = "PREPARE_APPLICATION" if fit_score and fit_score >= 60 else "UPDATE_RESUME"

    elif any(term in lower for term in ["sponsorship", "visa", "tier 2", "right to work", "work permit", "eligible"]):
        perspectives.append(SpecialistPerspective(
            agent="Fit Critic",
            perspective=f"Authoritative sponsorship assessment: {sponsorship_class}. {sponsorship_fact}",
            status="SUPPORTING",
            evidence_type="FACT",
        ))
        evidence_used.append(EvidenceItem(
            type="FACT",
            claim=f"Sponsorship status: {sponsorship_class}." + (f' Quote: "{sponsorship_quote}"' if sponsorship_quote else ""),
            source="CareerPilot deterministic fit analysis",
        ))
        if sponsorship_class in {"EXPLICIT", "LIKELY"}:
            reply = (
                f"The job listing indicates sponsorship is available or conditional ({sponsorship_class}). "
                "You can proceed with confidence, but confirm specific graduate scheme immigration criteria upon applying."
            )
            next_action = "Prepare your application."
            action_cta = "PREPARE_APPLICATION"
        elif sponsorship_class == "NO":
            reply = (
                "The job listing explicitly indicates no sponsorship or requires unrestricted right to work. "
                "If you require visa sponsorship, this role may present a formal eligibility barrier."
            )
            next_action = "Verify right-to-work eligibility before investing preparation time."
            action_cta = "JOB_MATCH"
        else:
            reply = (
                f"The sponsorship status is {sponsorship_class}. "
                "The source listing mentions work authorization or lacks explicit visa wording. "
                "Check the employer's direct graduate recruitment portal before submitting."
            )
            next_action = "Verify sponsorship on employer site."
            action_cta = "JOB_MATCH"

    elif any(term in lower for term in ["learn", "learning", "resources", "how do i", "how to", "tutorial", "course"]):
        tool_name = (mentioned_bi[0] if mentioned_bi else "the skill you named").title()
        related_gap = next((skill for skill in all_missing if skill.lower() == tool_name.lower()), None)
        relevance = (
            f" {tool_name} is a current gap for {job_title}, so prioritize it before optional tools."
            if related_gap else
            f" Use your existing skills ({', '.join(resume_skills[:3]) if resume_skills else 'from your resume'}) to build a small practice artifact as you learn."
        )
        reply = (
            f"For learning {tool_name}, use a progression rather than generic career advice: start with official beginner documentation and guided exercises; "
            "then use a structured beginner course; then recreate one dashboard from an open dataset; and finally publish a small portfolio dashboard with a short written explanation."
            f"{relevance}"
        )
        perspectives.append(SpecialistPerspective(
            agent="Resume Analyst", perspective=f"Learning recommendation is grounded in documented skills: {', '.join(resume_skills[:3]) if resume_skills else 'limited resume skill evidence'}.",
            status="SUPPORTING", evidence_type="FACT",
        ))
        next_action = f"Complete a beginner {tool_name} exercise and turn it into a portfolio artifact."
        action_cta = "UPDATE_RESUME"

    elif candidate_tools and any(term in lower for term in ["i know", "i actually know", "i have", "instead of", "substitute", "already have", "experience with"]):
        tool_name = (candidate_tools[0] if candidate_tools else (mentioned_bi[0] if mentioned_bi else "your mentioned skill")).title()
        perspectives.append(SpecialistPerspective(
            agent="Fit Critic",
            perspective=f"Candidate has documented/claimed {tool_name}. While this demonstrates transferable domain proficiency, the role explicitly specifies required tools.",
            status="ADJUSTED",
            evidence_type="INFERENCE",
        ))
        perspectives.append(SpecialistPerspective(
            agent="Resume Analyst",
            perspective=f"Documenting a concrete project translating {tool_name} workflows to the role's required stack will bridge recruiter screening concerns.",
            status="SUPPORTING",
            evidence_type="RECOMMENDATION",
        ))
        perspectives.append(SpecialistPerspective(
            agent="Career Strategist",
            perspective="The practical capability gap is lower than the heuristic score suggests. Recommending applying while framing this transferability in application talking points.",
            status="ADJUSTED",
            evidence_type="RECOMMENDATION",
        ))
        reply = (
            f"That is new user-reported evidence: you say you know {tool_name}, but the current resume does not document it. "
            "I would treat it as user-reported rather than verified resume evidence; it does not change the deterministic score until the resume or Fit Engine evidence is updated. "
            f"Add a concrete {tool_name} project or experience bullet before applying for {job_title}."
        )
        next_action = f"Apply for {job_title} while highlighting transferable {tool_name} evidence."
        reasoning = f"Transferable skill evidence ({tool_name}) mitigates functional gap while preparing required tool syntax in parallel."
        action_cta = "PREPARE_APPLICATION"

    elif any(term in lower for term in ["should i apply", "apply anyway", "why shouldn't", "apply yet", "ready to apply"]):
        if not has_fit:
            reply = f"I haven't calculated your fit for {job_title} yet, so I can't ground an application recommendation in a score or missing requirements. Run Analyze Fit first; then review the deterministic gaps and sponsorship evidence."
            perspectives.append(SpecialistPerspective(agent="Fit Critic", perspective="Application advice is waiting for deterministic fit evidence.", status="NEUTRAL", evidence_type="UNCERTAINTY"))
            next_action = f"Analyze Fit for {job_title}."
            action_cta = "JOB_MATCH"
            return SocietyDeliberateResponse(status="SUCCESS", reply=reply, specialist_perspectives=perspectives, next_best_action=next_action, reasoning="No deterministic fit result is available.", confidence=1.0, action_cta=action_cta, evidence_used=evidence_used, warnings=warnings)
        if fit_score and fit_score >= 70:
            perspectives.append(SpecialistPerspective(
                agent="Career Strategist",
                perspective=f"Fit score ({fit_score}/100) is solid. Core required skills overlap.",
                status="SUPPORTING",
                evidence_type="FACT",
            ))
            perspectives.append(SpecialistPerspective(
                agent="Fit Critic",
                perspective=f"Minor gaps remaining: {', '.join(all_missing) if all_missing else 'none critical'}. Addressable during preparation.",
                status="NEUTRAL",
                evidence_type="INFERENCE",
            ))
            sponsorship_note = (
                f" Sponsorship is assessed as {sponsorship_class}: {sponsorship_fact}"
                if sponsorship_class != "UNCLEAR" else " Sponsorship is not verified; confirm eligibility on the employer site."
            )
            reply = (
                f"Yes, you should apply. With a {fit_score}/100 match, you meet the primary threshold for {job_title} at {job_company}. "
                f"The remaining gap ({all_missing[0] if all_missing else 'preferred criteria'}) can be prepared in parallel or framed through adjacent project work."
                f"{sponsorship_note}"
            )
            next_action = f"Prepare and submit your application for {job_title}."
            action_cta = "PREPARE_APPLICATION"
        else:
            perspectives.append(SpecialistPerspective(
                agent="Fit Critic",
                perspective=f"Fit score is {fit_score or 'uncomputed'}/100 with key required gaps: {', '.join(missing_required) if missing_required else 'unspecified'}.",
                status="CHALLENGED",
                evidence_type="FACT",
            ))
            perspectives.append(SpecialistPerspective(
                agent="Career Strategist",
                perspective="Prioritize bridging the top required gap before applying, or prepare talking points that explain adjacent evidence.",
                status="SUPPORTING",
                evidence_type="RECOMMENDATION",
            ))
            reply = (
                f"Applying is possible, but we advise caution before submitting blindly. "
                f"The Fit Critic notes key missing requirement signals ({', '.join(missing_required) if missing_required else 'skills'}). "
                "Strengthening your resume bullets with concrete project evidence first will meaningfully increase interview callback rates."
            )
            next_action = f"Strengthen evidence for {missing_required[0] if missing_required else 'required skills'} before applying."
            action_cta = "UPDATE_RESUME"

    elif any(term in lower for term in ["fix first", "what should i fix", "improve resume", "fix resume", "update resume", "resume better", "resume gaps", "strengthen"]):
        recs = resume_recommendations[:3] if resume_recommendations else ["Add quantified achievements", "Ensure all key skills are explicitly listed", "Strengthen the projects section with measurable outcomes"]
        weaknesses_shown = resume_weaknesses_list[:2] if resume_weaknesses_list else ["No specific resume weaknesses were recorded."]
        reply = (
            f"Fix this first: {recs[0]}. It addresses the current resume evidence: {'; '.join(weaknesses_shown)}. "
            f"Then work through: {'; '.join(recs[1:]) if len(recs) > 1 else 'add a concrete, measurable example.'}"
        )
        perspectives.append(SpecialistPerspective(agent="Resume Analyst", perspective=f"Priority recommendation: {recs[0]}", status="SUPPORTING", evidence_type="RECOMMENDATION"))
        evidence_used.extend(EvidenceItem(type="FACT", claim=weakness, source="CareerPilot resume analysis") for weakness in weaknesses_shown)
        next_action = recs[0]
        action_cta = "UPDATE_RESUME"

    elif ("project" in lower or "projects" in lower) and any(term in lower for term in ["explain", "interviewer", "interview"]):
        raw_projects = resume_profile.get("projects", []) if isinstance(resume_profile, dict) else []
        if isinstance(raw_projects, str):
            projects = [raw_projects]
        elif isinstance(raw_projects, list):
            projects = [str(project) for project in raw_projects if project]
        else:
            projects = []
        project_text = "; ".join(projects[:3]) if projects else "your documented resume projects"
        reply = (
            f"Your resume documents: {project_text}. For each project, explain it as Problem → Approach → Result: "
            "start with the user or business problem, name the technical choices you personally made, then state the documented outcome (do not invent a metric). "
            f"Connect the approach to relevant skills such as {', '.join(resume_skills[:5]) if resume_skills else 'the skills shown on your resume'}. "
            "Expect follow-ups on your individual contribution, trade-offs, validation, and what you would improve next."
        )
        perspectives.append(SpecialistPerspective(agent="Resume Analyst", perspective="Interview explanation is grounded in documented project evidence.", status="SUPPORTING", evidence_type="FACT"))
        perspectives.append(SpecialistPerspective(agent="Career Strategist", perspective="Use a concise Problem → Approach → Result story for each project.", status="SUPPORTING", evidence_type="RECOMMENDATION"))
        next_action = "Prepare one 60-second Problem → Approach → Result explanation for each documented project."
        action_cta = "PRACTICE_INTERVIEW"

    elif any(term in lower for term in ["interview", "practice", "weakness", "communication"]):
        if not isinstance(interview_avg, (int, float)):
            reply = "You haven't completed an interview practice session yet. Start one for the selected role and I can use the real feedback and average score in our next conversation."
            perspectives.append(SpecialistPerspective(
                agent="Interview Agent", perspective="No completed interview result is available for this conversation.",
                status="NEUTRAL", evidence_type="UNCERTAINTY",
            ))
            next_action = "Complete an interview practice session."
            action_cta = "PRACTICE_INTERVIEW"
            return SocietyDeliberateResponse(status="FALLBACK", reply=reply, specialist_perspectives=perspectives, next_best_action=next_action, reasoning="Interview metrics are only shown after a completed practice session.", confidence=1.0, action_cta=action_cta, evidence_used=evidence_used, warnings=warnings)
        weak = interview_weaknesses[0] if interview_weaknesses else "structured response detail"
        perspectives.append(SpecialistPerspective(
            agent="Interview Agent",
            perspective=f"Interview history shows weakness in: {weak}. Practicing concrete situational examples will raise conversion.",
            status="SUPPORTING",
            evidence_type="FACT",
        ))
        reply = (
            f"Our interview agent evaluated your practice performance (average: {interview_avg}/100). "
            f"The primary growth area is: {weak}. "
            "Focus on delivering structured STAR answers (Situation, Task, Action, Result) with measurable metrics."
        )
        next_action = f"Practice adaptive interview on {weak}."
        action_cta = "PRACTICE_INTERVIEW"

    elif any(term in lower for term in ["project", "what projects", "what should i build", "portfolio", "side project"]):
        # Grounded project recommendations based on skill gaps and resume evidence
        gap_projects = []
        for skill in missing_required[:3]:
            gap_projects.append(f"Build a project demonstrating {skill} — it is a required skill for {job_title}.")
        for skill in missing_preferred[:2]:
            gap_projects.append(f"Add a project showing {skill} — it is listed as a preferred skill.")
        if not gap_projects and resume_skills:
            top_skill = resume_skills[0]
            gap_projects = [
                f"Extend an existing project to include end-to-end data pipelines using {top_skill}.",
                "Create a portfolio piece that demonstrates measurable impact (use real metrics where possible).",
                "Contribute to an open-source project in your primary domain.",
            ]
        if not gap_projects:
            gap_projects = [
                "Upload your resume first so the career team can give you role-specific project recommendations.",
            ]
        perspectives.append(SpecialistPerspective(
            agent="Resume Analyst",
            perspective="Project evidence is a key differentiator for graduate roles. Concrete, measurable outcomes outperform generic descriptions.",
            status="SUPPORTING",
            evidence_type="RECOMMENDATION",
        ))
        perspectives.append(SpecialistPerspective(
            agent="Fit Critic",
            perspective=f"Missing required skills for {job_title}: {', '.join(missing_required) if missing_required else 'none detected yet'}. Projects that close these gaps will directly improve your fit score.",
            status="SUPPORTING",
            evidence_type="FACT",
        ))
        perspectives.append(SpecialistPerspective(
            agent="Career Strategist",
            perspective="Focus projects on the highest-weight missing requirements first — they have the most impact on the fit score.",
            status="SUPPORTING",
            evidence_type="RECOMMENDATION",
        ))
        reply = (
            f"I couldn't complete the full team deliberation, but based on your current CareerPilot evidence for {job_title}:\n\n"
            + "\n".join(f"• {p}" for p in gap_projects)
            + "\n\nFocus on projects that produce measurable outcomes — recruiters respond to impact, not just technology."
        )
        next_action = f"Build a project demonstrating {missing_required[0] if missing_required else 'your key skills'} with measurable outcomes."
        action_cta = "UPDATE_RESUME"

    elif any(term in lower for term in ["what roles", "roles fit", "best role", "what job", "suitable role", "graduate job", "find job", "find me"]):
        top_skills = resume_skills[:5] if resume_skills else ["your key skills"]
        perspectives.append(SpecialistPerspective(
            agent="Resume Analyst",
            perspective=f"Your documented skills ({', '.join(top_skills)}) are most relevant to data, analytics, and technology roles.",
            status="SUPPORTING",
            evidence_type="FACT",
        ))
        perspectives.append(SpecialistPerspective(
            agent="Career Strategist",
            perspective="Graduate roles in data analysis, business intelligence, or junior development best match the evidence profile.",
            status="SUPPORTING",
            evidence_type="RECOMMENDATION",
        ))
        reply = (
            f"Based on your resume evidence, your strongest signals are: {', '.join(top_skills)}. "
            "Roles that best match this profile include: Graduate Data Analyst, Junior Data Scientist, Business Intelligence Analyst, "
            "and Software Developer positions. "
            "Use Job Intelligence to search and select a specific role — then run Analyze Fit for a precise match score."
        )
        next_action = "Search for matching roles in Job Intelligence."
        action_cta = "JOB_MATCH"

    elif any(term in lower for term in ["improve resume", "fix resume", "update resume", "resume better", "resume gaps", "strengthen"]):
        recs = resume_recommendations[:3] if resume_recommendations else ["Add quantified achievements", "Ensure all key skills are explicitly listed", "Strengthen the projects section with measurable outcomes"]
        weaknesses_shown = resume_weaknesses_list[:2] if resume_weaknesses_list else ["No specific weaknesses detected — upload your resume for a personalized analysis."]
        perspectives.append(SpecialistPerspective(
            agent="Resume Analyst",
            perspective=f"Top resume recommendations: {'; '.join(recs)}.",
            status="SUPPORTING",
            evidence_type="RECOMMENDATION",
        ))
        perspectives.append(SpecialistPerspective(
            agent="Fit Critic",
            perspective=f"These resume weaknesses reduce your fit score: {'; '.join(weaknesses_shown)}.",
            status="SUPPORTING",
            evidence_type="FACT",
        ))
        reply = (
            "Based on your resume analysis:\n"
            + "\n".join(f"• {r}" for r in recs)
            + f"\n\nKey areas to address: {'; '.join(weaknesses_shown)}. "
            "Go to Resume Intelligence for the full analysis and score breakdown."
        )
        next_action = "Update your resume evidence in Resume Intelligence."
        action_cta = "UPDATE_RESUME"

    elif any(term in lower for term in ["skill gap", "what skills", "biggest gap", "missing skill", "skills i lack"]):
        all_gaps = [f"{s} (required)" for s in missing_required] + [f"{s} (preferred)" for s in missing_preferred]
        gap_list = all_gaps[:5] if all_gaps else ["No specific job selected yet — select a job and run Analyze Fit for a precise gap analysis."]
        perspectives.append(SpecialistPerspective(
            agent="Fit Critic",
            perspective=f"Identified gaps for {job_title}: {', '.join(all_gaps) if all_gaps else 'none — select a job first'}.",
            status="SUPPORTING",
            evidence_type="FACT",
        ))
        perspectives.append(SpecialistPerspective(
            agent="Career Strategist",
            perspective="Prioritize required skill gaps first — they have the highest impact on fit score and recruiter screening.",
            status="SUPPORTING",
            evidence_type="RECOMMENDATION",
        ))
        reply = (
            f"Your current skill gaps for {job_title}:\n"
            + "\n".join(f"• {g}" for g in gap_list)
            + "\n\nFocus on the required skills first. Each one you can demonstrate in a project or resume bullet directly improves your fit score."
        )
        next_action = f"Address the top skill gap: {missing_required[0] if missing_required else 'select a job to get specific gaps'}."
        action_cta = "UPDATE_RESUME" if missing_required else "JOB_MATCH"

    else:
        # Default synthesis
        top_skill = (resume_skills[0] if resume_skills else "Python").title()
        gap = all_missing[0] if all_missing else ("your next target skill" if not resume_skills else "building project evidence")
        perspectives.append(SpecialistPerspective(
            agent="Resume Analyst",
            perspective=f"Candidate's documented strengths include {top_skill} and academic/project foundations.",
            status="SUPPORTING",
            evidence_type="FACT",
        ))
        perspectives.append(SpecialistPerspective(
            agent="Fit Critic",
            perspective=f"Primary area of inquiry for {job_title}: {gap}.",
            status="NEUTRAL",
            evidence_type="FACT",
        ))
        perspectives.append(SpecialistPerspective(
            agent="Career Strategist",
            perspective="Synthesizing team perspectives: proceed with application prep while addressing gap in parallel.",
            status="SUPPORTING",
            evidence_type="RECOMMENDATION",
        ))
        reply = (
            f"Based on your CareerPilot evidence for {job_title}: "
            f"your strongest documented signal is {top_skill}, while the most relevant area to develop is {gap}. "
            f"The career team recommends preparing targeted application talking points that demonstrate your impact. "
            f"If you want a deeper analysis on a specific topic, try asking: 'What projects should I build?', "
            f"'What are my skill gaps?', or 'Should I apply?'"
        )
        next_action = f"Prepare application talking points for {job_title}."
        action_cta = "PREPARE_APPLICATION"

    return SocietyDeliberateResponse(
        status="SUCCESS",
        reply=reply,
        specialist_perspectives=perspectives,
        next_best_action=next_action,
        reasoning=reasoning,
        confidence=confidence,
        action_cta=action_cta,
        evidence_used=evidence_used,
        warnings=warnings,
    )


class SocietyOrchestrator:
    def __init__(
        self,
        groq: GroqClient | None = None,
        ollama: OllamaClient | None = None,
    ) -> None:
        settings = get_settings()
        self.groq = groq or GroqClient(settings)
        self.ollama = ollama or OllamaClient(settings)

    def analyze(self, context: SocietyContext) -> SocietyResult:
        runs: list[AgentRunResult] = []
        warnings: list[str] = []

        resume_raw = _run(
            "Resume Analyst", self.groq.provider, self.groq.model, lambda: self.groq.complete_json(
                _prompt("Resume Analyst", context.resume_analysis)
            ), runs, warnings,
        )
        resume_report = None
        if resume_raw is not None:
            try:
                resume_report = ResumeAgentReport.model_validate(resume_raw)
            except ValidationError as exc:
                warnings.append("Resume Analyst returned an invalid schema.")
                runs[-1].status = "FAILED"
                runs[-1].error = "Invalid ResumeAgentReport schema."

        fit_payload = {
            "resume_report": resume_report.model_dump() if resume_report else context.resume_analysis,
            "job_record": context.job_record,
            "deterministic_fit_analysis": context.deterministic_fit_analysis,
            "skill_gaps": context.skill_gaps,
        }
        fit_raw = _run(
            "Fit Critic", self.groq.provider, self.groq.model, lambda: self.groq.complete_json(
                _prompt("Fit Critic", fit_payload)
            ), runs, warnings,
        )
        fit_report = None
        if fit_raw is not None:
            try:
                fit_report = FitCriticReport.model_validate(fit_raw)
                authoritative_sponsorship = _verified_sponsorship(context)
                if authoritative_sponsorship:
                    fit_report.sponsorship_assessment = authoritative_sponsorship
            except ValidationError:
                warnings.append("Fit Critic returned an invalid schema.")
                runs[-1].status = "FAILED"
                runs[-1].error = "Invalid FitCriticReport schema."

        interview_report = None
        if context.interview_context is None:
            now = datetime.now(timezone.utc)
            runs.append(AgentRunResult(
                agent="Interview Agent", provider=self.ollama.provider, model=self.ollama.model,
                status="SKIPPED", started_at=now, finished_at=now, duration_ms=0,
            ))
        else:
            interview_raw = _run(
                "Interview Agent", self.ollama.provider, self.ollama.model,
                lambda: self.ollama.complete_json(_prompt("Interview Agent", {
                    "resume": context.resume_analysis,
                    "job": context.job_record,
                    "skill_gaps": context.skill_gaps,
                    "context": context.interview_context,
                })), runs, warnings,
            )
            if interview_raw is not None:
                try:
                    interview_report = InterviewAgentReport.model_validate(interview_raw)
                except ValidationError:
                    warnings.append("Interview Agent returned an invalid schema.")
                    runs[-1].status = "FAILED"
                    runs[-1].error = "Invalid InterviewAgentReport schema."

        strategy_payload = {
            "resume_analysis": resume_report.model_dump() if resume_report else None,
            "fit_analysis": fit_report.model_dump() if fit_report else None,
            "interview_analysis": interview_report.model_dump() if interview_report else None,
            "deterministic_fit_analysis": context.deterministic_fit_analysis,
            "career_actions": context.career_actions,
            "application_context": context.application_context,
            "job_deadline": context.job_record.get("deadline"),
            "verified_sponsorship": (context.deterministic_fit_analysis or {}).get("sponsorship"),
        }
        strategy_raw = _run(
            "Career Strategist", self.groq.provider, self.groq.model,
            lambda: self.groq.complete_json(_prompt("Career Strategist", strategy_payload)),
            runs, warnings,
        )
        strategy = None
        status = "SUCCESS"
        if strategy_raw is not None:
            try:
                strategy = CareerStrategistReport.model_validate(strategy_raw)
            except ValidationError:
                warnings.append("Career Strategist returned an invalid schema.")
                runs[-1].status = "FAILED"
                runs[-1].error = "Invalid CareerStrategistReport schema."
        if strategy is None:
            strategy = _fallback_strategy(context)
            status = "FALLBACK"
        elif any(run.status == "FAILED" for run in runs):
            status = "DEGRADED"

        evidence = strategy.evidence_used
        verified_sponsorship = None
        sponsorship = (context.deterministic_fit_analysis or {}).get("sponsorship")
        if isinstance(sponsorship, dict):
            try:
                verified_sponsorship = SponsorshipAssessment.model_validate(sponsorship)
            except ValidationError:
                warnings.append("Stored sponsorship evidence was invalid.")
        return SocietyResult(
            status=status,
            resume_analysis=resume_report,
            fit_analysis=fit_report,
            interview_analysis=interview_report,
            career_strategy=strategy,
            next_best_action=strategy.next_best_action,
            verified_sponsorship=verified_sponsorship,
            evidence=evidence,
            agent_runs=runs,
            warnings=warnings,
        )

    def deliberate(
        self,
        context: SocietyContext,
        message: str,
        history: list[ChatMessage] | list[dict] | None = None,
    ) -> SocietyDeliberateResponse:
        """Deliberate with specialist agents on a user challenge or question."""
        deliberation_payload = {
            "user_message": message,
            "conversation_history": [
                h.model_dump(mode="json") if hasattr(h, "model_dump") else h
                for h in (history or [])
            ],
            "resume_analysis": context.resume_analysis,
            "job_record": context.job_record,
            "deterministic_fit_analysis": context.deterministic_fit_analysis,
            "skill_gaps": context.skill_gaps,
            "interview_results": context.interview_results,
            "application_context": context.application_context,
            "verified_sponsorship": (context.deterministic_fit_analysis or {}).get("sponsorship"),
        }

        try:
            raw_response = self.groq.complete_json(
                "You are CareerPilot, one context-aware AI career assistant. Resume Analyst, Fit Critic, "
                "Interview Agent, and Career Strategist are internal specialists: select only the evidence "
                "relevant to the user's complete natural-language question, then give one natural response. "
                "Use conversation history to resolve references such as 'that', remember user-reported skills, "
                "and compare previously recommended jobs. Documented resume evidence and user-reported evidence "
                "must remain distinct. The deterministic fit analysis is authoritative: never recalculate or "
                "change its score. If no fit exists, say it has not been calculated; never write N/A/100. "
                "If interview_results is absent, say the candidate has not completed an interview practice session "
                "instead of inventing an interview score. Answer project questions from the actual resume projects, "
                "including what they demonstrate and interview talking points. "
                "Return a JSON object with: "
                "'reply' (synthesized response addressing the user directly without inventing ungrounded facts), "
                "'specialist_perspectives' (list of {agent: str, perspective: str, status: 'SUPPORTING'|'CHALLENGED'|'ADJUSTED'|'NEUTRAL', evidence_type: 'FACT'|'INFERENCE'|'RECOMMENDATION'|'UNCERTAINTY'}), "
                "'next_best_action' (concrete next move), "
                "'reasoning' (why this action makes sense), "
                "'confidence' (float between 0 and 1), "
                "'action_cta' ('PREPARE_APPLICATION'|'PRACTICE_INTERVIEW'|'JOB_MATCH'|'UPDATE_RESUME'|null). "
                f"Input: {json.dumps(deliberation_payload, ensure_ascii=True, separators=(',', ':'))}"
            )
            res = SocietyDeliberateResponse.model_validate(raw_response)
            # Enforce verified sponsorship truth invariant
            authoritative = _verified_sponsorship(context)
            if authoritative and any("sponsorship" in p.perspective.lower() for p in res.specialist_perspectives):
                for p in res.specialist_perspectives:
                    if "sponsorship" in p.perspective.lower():
                        p.evidence_type = "FACT"
            return _ensure_authoritative_metrics(res, context, message)
        except (ProviderError, ValidationError, ValueError, Exception):
            return _fallback_deliberation(context, message)

