"""Orchestrate deterministic demo services into one dashboard response."""

import re
from time import perf_counter_ns
from typing import Annotated

from fastapi import Depends

from app.schemas.dashboard import DashboardResponse
from app.schemas.demo import ATSResponse, InterviewPrep, JobMatch
from app.services.demo_ai import DemoAIService, get_demo_ai_service

_NAME_PATTERN = re.compile(
    r"^(?:name\s*:\s*)?([A-Za-z][A-Za-z'\-]{0,39}\s+[A-Za-z][A-Za-z'\-]{0,39}(?:\s+[A-Za-z][A-Za-z'\-]{0,39}){0,2})$",
    re.IGNORECASE,
)
_NON_NAME_WORDS: frozenset[str] = frozenset(
    {"analyst", "data", "developer", "engineer", "graduate", "manager", "software", "student"}
)


class DashboardService:
    """Aggregate existing deterministic CareerPilot demo services."""

    def __init__(self, demo_ai_service: DemoAIService) -> None:
        """Initialize the service with its reusable demo-service dependency.

        Args:
            demo_ai_service: Existing deterministic service for ATS, job, and interview outputs.
        """
        self._demo_ai_service = demo_ai_service

    def analyze(self, resume_text: str) -> DashboardResponse:
        """Build one dashboard response by orchestrating the existing demo services.

        Args:
            resume_text: Validated raw resume text.

        Returns:
            A single validated dashboard response containing all demo outputs.
        """
        started_at_ns: int = perf_counter_ns()
        ats: ATSResponse = self._demo_ai_service.analyze_ats(resume_text)
        job_matches: list[JobMatch] = self._demo_ai_service.match_jobs(resume_text)
        interview: InterviewPrep = self._demo_ai_service.prepare_interview(resume_text)
        processing_time_ms: int = (perf_counter_ns() - started_at_ns) // 1_000_000

        return DashboardResponse(
            candidate_name=self._extract_candidate_name(resume_text),
            ats=ats,
            job_matches=job_matches,
            interview=interview,
            processing_time_ms=processing_time_ms,
        )

    @staticmethod
    def _extract_candidate_name(resume_text: str) -> str:
        """Extract a conservative display name from the first line of a resume.

        Args:
            resume_text: Raw text extracted from a candidate resume.

        Returns:
            A title-cased candidate name, or ``Candidate`` when no safe name is present.
        """
        first_line: str = resume_text.splitlines()[0].strip()
        match = _NAME_PATTERN.fullmatch(first_line)
        if match is None:
            return "Candidate"

        candidate_name: str = match.group(1).strip()
        name_words: tuple[str, ...] = tuple(word.casefold() for word in candidate_name.split())
        if any(word in _NON_NAME_WORDS for word in name_words):
            return "Candidate"
        return " ".join(word[:1].upper() + word[1:] for word in candidate_name.split())


def get_dashboard_service(
    demo_ai_service: Annotated[DemoAIService, Depends(get_demo_ai_service)],
) -> DashboardService:
    """Create a dashboard orchestrator from the injected demo service.

    Args:
        demo_ai_service: Existing deterministic demo service dependency.

    Returns:
        A dashboard service that reuses the supplied demo service.
    """
    return DashboardService(demo_ai_service)
