"""Pydantic models for structured resume analysis."""

from pydantic import BaseModel, Field


class ResumeAnalysisRequest(BaseModel):
    """Input for a structured resume analysis request."""

    resume_text: str = Field(min_length=1, max_length=100_000)


class EducationItem(BaseModel):
    """One education record extracted from a resume."""

    institution: str
    degree: str
    field_of_study: str
    graduation_year: int | None


class ExperienceItem(BaseModel):
    """One professional experience record extracted from a resume."""

    company: str
    title: str
    start_date: str
    end_date: str
    highlights: list[str]


class ProjectItem(BaseModel):
    """One project record extracted from a resume."""

    name: str
    description: str
    technologies: list[str]


class AnalysisResponse(BaseModel):
    """Validated, structured candidate profile derived from resume text."""

    candidate_name: str
    professional_summary: str
    skills: list[str]
    technical_skills: list[str]
    soft_skills: list[str]
    education: list[EducationItem]
    experience: list[ExperienceItem]
    projects: list[ProjectItem]
    certifications: list[str]
    languages: list[str]
    strengths: list[str]
    weaknesses: list[str]
    career_level: str
    estimated_years_experience: float = Field(ge=0)
