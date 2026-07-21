"""Pydantic response schemas for resume ingestion."""

from enum import StrEnum

from pydantic import BaseModel, Field


class ResumeFileType(StrEnum):
    """Supported resume document formats."""

    PDF = "pdf"
    DOCX = "docx"


class ResumeUploadResponse(BaseModel):
    """Structured text and metadata extracted from an uploaded resume."""

    filename: str = Field(min_length=1)
    file_type: ResumeFileType
    file_size_bytes: int = Field(ge=1, le=5 * 1024 * 1024)
    page_count: int | None = Field(default=None, ge=1)
    character_count: int = Field(ge=0)
    word_count: int = Field(ge=0)
    raw_text: str
