from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.models.job import JobRecord, JobSearchRequest, JobSearchResponse
from app.services.anakin_client import AnakinClient
from app.services.job_categories import (
    CATEGORY_LABELS,
    DEFAULT_EXPERIENCE,
    DEFAULT_LOCATION,
    DEFAULT_WORK_MODE,
    EXPERIENCE_LABELS,
    UK_LOCATIONS,
    WORK_MODE_LABELS,
    build_search_queries,
)
from app.services.job_data import (
    cache_live_jobs,
    deduplicate_jobs,
    diversify_by_source,
    filter_jobs,
    find_job,
    load_demo_jobs,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])

MAX_LIVE_RESULTS = 20
MAX_QUERIES = 3
RESULTS_PER_QUERY = 10


@router.get("/options")
async def job_search_options() -> dict:
    """Shared category/location/experience/work-mode config for the frontend."""
    return {
        "categories": [{"value": value, "label": label} for value, label in CATEGORY_LABELS.items()],
        "locations": UK_LOCATIONS,
        "default_location": DEFAULT_LOCATION,
        "experience_levels": [{"value": value, "label": label} for value, label in EXPERIENCE_LABELS.items()],
        "default_experience": DEFAULT_EXPERIENCE,
        "work_modes": [{"value": value, "label": label} for value, label in WORK_MODE_LABELS.items()],
        "default_work_mode": DEFAULT_WORK_MODE,
    }


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest) -> JobSearchResponse:
    demo = load_demo_jobs()
    if request.mode == "demo":
        jobs = filter_jobs(demo, request.role, request.location, request.keyword, request.category, request.experience, request.work_mode)
        return JobSearchResponse(jobs=jobs, mode="demo", total=len(jobs))

    client = AnakinClient()
    if not client.configured:
        jobs = filter_jobs(demo, request.role, request.location, request.keyword, request.category, request.experience, request.work_mode)
        return JobSearchResponse(jobs=jobs, mode="fallback", fallback_reason="Anakin credentials are not configured.", total=len(jobs))

    location = request.location or DEFAULT_LOCATION
    queries = build_search_queries(request.category, location, request.experience, request.keyword, max_queries=MAX_QUERIES)
    try:
        retrieved_at = datetime.now(timezone.utc)
        raw_results: list[dict] = []
        seen_urls: set[str] = set()
        for query in queries:
            batch = await client.search(query, location, limit=RESULTS_PER_QUERY)
            for result in batch:
                url = (result.get("source_url") or result.get("url") or "").strip().lower()
                if url and url in seen_urls:
                    continue
                if url:
                    seen_urls.add(url)
                raw_results.append(result)

        normalized: list[JobRecord] = []
        for result in raw_results:
            url = result.get("source_url") or result.get("url")
            scraped = await client.scrape(url) if url else result
            merged = {**result, **scraped}
            merged.setdefault("category", request.category)
            merged.setdefault("experience_level", request.experience)
            merged.setdefault("work_mode", request.work_mode)
            normalized.append(client.normalize(merged, retrieved_at))

        jobs = deduplicate_jobs(normalized)
        jobs = diversify_by_source(jobs)
        jobs = jobs[:MAX_LIVE_RESULTS]
        cache_live_jobs(jobs)
        note = f"{len(jobs)} relevant opportunit{'y' if len(jobs) == 1 else 'ies'} found."
        return JobSearchResponse(jobs=jobs, mode="live", total=len(jobs), queries_used=queries, result_note=note)
    except (httpx.HTTPError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        jobs = filter_jobs(demo, request.role, request.location, request.keyword, request.category, request.experience, request.work_mode)
        return JobSearchResponse(jobs=jobs, mode="fallback", fallback_reason=f"Live Anakin request failed: {exc}", total=len(jobs), queries_used=queries)


@router.get("", response_model=list[JobRecord])
async def list_jobs(
    role: str = Query(default=""),
    location: str = Query(default=""),
    keyword: str = Query(default=""),
    category: str | None = Query(default=None),
    experience: str | None = Query(default=None),
    work_mode: str | None = Query(default=None),
) -> list[JobRecord]:
    return filter_jobs(load_demo_jobs(), role, location, keyword, category, experience, work_mode)


@router.get("/{job_id}", response_model=JobRecord)
async def get_job(job_id: str) -> JobRecord:
    job = find_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
