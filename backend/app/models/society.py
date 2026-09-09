from pydantic import BaseModel


class SocietyAnalyzeRequest(BaseModel):
    resume_id: str
    job_id: str | None = None
    interview_id: str | None = None
