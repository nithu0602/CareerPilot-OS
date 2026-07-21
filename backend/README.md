# CareerPilot OS Backend

CareerPilot OS is a FastAPI backend with versioned APIs, central Pydantic configuration, SQLAlchemy connection management, CORS, lifecycle logging, resume parsing, structured resume analysis, and deterministic demo services.

## Setup

1. Create and activate a Python 3.13 virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set values for the environment.
4. Start the service with `uvicorn app.main:app --reload`.
5. Open Swagger UI at `http://127.0.0.1:8000/docs`.

## API endpoints

### Health check

`GET /api/v1/health`

```json
{
  "status": "healthy",
  "service": "CareerPilot Backend",
  "version": "1.0.0"
}
```

### Resume upload and parsing

`POST /api/v1/resume/upload`

Swagger payload: submit a `multipart/form-data` request with a `file` field containing a PDF or DOCX file no larger than 5 MB.

### Structured OpenAI resume analysis

`POST /api/v1/analysis/resume`

Swagger payload:

```json
{
  "resume_text": "Data analyst with Python, SQL, Power BI, and stakeholder management experience."
}
```

This endpoint requires `OPENAI_API_KEY` and returns a validated candidate-profile model.

### Aggregated deterministic dashboard analysis

`POST /api/v1/dashboard/analyze`

Swagger payload:

```json
{
  "resume_text": "John Doe\nData analyst with Python, SQL, Power BI, and stakeholder management experience. Built dashboards and delivered projects."
}
```

Returns one dashboard object containing the candidate name, deterministic ATS analysis, five job matches, interview questions, and the orchestration processing time. This endpoint reuses the existing demo services and makes no API or network calls.

### Deterministic demo ATS analysis

`POST /api/v1/demo/ats`

Swagger payload:

```json
{
  "resume_text": "Data analyst with Python, SQL, Power BI, and stakeholder management experience. Built dashboards and delivered projects."
}
```

Returns an overall ATS score, section-level scores, three strengths, and three practical improvements. No API key or network request is used.

### Deterministic demo job matches

`POST /api/v1/demo/job-match`

Swagger payload:

```json
{
  "resume_text": "Software engineer with Python, FastAPI, SQL, Docker, AWS, Git, and Agile delivery experience."
}
```

Returns five career recommendations, each with a deterministic match percentage, salary range, and evidence-based reason.

### Deterministic demo interview preparation

`POST /api/v1/demo/interview`

Swagger payload:

```json
{
  "resume_text": "Machine learning engineer with Python, scikit-learn, Docker, Git, and project delivery experience."
}
```

Returns three technical, three behavioural, and three resume-focused interview questions. No API key or network request is used.
