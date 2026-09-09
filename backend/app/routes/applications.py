from fastapi import APIRouter, HTTPException

from app.models.application import (
    Application,
    ApplicationCreateRequest,
    ApplicationUpdateRequest,
)
from app.services.application_service import (
    create_application,
    list_applications,
    prepare_application,
    update_application,
)
from app.services.application_service import _load

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=Application)
async def create(request: ApplicationCreateRequest):
    try:
        return create_application(request.resume_id, request.job_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("", response_model=list[Application])
async def get_all():
    return list_applications()


@router.get("/{application_id}", response_model=Application)
async def get_one(application_id: str):
    try:
        return _load(application_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{application_id}", response_model=Application)
async def patch(application_id: str, request: ApplicationUpdateRequest):
    try:
        return update_application(application_id, request.state)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{application_id}/prepare", response_model=Application)
async def prepare(application_id: str):
    try:
        return prepare_application(application_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
