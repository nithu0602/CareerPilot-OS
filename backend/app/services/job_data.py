import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from app.config import get_settings
from app.models.job import JobRecord


def demo_jobs_path() -> Path:
    return Path(__file__).parents[2] / "data" / "demo_jobs.json"


def load_demo_jobs() -> list[JobRecord]:
    records = json.loads(demo_jobs_path().read_text(encoding="utf-8"))
    retrieved_at = datetime.now(timezone.utc)
    return [
        JobRecord.model_validate({**record, "provenance": {**record.get("provenance", {}), "retrieved_at": retrieved_at}, "mode": "demo"})
        for record in records
    ]


def load_cached_live_jobs() -> list[JobRecord]:
    path = Path(get_settings().jobs_cache_dir) / "latest_live.json"
    if not path.exists():
        return []
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
        return [JobRecord.model_validate(record) for record in records]
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return []


def find_job(job_id: str) -> JobRecord | None:
    return next((job for job in [*load_demo_jobs(), *load_cached_live_jobs()] if job.job_id == job_id), None)


def filter_jobs(
    jobs: list[JobRecord],
    role: str = "",
    location: str = "",
    keyword: str = "",
    category: str | None = None,
    experience: str | None = None,
    work_mode: str | None = None,
) -> list[JobRecord]:
    terms = [term.lower() for term in (role, location, keyword) if term.strip()]
    filtered = jobs
    if terms:
        filtered = []
        for job in jobs:
            haystack = " ".join([
                job.title, job.company, job.location or "", job.description or "",
                *job.required_skills, *job.preferred_skills,
            ]).lower()
            if all(term in haystack for term in terms):
                filtered.append(job)
    if category:
        normalized_category = category.strip().upper()
        filtered = [job for job in filtered if (job.category or "").upper() == normalized_category]
    if experience and experience.strip().upper() not in ("", "ANY"):
        normalized_experience = experience.strip().upper()
        filtered = [job for job in filtered if (job.experience_level or "").upper() == normalized_experience]
    if work_mode and work_mode.strip().upper() not in ("", "ANY"):
        normalized_mode = work_mode.strip().upper()
        filtered = [job for job in filtered if (job.work_mode or "").upper() == normalized_mode]
    return filtered


def source_domain(url: str | None) -> str | None:
    if not url:
        return None
    try:
        netloc = urlparse(url).netloc
    except ValueError:
        return None
    return netloc.lower().removeprefix("www.") or None


def deduplicate_jobs(jobs: list[JobRecord]) -> list[JobRecord]:
    unique: dict[str, JobRecord] = {}
    for job in jobs:
        key = (job.source_url or f"{job.company}:{job.title}:{job.location or ''}").lower().strip()
        if key not in unique:
            unique[key] = job
    return list(unique.values())


def diversify_by_source(jobs: list[JobRecord]) -> list[JobRecord]:
    """Rank preference for source diversity, without discarding relevant results.

    Interleaves jobs so that consecutive same-domain results are spread out
    when other domains are available. Relevance order within a domain is
    preserved; nothing is dropped.
    """
    buckets: dict[str, list[JobRecord]] = {}
    order: list[str] = []
    for job in jobs:
        domain = job.source_domain or source_domain(job.source_url) or "unknown"
        if domain not in buckets:
            buckets[domain] = []
            order.append(domain)
        buckets[domain].append(job)

    if len(order) <= 1:
        return jobs

    result: list[JobRecord] = []
    while any(buckets[domain] for domain in order):
        for domain in order:
            if buckets[domain]:
                result.append(buckets[domain].pop(0))
    return result


def cache_live_jobs(jobs: list[JobRecord]) -> None:
    cache_dir = Path(get_settings().jobs_cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "latest_live.json").write_text(
        json.dumps([job.model_dump(mode="json") for job in jobs], indent=2),
        encoding="utf-8",
    )
