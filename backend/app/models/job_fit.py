from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FitComponent(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    weight: int = Field(ge=0, le=100)
    explanation: str


class RequirementEvidence(BaseModel):
    requirement: str
    status: Literal["matched", "partial", "missing"]
    candidate_evidence: str


class SkillGap(BaseModel):
    skill: str
    category: Literal["missing required skill", "missing preferred skill", "weak evidence", "strong match"]
    why_it_matters: str
    job_evidence: str
    candidate_evidence: str
    recommended_action: str


class SponsorshipAssessment(BaseModel):
    classification: Literal["EXPLICIT", "LIKELY", "UNCLEAR", "NO", "VERIFY"]
    evidence_quote: str | None = None
    source_url: str | None = None
    reasoning: str
    fact: str
    inference: str


class JobMatchAnalysis(BaseModel):
    match_id: str
    resume_id: str
    job_id: str
    analyzed_at: datetime
    fit_score: int = Field(ge=0, le=100)
    score_breakdown: list[FitComponent]
    matched_requirements: list[RequirementEvidence]
    partially_matched_requirements: list[RequirementEvidence]
    missing_requirements: list[RequirementEvidence]
    skill_gaps: list[SkillGap]
    sponsorship: SponsorshipAssessment
    salary: str | None
    salary_evidence: str | None
    deadline: str | None
    deadline_evidence: str | None
    why_this_match: list[str]
    why_not_100: list[str]
    recommended_next_step: str
