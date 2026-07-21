"""Service health endpoint."""

from fastapi import APIRouter, status

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    """Return the backend service status and version."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }
