# CareerPilot OS Backend

Phase 1 provides the production foundation for the FastAPI service: central Pydantic Settings configuration, SQLAlchemy connection management, CORS, application lifecycle logging, and the versioned health endpoint.

## Setup

1. Create and activate a Python 3.12 virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and adjust values for the environment.
4. Start the service with `uvicorn app.main:app --reload`.

## Health check

`GET /api/v1/health` returns:

```json
{
  "status": "healthy",
  "service": "CareerPilot Backend",
  "version": "1.0.0"
}
```
