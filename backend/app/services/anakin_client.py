from typing import Any
from urllib.parse import urlparse

import httpx

from app.config import get_settings
from app.models.job import JobRecord


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
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{self.api_url}/search",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"query": query, "location": location, "limit": min(limit, 15)},
            )
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, list):
            raise ValueError("Anakin search returned an invalid response.")
        return [item for item in payload if isinstance(item, dict)]

    async def scrape(self, url: str) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError("Anakin credentials are not configured.")
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{self.api_url}/url-scraper/scrape",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"url": url},
            )
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Anakin scrape returned an invalid response.")
        return payload

    @staticmethod
    def normalize(raw: dict[str, Any], retrieved_at: Any) -> JobRecord:
        source_url = raw.get("source_url") or raw.get("url")
        domain = None
        if source_url:
            try:
                domain = urlparse(source_url).netloc.lower().removeprefix("www.") or None
            except ValueError:
                domain = None
        return JobRecord.model_validate({
            "job_id": str(raw.get("job_id") or raw.get("id") or source_url or f"{raw.get('company', 'unknown')}-{raw.get('title', 'job')}"),
            "title": raw.get("title") or "Untitled role",
            "company": raw.get("company") or "Unknown company",
            "location": raw.get("location"),
            "employment_type": raw.get("employment_type"),
            "salary": raw.get("salary"),
            "deadline": raw.get("deadline"),
            "source_url": source_url,
            "description": raw.get("description"),
            "requirements": raw.get("requirements") or [],
            "responsibilities": raw.get("responsibilities") or [],
            "required_skills": raw.get("required_skills") or raw.get("skills") or [],
            "preferred_skills": raw.get("preferred_skills") or [],
            "eligibility": raw.get("eligibility"),
            "sponsorship_information": raw.get("sponsorship_information"),
            "provenance": {
                "source_url": source_url,
                "source_name": raw.get("source_name") or "Anakin",
                "retrieved_at": retrieved_at,
                "salary_source": raw.get("salary_source"),
                "deadline_source": raw.get("deadline_source"),
                "requirements_source": raw.get("requirements_source"),
                "sponsorship_source": raw.get("sponsorship_source"),
            },
            "mode": "live",
            "category": raw.get("category"),
            "experience_level": raw.get("experience_level"),
            "work_mode": raw.get("work_mode"),
            "source_domain": domain,
        })
