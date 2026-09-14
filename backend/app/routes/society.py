import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.agents.society_orchestrator import SocietyOrchestrator
from app.config import get_settings
from app.models.job_fit import JobMatchAnalysis
from app.models.resume import ResumeAnalysis
from app.models.society import SocietyAnalyzeRequest
from app.schemas.society import (
    SocietyContext,
    SocietyDeliberateRequest,
    SocietyDeliberateResponse,
    SocietyResult,
)
from app.services.application_service import list_applications
from app.services.career_strategist import generate_actions
from app.services.interview_agent import latest_completed_results, results as get_interview_results
from app.services.job_data import find_job
from app.services.job_fit_intelligence import get_persisted_match

router = APIRouter(prefix="/society", tags=["society"])


def _load_resume(resume_id: str) -> ResumeAnalysis:
    path = Path(get_settings().analysis_storage_dir) / f"{resume_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Resume analysis not found.")
    try:
        return ResumeAnalysis.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Stored resume analysis is malformed.") from exc


def _load_match(resume_id: str, job_id: str) -> JobMatchAnalysis:
    try:
        return get_persisted_match(resume_id, job_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Job fit analysis not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Stored job fit analysis is malformed.") from exc


def _load_optional_match(resume_id: str, job_id: str | None) -> JobMatchAnalysis | None:
    """Chat can discuss a selected role before its fit has been persisted."""
    if not job_id:
        return None
    try:
        return _load_match(resume_id, job_id)
    except HTTPException as exc:
        if exc.status_code == 404:
            return None
        raise


def _load_application_context(resume_id: str, job_id: str | None) -> dict | None:
    try:
        apps = list_applications()
        for app in apps:
            if app.resume_id == resume_id and (job_id is None or app.job_id == job_id):
                return app.model_dump(mode="json")
    except Exception:
        pass
    return None


@router.post("/analyze", response_model=SocietyResult)
async def analyze_society(request: SocietyAnalyzeRequest) -> SocietyResult:
    resume = _load_resume(request.resume_id)
    job = find_job(request.job_id) if request.job_id else None
    if request.job_id and job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    fit = _load_match(request.resume_id, request.job_id) if request.job_id else None
    interview = None
    if request.interview_id:
        try:
            interview = get_interview_results(request.interview_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="Interview not found.") from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Interview results are not available.") from exc
        if interview.resume_id != request.resume_id:
            raise HTTPException(status_code=422, detail="Interview does not belong to the supplied resume.")
        if request.job_id and interview.job_id != request.job_id:
            raise HTTPException(status_code=422, detail="Interview does not belong to the supplied job.")

    if interview is None:
        interview = latest_completed_results(request.resume_id, request.job_id)
    actions = generate_actions(request.resume_id)
    app_ctx = _load_application_context(request.resume_id, request.job_id)
    context = SocietyContext(
        resume_analysis=resume.model_dump(mode="json"),
        job_record=job.model_dump(mode="json") if job else {},
        deterministic_fit_analysis=fit.model_dump(mode="json") if fit else None,
        skill_gaps=[gap.model_dump(mode="json") if hasattr(gap, "model_dump") else gap for gap in fit.skill_gaps] if fit else [],
        interview_context=interview.model_dump(mode="json") if interview else None,
        interview_results=interview.model_dump(mode="json") if interview else None,
        application_context=app_ctx,
        career_actions=actions.model_dump(mode="json"),
        resume_id=request.resume_id,
    )
    return SocietyOrchestrator().analyze(context)


@router.post("/deliberate", response_model=SocietyDeliberateResponse)
async def deliberate_society(request: SocietyDeliberateRequest) -> SocietyDeliberateResponse:
    resume = _load_resume(request.resume_id)
    job = find_job(request.job_id) if request.job_id else None
    if request.job_id and job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    fit = _load_optional_match(request.resume_id, request.job_id)
    interview = None
    if request.interview_id:
        try:
            interview = get_interview_results(request.interview_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="Interview not found.") from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Interview results are not available.") from exc
        if interview.resume_id != request.resume_id:
            raise HTTPException(status_code=422, detail="Interview does not belong to the supplied resume.")
        if request.job_id and interview.job_id != request.job_id:
            raise HTTPException(status_code=422, detail="Interview does not belong to the supplied job.")

    if interview is None:
        interview = latest_completed_results(request.resume_id, request.job_id)
    actions = generate_actions(request.resume_id)
    app_ctx = _load_application_context(request.resume_id, request.job_id)
    context = SocietyContext(
        resume_analysis=resume.model_dump(mode="json"),
        job_record=job.model_dump(mode="json") if job else {},
        deterministic_fit_analysis=fit.model_dump(mode="json") if fit else None,
        skill_gaps=[gap.model_dump(mode="json") if hasattr(gap, "model_dump") else gap for gap in fit.skill_gaps] if fit else [],
        interview_context=interview.model_dump(mode="json") if interview else None,
        interview_results=interview.model_dump(mode="json") if interview else None,
        application_context=app_ctx,
        career_actions=actions.model_dump(mode="json"),
        resume_id=request.resume_id,
    )
    return SocietyOrchestrator().deliberate(context, request.message, request.history)

