import asyncio
from datetime import datetime, timezone
from typing import Any

from fastapi.testclient import TestClient

from app.main import app
from app.models.job import JobRecord
from app.services.anakin_client import AnakinClient
from app.services.job_data import deduplicate_jobs, load_demo_jobs


def test_demo_job_loading_and_missing_fields():
    jobs = load_demo_jobs()
    assert len(jobs) == 20
    assert any(job.salary is None for job in jobs)
    assert any(job.deadline is None for job in jobs)
    assert all(job.provenance.source_name == "CareerPilot demo dataset" for job in jobs)


def test_demo_dataset_covers_categories_and_uk_locations():
    jobs = load_demo_jobs()
    categories = {job.category for job in jobs}
    assert {"DATA", "IT_SOFTWARE", "BUSINESS", "HR"}.issubset(categories)
    locations = {job.location for job in jobs if job.location}
    assert any("London" in location for location in locations)
    assert any("Nottingham" in location for location in locations)
    assert any("Manchester" in location for location in locations)
    assert any("Birmingham" in location for location in locations)


def test_job_deduplication_preserves_first_record():
    jobs = load_demo_jobs()
    assert len(deduplicate_jobs([jobs[0], jobs[0]])) == 1


def test_anakin_response_normalization_preserves_provenance():
    job = AnakinClient.normalize({
        "id": "live-1", "title": "Data Analyst", "company": "Example",
        "url": "https://example.com/job", "skills": ["SQL"],
        "salary_source": "Employer page",
    }, datetime.now(timezone.utc))
    assert isinstance(job, JobRecord)
    assert job.job_id == "live-1"
    assert job.source_url == "https://example.com/job"
    assert job.provenance.salary_source == "Employer page"
    assert job.salary is None


def test_anakin_uses_official_search_and_inline_scraper_paths(monkeypatch):
    calls: list[tuple[str, str]] = []

    class MockResponse:
        def __init__(self, payload: Any):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, path, **kwargs):
            calls.append((path, kwargs["json"].get("url", "")))
            if path.endswith("/search"):
                return MockResponse([{"id": "live-1", "title": "Data Analyst", "company": "Example"}])
            return MockResponse({"description": "Scraped job details"})

    monkeypatch.setattr("app.services.anakin_client.httpx.AsyncClient", lambda timeout: MockClient())
    client = AnakinClient(api_key="test-key", api_url="https://api.anakin.io/v1")
    asyncio.run(client.search("data analyst"))
    asyncio.run(client.scrape("https://example.com/job"))
    assert calls == [
        ("https://api.anakin.io/v1/search", ""),
        ("https://api.anakin.io/v1/url-scraper/scrape", "https://example.com/job"),
    ]


def test_demo_search_api_and_detail():
    with TestClient(app) as client:
        response = client.post("/api/jobs/search", json={"role": "data analyst", "mode": "demo"})
        assert response.status_code == 200
        assert response.json()["mode"] == "demo"
        assert response.json()["total"] >= 1
        job_id = response.json()["jobs"][0]["job_id"]
        detail = client.get(f"/api/jobs/{job_id}")
        assert detail.status_code == 200


def test_live_mode_without_credentials_falls_back_to_demo():
    with TestClient(app) as client:
        response = client.post("/api/jobs/search", json={"mode": "live"})
    assert response.status_code == 200
    assert response.json()["mode"] == "fallback"
    assert response.json()["total"] == 20


def test_search_options_endpoint_exposes_shared_config():
    with TestClient(app) as client:
        response = client.get("/api/jobs/options")
    assert response.status_code == 200
    data = response.json()
    assert data["default_location"] == "London"
    assert data["default_experience"] == "GRADUATE"
    values = {item["value"] for item in data["categories"]}
    assert {"DATA", "IT_SOFTWARE", "BUSINESS", "HR"}.issubset(values)


def test_category_filter_narrows_demo_results():
    with TestClient(app) as client:
        response = client.post("/api/jobs/search", json={"mode": "demo", "category": "HR"})
    assert response.status_code == 200
    jobs = response.json()["jobs"]
    assert jobs
    assert all(job["category"] == "HR" for job in jobs)


def test_experience_filter_narrows_demo_results():
    with TestClient(app) as client:
        response = client.post("/api/jobs/search", json={"mode": "demo", "experience": "INTERNSHIP"})
    assert response.status_code == 200
    jobs = response.json()["jobs"]
    assert jobs
    assert all(job["experience_level"] == "INTERNSHIP" for job in jobs)


def test_work_mode_filter_narrows_demo_results():
    with TestClient(app) as client:
        response = client.post("/api/jobs/search", json={"mode": "demo", "work_mode": "REMOTE"})
    assert response.status_code == 200
    jobs = response.json()["jobs"]
    assert jobs
    assert all(job["work_mode"] == "REMOTE" for job in jobs)


def test_london_is_default_search_location():
    from app.services.job_categories import DEFAULT_LOCATION, build_search_queries
    assert DEFAULT_LOCATION == "London"
    queries = build_search_queries("DATA", DEFAULT_LOCATION, "GRADUATE", "", max_queries=3)
    assert all("London" in query for query in queries)


def test_uk_location_is_respected_and_not_replaced():
    from app.services.job_categories import build_search_queries, is_uk_location
    assert is_uk_location("United Kingdom")
    assert is_uk_location("Manchester")
    assert not is_uk_location("Toronto")
    queries = build_search_queries("IT_SOFTWARE", "United Kingdom", "GRADUATE", "", max_queries=2)
    assert all("Canada" not in query for query in queries)
    assert all("United Kingdom" in query for query in queries)


def test_query_expansion_is_bounded():
    from app.services.job_categories import build_search_queries
    queries = build_search_queries("HR", "London", "GRADUATE", "", max_queries=3)
    assert 1 <= len(queries) <= 3
    assert len(queries) == len(set(queries))


def test_source_diversity_interleaves_domains_without_dropping_results():
    from app.services.job_data import diversify_by_source

    def job(job_id, url):
        return JobRecord.model_validate({
            "job_id": job_id,
            "title": "Role",
            "company": "Co",
            "source_url": url,
            "source_domain": url.split("//")[1].split("/")[0],
            "provenance": {"source_url": url, "source_name": "test", "retrieved_at": datetime.now(timezone.utc)},
        })

    jobs = [
        job("a1", "https://a.com/1"), job("a2", "https://a.com/2"), job("a3", "https://a.com/3"),
        job("b1", "https://b.com/1"), job("c1", "https://c.com/1"),
    ]
    result = diversify_by_source(jobs)
    assert len(result) == 5
    assert {j.job_id for j in result} == {j.job_id for j in jobs}
    # first three domains should be spread out, not all "a.com" consecutively
    assert [j.source_domain for j in result[:3]] != ["a.com", "a.com", "a.com"]


def test_url_deduplication_across_queries():
    with TestClient(app) as client:
        response = client.post("/api/jobs/search", json={"mode": "demo"})
    assert response.status_code == 200
    urls = [job["source_url"] for job in response.json()["jobs"] if job["source_url"]]
    assert len(urls) == len(set(urls))
