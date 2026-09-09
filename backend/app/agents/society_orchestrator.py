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
    EvidenceItem,
    FitCriticReport,
    InterviewAgentReport,
    ResumeAgentReport,
    SocietyContext,
    SocietyResult,
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
