from fastapi import APIRouter, HTTPException

from app.models.interview import (
    InterviewAnswerRequest,
    InterviewAnswerResponse,
    InterviewResults,
    InterviewSession,
    InterviewStartRequest,
)
from app.services.interview_agent import answer_interview, results, start_interview

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/start", response_model=InterviewSession)
async def start(request: InterviewStartRequest):
    try:
        return start_interview(request.resume_id, request.job_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{interview_id}/answer", response_model=InterviewAnswerResponse)
async def answer(interview_id: str, request: InterviewAnswerRequest):
    try:
        session, evaluation = answer_interview(interview_id, request.answer)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    next_question = None if session.status == "completed" else session.current_question
    return InterviewAnswerResponse(
        interview_id=interview_id, evaluation=evaluation, next_question=next_question,
        progress=round(len(session.turns) / session.max_questions * 100),
        status=session.status,
    )


@router.get("/{interview_id}/results", response_model=InterviewResults)
async def get_results(interview_id: str):
    try:
        return results(interview_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
