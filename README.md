# CareerPilot

CareerPilot is a one-week hackathon MVP for international students and graduates. This repository contains the final hardened MVP: Resume Intelligence, demo-safe Job Intelligence, explainable Job + Fit Intelligence, a text-only Adaptive Interview Agent, a deterministic Career Strategist, and human-controlled application preparation/state tracking.

## Prerequisites

- Node.js 20+
- Python 3.11+

## Setup

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

Health endpoint: `http://localhost:8000/api/health`

Resume analysis accepts text-based PDFs up to 10 MB. Uploaded files and JSON analyses are stored locally under `backend/data/` for this MVP and are ignored by Git.

Job Intelligence defaults to the cached, synthetic dataset in `backend/data/demo_jobs.json`. Optional Anakin live mode uses `ANAKIN_API_KEY` and `ANAKIN_API_URL`; live failures fall back to the demo dataset.

With `ANAKIN_API_URL=https://api.anakin.io/v1`, the client uses `POST /v1/search` and the inline `POST /v1/url-scraper/scrape` endpoint. No live request is made without explicit credentials.

After analyzing a resume, select a cached job and choose **Analyze fit for my resume**. Phase 4 computes a deterministic score, skill gaps, source-grounded sponsorship evidence, and a recommended next step. Match JSON is stored under `backend/data/jobs/matches/` for this MVP.

Phase 5 adds a five-question maximum text interview. It uses deterministic answer evaluation and adaptive follow-ups; no external LLM or paid API is required.

Phase 6 adds a career command center that combines available resume, job match, skill-gap, sponsorship, deadline, and interview evidence into prioritized recommendations. It never submits applications or performs external actions.

Phase 7 adds manual application preparation and local state tracking. Preparation is grounded in resume and job evidence; the candidate opens the source URL and submits externally.

For a reliable demo, use cached demo mode: upload a text-based PDF, search the cached jobs, analyze one job fit, run the five-question interview, review the Career Strategist's next action, then create and prepare an application. The **Open application** link only opens the source URL; CareerPilot never submits an external application.

### Frontend

In a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open `http://localhost:3000`. The dashboard displays whether it can reach the backend health endpoint.

## Supabase

The initial schema is in `supabase/schema.sql`. It defines only the core MVP entities and does not require authentication, vector search, or additional infrastructure.

## Tests

```powershell
cd backend
python -m pytest tests -q
```

## Scope

The final MVP intentionally does not include notifications, project management, audio, video, speech-to-text, emotion analysis, OCR, LangGraph, embeddings, pgvector, browser automation, automatic application submission, external-site login automation, CAPTCHA handling, or ML predictions. Applications remain human-controlled.
