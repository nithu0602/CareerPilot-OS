from typing import Any
from urllib.parse import urlparse

import httpx

from app.config import get_settings
from app.models.job import JobRecord


def _normalize_url_for_matching(url: Any) -> str:
    if not url or not isinstance(url, str):
        return ""
    return url.strip().rstrip("/").lower()


class AnakinClient:
    """Small integration boundary for Anakin search and URL scraping."""

    def __init__(self, api_key: str | None = None, api_url: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.anakin_api_key
        self.api_url = (api_url or settings.anakin_api_url).rstrip("/")

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.api_url)

    async def search(self, query: str, location: str = "", limit: int = 10) -> list[dict[str, Any]]:
        if not self.configured:
            raise RuntimeError("Anakin credentials are not configured.")
        prompt = f"{query} in {location}" if location else query
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{self.api_url}/search",
                headers={"X-API-Key": self.api_key},
                json={"prompt": prompt, "limit": min(limit, 15)},
            )
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Anakin search returned an invalid response.")
        results = payload.get("results")
        if not isinstance(results, list):
            raise ValueError("Anakin search returned an invalid response.")
        return [item for item in results if isinstance(item, dict)]

    async def scrape(self, url: str) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError("Anakin credentials are not configured.")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.api_url}/url-scraper/scrape",
                headers={"X-API-Key": self.api_key},
                json={"url": url},
            )
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Anakin scrape returned an invalid response.")
        return payload

    @staticmethod
    def normalize(raw: dict[str, Any], retrieved_at: Any) -> JobRecord:
        nested_job: dict[str, Any] = {}
        jobs_list = raw.get("jobs")
        if isinstance(jobs_list, list):
            valid_jobs = [j for j in jobs_list if isinstance(j, dict)]
            if valid_jobs:
                requested_url_norm = _normalize_url_for_matching(raw.get("source_url") or raw.get("url"))
                if requested_url_norm:
                    for candidate in valid_jobs:
                        cand_url_norm = _normalize_url_for_matching(candidate.get("url") or candidate.get("source_url"))
                        if cand_url_norm and cand_url_norm == requested_url_norm:
                            nested_job = candidate
                            break
                if not nested_job:
                    nested_job = valid_jobs[0]

        source_url = (
            raw.get("source_url")
            or raw.get("url")
            or nested_job.get("source_url")
            or nested_job.get("url")
        )
        domain = None
        if source_url:
            try:
                domain = urlparse(source_url).netloc.lower().removeprefix("www.") or None
            except ValueError:
                domain = None

        company = nested_job.get("company") or raw.get("company") or "Unknown company"
        title = nested_job.get("title") or raw.get("title") or "Untitled role"
        location = nested_job.get("location") or raw.get("location")
        salary = nested_job.get("salary") or raw.get("salary")
        description = nested_job.get("description") or raw.get("description")
        employment_type = (
            nested_job.get("jobType")
            or nested_job.get("employment_type")
            or nested_job.get("job_type")
            or raw.get("employment_type")
            or raw.get("jobType")
            or raw.get("job_type")
        )

        job_id = str(
            raw.get("job_id")
            or raw.get("id")
            or nested_job.get("job_id")
            or nested_job.get("id")
            or source_url
            or f"{company}-{title}"
        )

        return JobRecord.model_validate({
            "job_id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "employment_type": employment_type,
            "salary": salary,
            "deadline": nested_job.get("deadline") or raw.get("deadline"),
            "source_url": source_url,
            "description": description,
            "requirements": nested_job.get("requirements") or raw.get("requirements") or [],
            "responsibilities": nested_job.get("responsibilities") or raw.get("responsibilities") or [],
            "required_skills": (
                nested_job.get("required_skills")
                or nested_job.get("skills")
                or raw.get("required_skills")
                or raw.get("skills")
                or []
            ),
            "preferred_skills": nested_job.get("preferred_skills") or raw.get("preferred_skills") or [],
            "eligibility": nested_job.get("eligibility") or raw.get("eligibility"),
            "sponsorship_information": (
                nested_job.get("sponsorship_information")
                or raw.get("sponsorship_information")
            ),
            "provenance": {
                "source_url": source_url,
                "source_name": raw.get("source_name") or nested_job.get("source_name") or "Anakin",
                "retrieved_at": retrieved_at,
                "salary_source": raw.get("salary_source") or nested_job.get("salary_source"),
                "deadline_source": raw.get("deadline_source") or nested_job.get("deadline_source"),
                "requirements_source": raw.get("requirements_source") or nested_job.get("requirements_source"),
                "sponsorship_source": raw.get("sponsorship_source") or nested_job.get("sponsorship_source"),
            },
            "mode": "live",
            "category": raw.get("category") or nested_job.get("category"),
            "experience_level": raw.get("experience_level") or nested_job.get("experience_level"),
            "work_mode": raw.get("work_mode") or nested_job.get("work_mode"),
            "source_domain": domain,
        })

