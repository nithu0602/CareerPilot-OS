from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.job_fit import JobMatchAnalysis
from app.services.job_data import find_job
from app.services.job_fit_intelligence import analyze_and_persist, get_persisted_match

router = APIRouter(prefix="/jobs", tags=["job-fit"])


class JobAnalysisRequest(BaseModel):
    resume_id: str


def _job(job_id: str):
    return find_job(job_id)


@router.post("/{job_id}/analyze", response_model=JobMatchAnalysis)
async def analyze_job(job_id: str, request: JobAnalysisRequest) -> JobMatchAnalysis:
    job = _job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    try:
        return analyze_and_persist(request.resume_id, job)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{job_id}/match", response_model=JobMatchAnalysis)
async def get_match(job_id: str, resume_id: str):
    if _job(job_id) is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    try:
        return get_persisted_match(resume_id, job_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
