"""Aggregated dashboard analysis endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.logging import get_logger
from app.schemas.dashboard import DashboardRequest, DashboardResponse
from app.services.dashboard_service import DashboardService, get_dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = get_logger(__name__)


@router.post("/analyze", response_model=DashboardResponse, status_code=status.HTTP_200_OK)
async def analyze_dashboard(
    request: DashboardRequest,
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DashboardResponse:
    """Return all deterministic demo analyses through one frontend request.

    Args:
        request: Validated raw resume text.
        service: Injected dashboard orchestrator.

    Returns:
        A single dashboard response with ATS, job-match, and interview outputs.

    Raises:
        HTTPException: If the deterministic dashboard workflow cannot complete.
    """
    logger.info("dashboard_request", extra={"resume_character_count": len(request.resume_text)})
    try:
        response: DashboardResponse = service.analyze(request.resume_text)
    except Exception as error:
        logger.exception("dashboard_failed", extra={"resume_character_count": len(request.resume_text)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dashboard analysis could not be completed.",
        ) from error

    logger.info("dashboard_completed", extra={"processing_time_ms": response.processing_time_ms})
    logger.info("processing_time", extra={"processing_time_ms": response.processing_time_ms})
    return response
