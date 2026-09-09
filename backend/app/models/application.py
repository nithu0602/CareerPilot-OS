from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ApplicationState = Literal["SAVED", "PREPARING", "READY_TO_APPLY", "APPLIED", "INTERVIEW", "OFFER", "REJECTED"]


class ApplicationQuestion(BaseModel):
    question: str
    label: str = "Likely application question"
    relevant_evidence: str
    key_points: list[str]
    missing_evidence_caution: str


class TalkingPoint(BaseModel):
    subject: str
    why_relevant: str
    skills_demonstrated: list[str]
    talking_points: list[str]
    evidence_source: str


class ApplicationPreparation(BaseModel):
    resume_recommendations: list[str]
    sections_to_emphasize: list[str]
    skills_to_highlight: list[str]
    likely_questions: list[ApplicationQuestion]
    talking_points: list[TalkingPoint]
    evidence_note: str


class Application(BaseModel):
    application_id: str
    resume_id: str
    job_id: str
    job_title: str
    company: str
    application_url: str | None
    state: ApplicationState
    fit_score: int | None = Field(default=None, ge=0, le=100)
    sponsorship_status: str | None = None
    salary: str | None = None
    deadline: str | None = None
    preparation: ApplicationPreparation | None = None
    created_at: datetime
    updated_at: datetime


class ApplicationCreateRequest(BaseModel):
    resume_id: str
    job_id: str


class ApplicationUpdateRequest(BaseModel):
    state: ApplicationState

