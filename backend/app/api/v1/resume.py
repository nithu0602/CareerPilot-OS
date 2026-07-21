"""Resume upload API endpoints."""

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.logging import get_logger
from app.schemas.resume import ResumeUploadResponse
from app.services.resume_parser import ResumeParseError, parse_resume
from app.utils.file_validation import validate_resume_upload

router = APIRouter(prefix="/resume", tags=["resume"])
logger = get_logger(__name__)


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_resume(file: UploadFile = File(...)) -> ResumeUploadResponse:
    """Validate and parse a PDF or DOCX resume without persisting the uploaded file."""
    validated_upload = await validate_resume_upload(file)
    try:
        result = parse_resume(validated_upload)
    except ResumeParseError as error:
        logger.warning("resume_parse_failed", extra={"filename": validated_upload.filename})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    finally:
        await file.close()

    logger.info(
        "resume_parsed",
        extra={
                "resume_filename": result.filename,
                "resume_file_type": result.file_type,
                "resume_file_size_bytes": result.file_size_bytes,
                "resume_page_count": result.page_count,
}
    )
    return result
