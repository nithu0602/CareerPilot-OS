from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):
    resume_id: str
    filename: str
    status: Literal["uploaded"]


class ScoreComponent(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    weight: int = Field(ge=0, le=100)
    explanation: str


class ResumeAnalysis(BaseModel):
    resume_id: str
    filename: str
    status: Literal["analyzed"]
    analyzed_at: datetime
    extracted_text: str
    profile: dict[str, object]
    ats_estimate: int = Field(ge=0, le=100)
    score_breakdown: list[ScoreComponent]
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    skill_signals: list[str]
    formatting_flags: list[str]

