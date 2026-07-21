"""Validation utilities for supported resume upload files."""

from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.schemas.resume import ResumeFileType

MAX_RESUME_FILE_SIZE_BYTES = 5 * 1024 * 1024
SUPPORTED_MEDIA_TYPES: dict[ResumeFileType, str] = {
    ResumeFileType.PDF: "application/pdf",
    ResumeFileType.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
SUPPORTED_EXTENSIONS: dict[str, ResumeFileType] = {
    ".pdf": ResumeFileType.PDF,
    ".docx": ResumeFileType.DOCX,
}


@dataclass(frozen=True)
class ValidatedResumeUpload:
    """Trusted upload metadata and bytes after validation has completed."""

    filename: str
    file_type: ResumeFileType
    media_type: str
    content: bytes

    @property
    def file_size_bytes(self) -> int:
        """Return the validated byte length."""
        return len(self.content)


async def validate_resume_upload(upload: UploadFile) -> ValidatedResumeUpload:
    """Validate a resume's name, extension, declared MIME type, and byte size."""
    if not upload.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required for resume uploads.",
        )

    filename = Path(upload.filename).name
    extension = Path(filename).suffix.lower()
    file_type = SUPPORTED_EXTENSIONS.get(extension)
    if file_type is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF and DOCX resume files are supported.",
        )

    media_type = (upload.content_type or "").lower()
    expected_media_type = SUPPORTED_MEDIA_TYPES[file_type]
    if media_type != expected_media_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"The declared MIME type must be {expected_media_type} for {extension} files.",
        )

    content = await upload.read(MAX_RESUME_FILE_SIZE_BYTES + 1)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded resume file is empty.",
        )
    if len(content) > MAX_RESUME_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Resume uploads must not exceed 5 MB.",
        )

    return ValidatedResumeUpload(
        filename=filename,
        file_type=file_type,
        media_type=media_type,
        content=content,
    )
