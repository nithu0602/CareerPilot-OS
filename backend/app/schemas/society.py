from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.job_fit import SponsorshipAssessment

AgentStatus = Literal["SUCCESS", "FAILED", "SKIPPED"]
SocietyStatus = Literal["SUCCESS", "DEGRADED", "FALLBACK"]
EvidenceType = Literal["FACT", "INFERENCE", "RECOMMENDATION", "UNCERTAINTY"]


class EvidenceItem(BaseModel):
    type: EvidenceType
    claim: str
    source: str


class AgentRunResult(BaseModel):
    agent: str
    provider: str
    model: str
    status: AgentStatus
    started_at: datetime
    finished_at: datetime
    duration_ms: int = Field(ge=0)
    error: str | None = None


class ResumeAgentReport(BaseModel):
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience_project_evidence: list[EvidenceItem] = Field(default_factory=list)
    strengths: list[EvidenceItem] = Field(default_factory=list)
    missing_uncertain_areas: list[EvidenceItem] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)


class FitCriticReport(BaseModel):
    strong_evidence: list[EvidenceItem] = Field(default_factory=list)
    missing_evidence: list[EvidenceItem] = Field(default_factory=list)
    uncertainty: list[EvidenceItem] = Field(default_factory=list)
    not_perfect_reason: str
    fit_assessment: str
    sponsorship_assessment: EvidenceItem
    evidence: list[EvidenceItem] = Field(default_factory=list)


class InterviewAgentReport(BaseModel):
    question: str
    category: str
    evaluates: str
    weaknesses: list[EvidenceItem] = Field(default_factory=list)
    follow_up_question: str | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)


class CareerStrategistReport(BaseModel):
    decision: str
    next_best_action: str
    reasoning: str
    evidence_used: list[EvidenceItem] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class SocietyContext(BaseModel):
    resume_analysis: dict[str, object]
    job_record: dict[str, object]
    deterministic_fit_analysis: dict[str, object] | None = None
    skill_gaps: list[dict[str, object]] = Field(default_factory=list)
    interview_context: dict[str, object] | None = None
    interview_results: dict[str, object] | None = None
    application_context: dict[str, object] | None = None
    career_actions: dict[str, object] | None = None
    resume_id: str | None = None


class SocietyResult(BaseModel):
    status: SocietyStatus
    resume_analysis: ResumeAgentReport | None = None
    fit_analysis: FitCriticReport | None = None
    interview_analysis: InterviewAgentReport | None = None
    career_strategy: CareerStrategistReport
    next_best_action: str
    verified_sponsorship: SponsorshipAssessment | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)
    agent_runs: list[AgentRunResult] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class SpecialistPerspective(BaseModel):
    agent: str
    perspective: str
    status: Literal["SUPPORTING", "CHALLENGED", "ADJUSTED", "NEUTRAL"] = "NEUTRAL"
    evidence_type: EvidenceType = "FACT"


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    specialist_perspectives: list[SpecialistPerspective] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class SocietyDeliberateRequest(BaseModel):
    resume_id: str
    job_id: str | None = None
    interview_id: str | None = None
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


class SocietyDeliberateResponse(BaseModel):
    status: SocietyStatus = "SUCCESS"
    reply: str
    specialist_perspectives: list[SpecialistPerspective] = Field(default_factory=list)
    next_best_action: str
    reasoning: str
    confidence: float = Field(ge=0, le=1, default=0.8)
    action_cta: str | None = None
    evidence_used: list[EvidenceItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

