from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class JobProvenance(BaseModel):
    source_url: str | None = None
    source_name: str = "unknown"
    retrieved_at: datetime
    salary_source: str | None = None
    deadline_source: str | None = None
    requirements_source: str | None = None
    sponsorship_source: str | None = None


class JobRecord(BaseModel):
    job_id: str
    title: str
    company: str
    location: str | None = None
    employment_type: str | None = None
    salary: str | None = None
    deadline: str | None = None
    source_url: str | None = None
    description: str | None = None
    requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    eligibility: str | None = None
    sponsorship_information: str | None = None
    provenance: JobProvenance
    mode: Literal["demo", "live"] = "demo"
    category: str | None = None
    experience_level: str | None = None
    work_mode: str | None = None
    source_domain: str | None = None


class JobSearchRequest(BaseModel):
    role: str = ""
    location: str = ""
    keyword: str = ""
    mode: Literal["demo", "live"] = "demo"
    category: str | None = None
    experience: str | None = None
    work_mode: str | None = None


class JobSearchResponse(BaseModel):
    jobs: list[JobRecord]
    mode: Literal["demo", "live", "fallback"]
    fallback_reason: str | None = None
    total: int
    queries_used: list[str] = Field(default_factory=list)
    result_note: str | None = None
