from fastapi import APIRouter

from app.models.career import CareerActionsResponse, CareerDashboard, CareerPlanRequest, CareerPlanResponse
from app.services.career_strategist import dashboard, generate_actions, plan

router = APIRouter(prefix="/career", tags=["career"])


@router.get("/dashboard", response_model=CareerDashboard)
async def get_dashboard(resume_id: str | None = None) -> CareerDashboard:
    return dashboard(resume_id)


@router.get("/next-actions", response_model=CareerActionsResponse)
async def get_next_actions(resume_id: str | None = None) -> CareerActionsResponse:
    return generate_actions(resume_id)


@router.post("/plan", response_model=CareerPlanResponse)
async def create_plan(request: CareerPlanRequest) -> CareerPlanResponse:
    return plan(request.resume_id)
