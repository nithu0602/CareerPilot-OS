import asyncio
from datetime import datetime, timezone
from typing import Any

from fastapi.testclient import TestClient

from app.main import app
from app.models.job import JobRecord
from app.services.anakin_client import AnakinClient
from app.services.job_data import deduplicate_jobs, load_demo_jobs


DEMO_JOB_COUNT = 77
DEMO_CATEGORIES = [
    "DATA", "IT_SOFTWARE", "BUSINESS", "HR", "FINANCE",
    "MARKETING", "OPERATIONS", "CONSULTING", "ENGINEERING",
]
DEMO_CITIES = [
    "London", "Manchester", "Birmingham", "Leeds", "Edinburgh",
    "Nottingham", "Bristol", "Glasgow", "Sheffield", "Cambridge",
]


def test_demo_job_loading_and_missing_fields():
    jobs = load_demo_jobs()
    assert len(jobs) == DEMO_JOB_COUNT
    assert any(job.salary is None for job in jobs)
    assert any(job.deadline is None for job in jobs)
    assert all(job.provenance.source_name == "CareerPilot demo dataset" for job in jobs)
    assert all(job.education for job in jobs)
    assert all(job.experience for job in jobs)
    assert all(job.mode == "demo" for job in jobs)
    assert len({job.job_id for job in jobs}) == DEMO_JOB_COUNT
    assert len({job.source_url for job in jobs}) == DEMO_JOB_COUNT


def test_demo_dataset_covers_categories_and_uk_locations():
    jobs = load_demo_jobs()
    categories = {job.category for job in jobs}
    assert set(DEMO_CATEGORIES).issubset(categories)
    for category in DEMO_CATEGORIES:
        assert sum(1 for job in jobs if job.category == category) >= 5
    locations = {job.location for job in jobs if job.location}
    for city in DEMO_CITIES:
        assert any(city in location for location in locations), f"missing {city}"
    # The default demo flow (London + GRADUATE) relies on a UK-wide widened
    # result set: every category needs at least 5 GRADUATE roles somewhere.
    for category in DEMO_CATEGORIES:
        graduate = [job for job in jobs if job.category == category and job.experience_level == "GRADUATE"]
        assert len(graduate) >= 5, f"only {len(graduate)} GRADUATE roles in {category}"


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


class _MockResponse:
    def __init__(self, payload: Any, status_error: Exception | None = None):
        self.payload = payload
        self._status_error = status_error

    def raise_for_status(self):
        if self._status_error:
            raise self._status_error

    def json(self):
        return self.payload


def _anakin_client_with_handler(monkeypatch, handler):
    """Build an AnakinClient whose internal httpx.AsyncClient.post is stubbed by `handler`."""

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, path, **kwargs):
            return handler(path, kwargs)

    monkeypatch.setattr("app.services.anakin_client.httpx.AsyncClient", lambda timeout: MockClient())
    return AnakinClient(api_key="test-key", api_url="https://api.anakin.io/v1")


def test_anakin_uses_official_search_and_inline_scraper_paths(monkeypatch):
    calls: list[tuple[str, dict[str, Any]]] = []

    def handler(path, kwargs):
        calls.append((path, kwargs))
        if path.endswith("/search"):
            return _MockResponse({"id": "search_1", "results": [
                {"title": "Data Analyst", "url": "https://example.com/job", "snippet": "Great role"},
            ]})
        return _MockResponse({"description": "Scraped job details"})

    client = _anakin_client_with_handler(monkeypatch, handler)
    asyncio.run(client.search("data analyst"))
    asyncio.run(client.scrape("https://example.com/job"))

    assert calls[0][0] == "https://api.anakin.io/v1/search"
    assert calls[1] == (
        "https://api.anakin.io/v1/url-scraper/scrape",
        {"headers": {"X-API-Key": "test-key"}, "json": {"url": "https://example.com/job"}},
    )


def test_anakin_search_sends_x_api_key_header(monkeypatch):
    seen_headers = {}

    def handler(path, kwargs):
        seen_headers.update(kwargs["headers"])
        return _MockResponse({"id": "search_1", "results": []})

    client = _anakin_client_with_handler(monkeypatch, handler)
    asyncio.run(client.search("graduate data analyst jobs"))

    assert seen_headers == {"X-API-Key": "test-key"}


def test_anakin_search_builds_natural_language_prompt_with_location(monkeypatch):
    seen_json = {}

    def handler(path, kwargs):
        seen_json.update(kwargs["json"])
        return _MockResponse({"id": "search_1", "results": []})

    client = _anakin_client_with_handler(monkeypatch, handler)
    asyncio.run(client.search("graduate data analyst jobs", location="London"))

    assert seen_json["prompt"] == "graduate data analyst jobs in London"


def test_anakin_search_without_location_uses_query_as_prompt(monkeypatch):
    seen_json = {}

    def handler(path, kwargs):
        seen_json.update(kwargs["json"])
        return _MockResponse({"id": "search_1", "results": []})

    client = _anakin_client_with_handler(monkeypatch, handler)
    asyncio.run(client.search("graduate data analyst jobs"))

    assert seen_json["prompt"] == "graduate data analyst jobs"


def test_anakin_search_caps_limit_at_fifteen(monkeypatch):
    seen_json = {}

    def handler(path, kwargs):
        seen_json.update(kwargs["json"])
        return _MockResponse({"id": "search_1", "results": []})

    client = _anakin_client_with_handler(monkeypatch, handler)
    asyncio.run(client.search("graduate data analyst jobs", limit=50))

    assert seen_json["limit"] == 15


def test_anakin_search_passes_through_limit_below_cap(monkeypatch):
    seen_json = {}

    def handler(path, kwargs):
        seen_json.update(kwargs["json"])
        return _MockResponse({"id": "search_1", "results": []})

    client = _anakin_client_with_handler(monkeypatch, handler)
    asyncio.run(client.search("graduate data analyst jobs", limit=5))

    assert seen_json["limit"] == 5


def test_anakin_search_parses_results_from_payload(monkeypatch):
    def handler(path, kwargs):
        return _MockResponse({
            "id": "search_1",
            "results": [
                {"title": "Data Analyst", "url": "https://example.com/1", "snippet": "A"},
                {"title": "Data Engineer", "url": "https://example.com/2", "snippet": "B"},
            ],
        })

    client = _anakin_client_with_handler(monkeypatch, handler)
    results = asyncio.run(client.search("graduate data analyst jobs"))

    assert results == [
        {"title": "Data Analyst", "url": "https://example.com/1", "snippet": "A"},
        {"title": "Data Engineer", "url": "https://example.com/2", "snippet": "B"},
    ]


def test_anakin_search_raises_on_non_dict_payload(monkeypatch):
    def handler(path, kwargs):
        return _MockResponse([{"title": "Data Analyst"}])

    client = _anakin_client_with_handler(monkeypatch, handler)
    try:
        asyncio.run(client.search("graduate data analyst jobs"))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for a non-dict payload")


def test_anakin_search_raises_when_results_field_is_missing_or_invalid(monkeypatch):
    def handler(path, kwargs):
        return _MockResponse({"id": "search_1", "results": "not-a-list"})

    client = _anakin_client_with_handler(monkeypatch, handler)
    try:
        asyncio.run(client.search("graduate data analyst jobs"))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError when results is not a list")


def test_anakin_search_filters_out_non_dict_result_items(monkeypatch):
    def handler(path, kwargs):
        return _MockResponse({"id": "search_1", "results": [{"title": "Valid"}, "not-a-dict", 42]})

    client = _anakin_client_with_handler(monkeypatch, handler)
    results = asyncio.run(client.search("graduate data analyst jobs"))

    assert results == [{"title": "Valid"}]


def test_anakin_search_propagates_http_errors(monkeypatch):
    import httpx

    def handler(path, kwargs):
        request = httpx.Request("POST", path)
        response = httpx.Response(500, request=request)
        return _MockResponse(
            {},
            status_error=httpx.HTTPStatusError("server error", request=request, response=response),
        )

    client = _anakin_client_with_handler(monkeypatch, handler)
    import pytest

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(client.search("graduate data analyst jobs"))


def test_live_mode_fallback_reason_includes_exception_type_when_message_is_empty(monkeypatch):
    """Reproduces the real failure: AnakinClient.search() succeeds, but scrape()
    times out with an exception whose str() is empty (httpx.ReadTimeout('')).
    The fallback_reason must still name the exception type instead of showing
    "Live Anakin request failed: " with nothing after the colon.
    """
    import httpx

    from app.routes import jobs as jobs_route

    monkeypatch.setattr(AnakinClient, "configured", property(lambda self: True))

    async def fake_search(self, query, location, limit=10):
        return [{"title": "Data Analyst", "url": "https://example.com/job", "snippet": "..."}]

    async def fake_scrape(self, url):
        raise httpx.ReadTimeout("")

    monkeypatch.setattr(jobs_route.AnakinClient, "search", fake_search)
    monkeypatch.setattr(jobs_route.AnakinClient, "scrape", fake_scrape)

    with TestClient(app) as client:
        response = client.post("/api/jobs/search", json={"mode": "live"})

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "fallback"
    assert data["fallback_reason"] == "Live Anakin request failed: ReadTimeout"
    assert data["total"] == len(load_demo_jobs())


def test_demo_search_api_and_detail():
    with TestClient(app) as client:
        response = client.post("/api/jobs/search", json={"role": "data analyst", "mode": "demo"})
        assert response.status_code == 200
        assert response.json()["mode"] == "demo"
        assert response.json()["total"] >= 1
        job_id = response.json()["jobs"][0]["job_id"]
        detail = client.get(f"/api/jobs/{job_id}")
        assert detail.status_code == 200


def test_live_mode_without_credentials_falls_back_to_demo(monkeypatch):
    # Force "not configured" for this test regardless of real Anakin credentials
    # present in the developer's .env, without touching .env or config globals.
    monkeypatch.setattr(AnakinClient, "configured", property(lambda self: False))
    with TestClient(app) as client:
        response = client.post("/api/jobs/search", json={"mode": "live"})
    assert response.status_code == 200
    assert response.json()["mode"] == "fallback"
    assert response.json()["total"] == len(load_demo_jobs())


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


def test_demo_sparse_location_gracefully_widens_to_uk_roles():
    """A specific location with <5 direct matches returns closest relevant
    UK demo roles instead of an empty page (used by the default demo flow)."""
    payload = {"mode": "demo", "category": "FINANCE", "location": "London", "experience": "GRADUATE"}
    with TestClient(app) as client:
        response = client.post("/api/jobs/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 5
    assert all(job["category"] == "FINANCE" for job in data["jobs"])
    assert data["result_note"]
    assert "only had" in data["result_note"] and "across the UK" in data["result_note"]


def test_demo_london_search_returns_graduate_data_roles():
    """The default demo landing view (Data / London / Graduate) must be rich."""
    payload = {"mode": "demo", "category": "DATA", "location": "London", "experience": "GRADUATE"}
    with TestClient(app) as client:
        response = client.post("/api/jobs/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 5
    assert all(job["category"] == "DATA" and job["experience_level"] == "GRADUATE" for job in data["jobs"])
    cities = [job["location"] for job in data["jobs"]]
    assert any("London" in city for city in cities)


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


def test_nested_jobs_response_normalization():
    payload = {
        "jobs": [
            {
                "company": "The Information Lab",
                "description": "Consulting and analytics role with client projects.",
                "jobType": "Graduate",
                "location": "London",
                "postedDate": "August 17, 2026",
                "salary": "£35,000",
                "title": "Graduate Data Consulting Analyst",
                "url": "https://www.grb.uk.com/graduate-jobs/the-information-lab-graduate-data-consulting-analyst-london-36507",
            }
        ],
        "pageTitle": "Graduate Data Consulting Analyst",
        "pageType": "jobListing",
        "totalJobs": 1,
    }
    job = AnakinClient.normalize(payload, datetime.now(timezone.utc))
    assert job.title == "Graduate Data Consulting Analyst"
    assert job.company == "The Information Lab"
    assert job.location == "London"
    assert job.salary == "£35,000"
    assert job.employment_type == "Graduate"
    assert job.description == "Consulting and analytics role with client projects."
    assert job.source_url == "https://www.grb.uk.com/graduate-jobs/the-information-lab-graduate-data-consulting-analyst-london-36507"
    assert job.mode == "live"
    assert job.source_domain == "grb.uk.com"


def test_nested_jobs_exact_url_matching():
    payload = {
        "url": "https://www.grb.uk.com/graduate-jobs/target-role-2",
        "jobs": [
            {
                "company": "Company 1",
                "title": "Role 1",
                "url": "https://www.grb.uk.com/graduate-jobs/other-role-1",
                "salary": "£30,000",
            },
            {
                "company": "Target Company",
                "title": "Target Role",
                "url": "https://www.grb.uk.com/graduate-jobs/target-role-2",
                "salary": "£45,000",
            },
        ],
    }
    job = AnakinClient.normalize(payload, datetime.now(timezone.utc))
    assert job.company == "Target Company"
    assert job.title == "Target Role"
    assert job.salary == "£45,000"
    assert job.source_url == "https://www.grb.uk.com/graduate-jobs/target-role-2"


def test_nested_jobs_fallback_to_first_job_when_no_url_matches():
    payload = {
        "source_url": "https://www.grb.uk.com/graduate-jobs/unmatched-url",
        "jobs": [
            {
                "company": "First Company",
                "title": "First Role",
                "location": "Edinburgh",
                "url": "https://www.grb.uk.com/graduate-jobs/first-role",
            },
            {
                "company": "Second Company",
                "title": "Second Role",
                "location": "Cardiff",
                "url": "https://www.grb.uk.com/graduate-jobs/second-role",
            },
        ],
    }
    job = AnakinClient.normalize(payload, datetime.now(timezone.utc))
    assert job.company == "First Company"
    assert job.title == "First Role"
    assert job.location == "Edinburgh"
    assert job.source_url == "https://www.grb.uk.com/graduate-jobs/unmatched-url"


def test_nested_jobs_null_field_preservation():
    payload = {
        "jobs": [
            {
                "company": "Minimal Co",
                "title": "Minimal Role",
                "url": "https://example.com/job",
            }
        ]
    }
    job = AnakinClient.normalize(payload, datetime.now(timezone.utc))
    assert job.company == "Minimal Co"
    assert job.title == "Minimal Role"
    assert job.location is None
    assert job.salary is None
    assert job.employment_type is None
    assert job.description is None
    assert job.deadline is None
    assert job.sponsorship_information is None
    assert job.requirements == []
    assert job.required_skills == []
    assert job.responsibilities == []
    assert job.preferred_skills == []


def test_existing_simple_scraper_response_compatibility():
    payload = {
        "title": "Software Engineer",
        "company": "Tech Labs",
        "location": "Manchester",
        "salary": "£50,000",
        "description": "Exciting software engineering role.",
        "employment_type": "Permanent",
        "url": "https://example.com/engineering-role",
    }
    job = AnakinClient.normalize(payload, datetime.now(timezone.utc))
    assert job.title == "Software Engineer"
    assert job.company == "Tech Labs"
    assert job.location == "Manchester"
    assert job.salary == "£50,000"
    assert job.description == "Exciting software engineering role."
    assert job.employment_type == "Permanent"
    assert job.source_url == "https://example.com/engineering-role"


def test_live_search_maps_nested_scraper_results(monkeypatch):
    from app.routes import jobs as jobs_route

    monkeypatch.setattr(AnakinClient, "configured", property(lambda self: True))

    target_url = "https://www.grb.uk.com/graduate-jobs/the-information-lab-graduate-data-consulting-analyst-london-36507"

    async def fake_search(self, query, location, limit=10):
        return [{"title": "Search Snippet Title", "url": target_url, "snippet": "..."}]

    async def fake_scrape(self, url):
        return {
            "jobs": [
                {
                    "company": "The Information Lab",
                    "description": "Full graduate analyst role description.",
                    "jobType": "Graduate",
                    "location": "London",
                    "postedDate": "August 17, 2026",
                    "salary": "£35,000",
                    "title": "Graduate Data Consulting Analyst",
                    "url": target_url,
                }
            ],
            "pageTitle": "Graduate Data Consulting Analyst",
            "pageType": "jobListing",
            "totalJobs": 1,
        }

    monkeypatch.setattr(jobs_route.AnakinClient, "search", fake_search)
    monkeypatch.setattr(jobs_route.AnakinClient, "scrape", fake_scrape)

    with TestClient(app) as client:
        response = client.post("/api/jobs/search", json={"mode": "live", "category": "DATA"})

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "live"
    assert data["total"] == 1
    job = data["jobs"][0]
    assert job["title"] == "Graduate Data Consulting Analyst"
    assert job["company"] == "The Information Lab"
    assert job["location"] == "London"
    assert job["salary"] == "£35,000"
    assert job["employment_type"] == "Graduate"
    assert job["description"] == "Full graduate analyst role description."
    assert job["source_url"] == target_url
    assert job["mode"] == "live"
    assert job["requirements"] == []
    assert job["required_skills"] == []

