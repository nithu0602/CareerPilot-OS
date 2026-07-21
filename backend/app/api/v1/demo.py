"""Deterministic demo endpoints for CareerPilot OS."""

from fastapi import APIRouter, Depends, status

from app.core.logging import get_logger
from app.schemas.demo import ATSResponse, DemoResumeRequest, InterviewPrep, JobMatch
from app.services.demo_ai import DemoAIService, get_demo_ai_service

router = APIRouter(prefix="/demo", tags=["demo"])
logger = get_logger(__name__)


@router.post("/ats", response_model=ATSResponse, status_code=status.HTTP_200_OK)
async def analyze_demo_ats(
    request: DemoResumeRequest,
    service: DemoAIService = Depends(get_demo_ai_service),
) -> ATSResponse:
    """Return a deterministic ATS analysis for demo use.

    Args:
        request: Validated resume text request.
        service: Injected deterministic demo service.

    Returns:
        A structured ATS analysis response.
    """
    response: ATSResponse = service.analyze_ats(request.resume_text)
    logger.info("demo_ats_completed", extra={"resume_character_count": len(request.resume_text)})
    return response


@router.post("/job-match", response_model=list[JobMatch], status_code=status.HTTP_200_OK)
async def match_demo_jobs(
    request: DemoResumeRequest,
    service: DemoAIService = Depends(get_demo_ai_service),
) -> list[JobMatch]:
    """Return five deterministic career matches for demo use.

    Args:
        request: Validated resume text request.
        service: Injected deterministic demo service.

    Returns:
        Five structured career matches ordered by descending match score.
    """
    response: list[JobMatch] = service.match_jobs(request.resume_text)
    logger.info("demo_job_match_completed", extra={"resume_character_count": len(request.resume_text)})
    return response


@router.post("/interview", response_model=InterviewPrep, status_code=status.HTTP_200_OK)
async def prepare_demo_interview(
    request: DemoResumeRequest,
    service: DemoAIService = Depends(get_demo_ai_service),
) -> InterviewPrep:
    """Return deterministic interview preparation questions for demo use.

    Args:
        request: Validated resume text request.
        service: Injected deterministic demo service.

    Returns:
        Structured interview preparation questions.
    """
    response: InterviewPrep = service.prepare_interview(request.resume_text)
    logger.info("demo_interview_completed", extra={"resume_character_count": len(request.resume_text)})
    return response
