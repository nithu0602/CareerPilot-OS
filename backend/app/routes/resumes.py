import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import get_settings
from app.models.resume import ResumeAnalysis, ResumeUploadResponse
from app.services.resume_intelligence import analyze_resume

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _dirs() -> tuple[Path, Path]:
    settings = get_settings()
    resume_dir = Path(settings.resume_storage_dir)
    analysis_dir = Path(settings.analysis_storage_dir)
    resume_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    return resume_dir, analysis_dir


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...)) -> ResumeUploadResponse:
    if file.content_type != "application/pdf" or not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")
    settings = get_settings()
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded PDF is empty.")
    if len(content) > settings.max_resume_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Resume must be smaller than {settings.max_resume_size_mb} MB.")
    resume_id = str(uuid4())
    resume_dir, _ = _dirs()
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", file.filename)
    (resume_dir / f"{resume_id}.pdf").write_bytes(content)
    (resume_dir / f"{resume_id}.json").write_text(json.dumps({"filename": safe_name}), encoding="utf-8")
    return ResumeUploadResponse(resume_id=resume_id, filename=safe_name, status="uploaded")


@router.post("/{resume_id}/analyze", response_model=ResumeAnalysis)
async def analyze_uploaded_resume(resume_id: str) -> ResumeAnalysis:
    resume_dir, analysis_dir = _dirs()
    metadata_path = resume_dir / f"{resume_id}.json"
    pdf_path = resume_dir / f"{resume_id}.pdf"
    if not metadata_path.exists() or not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Resume not found.")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    try:
        result = analyze_resume(pdf_path, resume_id, metadata["filename"])
    except (ValueError, OSError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    result["analyzed_at"] = datetime.now(timezone.utc)
    (analysis_dir / f"{resume_id}.json").write_text(json.dumps(result, default=str), encoding="utf-8")
    return ResumeAnalysis.model_validate(result)


@router.get("/{resume_id}", response_model=ResumeAnalysis)
async def get_resume_analysis(resume_id: str) -> ResumeAnalysis:
    _, analysis_dir = _dirs()
    path = analysis_dir / f"{resume_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Resume analysis not found.")
    try:
        return ResumeAnalysis.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=500, detail="Stored resume analysis is malformed.") from exc
