from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.logging_config import configure_logging, get_logger
from app.routes.health import router as health_router
from app.routes.resumes import router as resumes_router
from app.routes.jobs import router as jobs_router
from app.routes.job_fit import router as job_fit_router
from app.routes.interviews import router as interviews_router
from app.routes.career import router as career_router
from app.routes.applications import router as applications_router
from app.routes.society import router as society_router

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("CareerPilot backend starting", extra={"environment": settings.environment})
    yield
    logger.info("CareerPilot backend stopping")


app = FastAPI(
    title="CareerPilot API",
    version="0.1.0",
    description="Minimal backend foundation for the CareerPilot MVP.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(resumes_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(job_fit_router, prefix="/api")
app.include_router(interviews_router, prefix="/api")
app.include_router(career_router, prefix="/api")
app.include_router(applications_router, prefix="/api")
app.include_router(society_router, prefix="/api")
