from typing import Literal

from pydantic import BaseModel, Field


ActionType = Literal[
    "APPLY",
    "PREPARE_APPLICATION",
    "IMPROVE_SKILL",
    "PRACTICE_INTERVIEW",
    "IMPROVE_RESUME",
    "VERIFY_ELIGIBILITY",
    "REVIEW_JOB",
]


class CareerAction(BaseModel):
    action_id: str
    action: ActionType
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    priority_score: int = Field(ge=0)
    title: str
    reason: str
    supporting_evidence: list[str]
    related_job_id: str | None = None
    related_skill: str | None = None
    related_interview_id: str | None = None
    suggested_next_step: str


class CareerDashboard(BaseModel):
    resume_id: str | None
    resume_score: int | None
    job_count: int
    high_fit_jobs: list[dict[str, object]]
    active_interviews: int
    completed_interviews: int
    top_skill_gaps: list[dict[str, object]]
    next_best_action: CareerAction | None
    actions: list[CareerAction]
    notes: list[str]


class CareerActionsResponse(BaseModel):
    resume_id: str | None
    actions: list[CareerAction]
    next_best_action: CareerAction | None
    methodology: str


class CareerPlanRequest(BaseModel):
    resume_id: str | None = None


class CareerPlanResponse(BaseModel):
    resume_id: str | None
    this_week: list[CareerAction]
    next: list[CareerAction]
    explanation: str
