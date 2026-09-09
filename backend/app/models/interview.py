from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class InterviewTurn(BaseModel):
    question: str
    question_type: Literal["behavioral", "technical", "project", "situational"]
    competency: str
    answer: str | None = None
    score: int | None = Field(default=None, ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    feedback: str | None = None
    evidence: str | None = None
    follow_up_question: str | None = None
    adaptive: bool = False


class InterviewSession(BaseModel):
    interview_id: str
    resume_id: str
    job_id: str
    job_title: str
    company: str
    status: Literal["active", "completed"]
    question_number: int
    max_questions: int = 5
    current_question: InterviewTurn
    turns: list[InterviewTurn] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class InterviewStartRequest(BaseModel):
    resume_id: str
    job_id: str


class InterviewAnswerRequest(BaseModel):
    answer: str


class InterviewAnswerResponse(BaseModel):
    interview_id: str
    evaluation: InterviewTurn
    next_question: InterviewTurn | None
    progress: int
    status: Literal["active", "completed"]


class InterviewResults(BaseModel):
    interview_id: str
    resume_id: str
    job_id: str
    status: Literal["completed"]
    average_score: int
    overall_assessment: str
    strengths: list[str]
    weaknesses: list[str]
    competencies_assessed: list[str]
    strongest_answer: str
    weakest_answer: str
    recommended_improvements: list[str]
    suggested_next_action: str
    turns: list[InterviewTurn]
