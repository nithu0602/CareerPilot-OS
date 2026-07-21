"""Pydantic models for the aggregated dashboard analysis endpoint."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.demo import ATSResponse, DemoResumeRequest, InterviewPrep, JobMatch


class DashboardRequest(DemoResumeRequest):
    """Validate the resume text used to assemble a dashboard response.

    Attributes:
        resume_text: Raw text extracted from a candidate resume.
    """


class DashboardResponse(BaseModel):
    """Represent the complete deterministic dashboard analysis response.

    Attributes:
        candidate_name: Candidate name extracted from the leading resume line when available.
        ats: Deterministic ATS analysis output.
        job_matches: Five deterministic career recommendations.
        interview: Deterministic interview preparation questions.
        processing_time_ms: End-to-end orchestration duration in milliseconds.
    """

    model_config = ConfigDict(extra="forbid")

    candidate_name: str = Field(min_length=1, max_length=120)
    ats: ATSResponse
    job_matches: list[JobMatch] = Field(min_length=5, max_length=5)
    interview: InterviewPrep
    processing_time_ms: int = Field(ge=0)
