"""Structured AI resume analysis API endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.logging import get_logger
from app.schemas.analysis import AnalysisResponse, ResumeAnalysisRequest
from app.services.ai_resume_analyzer import (
    OpenAIAnalysisResponseError,
    OpenAIAnalysisTimeout,
    OpenAIAnalysisUnavailable,
    OpenAIConfigurationError,
    ResumeAnalyzer,
    get_resume_analyzer,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])
logger = get_logger(__name__)


@router.post(
    "/resume",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_resume(
    request: ResumeAnalysisRequest,
    analyzer: ResumeAnalyzer = Depends(get_resume_analyzer),
) -> AnalysisResponse:
    """Analyze raw resume text and return only a validated structured model."""
    try:
        return await analyzer.analyze(request.resume_text)
    except OpenAIConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Resume analysis is not configured.",
        ) from error
    except OpenAIAnalysisTimeout as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Resume analysis timed out. Please try again.",
        ) from error
    except OpenAIAnalysisUnavailable as error:
        logger.warning("resume_analysis_unavailable")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume analysis is temporarily unavailable. Please try again.",
        ) from error
    except OpenAIAnalysisResponseError as error:
        logger.warning("resume_analysis_invalid_response")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Resume analysis could not produce a valid structured result.",
        ) from error
