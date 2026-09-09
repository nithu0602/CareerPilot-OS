"""Shared job category and location configuration.

Kept intentionally small and data-driven so the frontend can mirror the same
category/location/experience/work-mode options without duplicating logic.
"""

from typing import Literal

Category = Literal[
    "DATA",
    "IT_SOFTWARE",
    "BUSINESS",
    "HR",
    "FINANCE",
    "MARKETING",
    "OPERATIONS",
    "CONSULTING",
    "ENGINEERING",
]

Experience = Literal["GRADUATE", "INTERNSHIP", "PLACEMENT", "ENTRY_LEVEL", "ANY"]
WorkMode = Literal["ANY", "ON_SITE", "HYBRID", "REMOTE"]

# Search terms used to expand a category into concrete query keywords.
CATEGORY_SEARCH_TERMS: dict[Category, list[str]] = {
    "DATA": [
        "data scientist",
        "data analyst",
        "data science",
        "business intelligence",
        "machine learning",
        "analytics",
    ],
    "IT_SOFTWARE": [
        "software engineer",
        "software developer",
        "cloud",
        "devops",
        "cybersecurity",
        "IT support",
        "technology graduate",
    ],
    "BUSINESS": [
        "business analyst",
        "graduate business analyst",
        "strategy",
        "management consulting",
        "operations analyst",
    ],
    "HR": [
        "HR graduate",
        "HR assistant",
        "people analyst",
        "talent acquisition",
        "recruitment",
        "human resources",
    ],
    "FINANCE": [
        "finance graduate",
        "financial analyst",
        "risk analyst",
        "accounting graduate",
    ],
    "MARKETING": [
        "marketing graduate",
        "digital marketing",
        "marketing analyst",
        "communications",
    ],
    "OPERATIONS": [
        "operations analyst",
        "supply chain graduate",
        "operations graduate",
    ],
    "CONSULTING": [
        "graduate consultant",
        "technology consultant",
        "business consultant",
        "analyst consultant",
    ],
    "ENGINEERING": [
        "graduate engineer",
        "engineering graduate",
        "systems engineer",
        "data engineer",
    ],
}

# Human-readable labels for the frontend selector, in a sensible display order.
CATEGORY_LABELS: dict[Category, str] = {
    "DATA": "Data",
    "IT_SOFTWARE": "IT & Software",
    "BUSINESS": "Business",
    "HR": "HR",
    "FINANCE": "Finance",
    "MARKETING": "Marketing",
    "OPERATIONS": "Operations",
    "CONSULTING": "Consulting",
    "ENGINEERING": "Engineering",
}

# Primary UK locations. London is first-class and the default.
UK_LOCATIONS: list[str] = [
    "London",
    "Manchester",
    "Birmingham",
    "Leeds",
    "Bristol",
    "Edinburgh",
    "Glasgow",
    "Cambridge",
    "Oxford",
    "Nottingham",
    "Remote UK",
    "United Kingdom",
]

DEFAULT_LOCATION = "London"

EXPERIENCE_LABELS: dict[Experience, str] = {
    "GRADUATE": "Graduate",
    "INTERNSHIP": "Internship",
    "PLACEMENT": "Placement",
    "ENTRY_LEVEL": "Entry Level",
    "ANY": "Any",
}

# Extra keywords appended per experience level to bias query expansion.
EXPERIENCE_SEARCH_TERMS: dict[Experience, list[str]] = {
    "GRADUATE": ["graduate"],
    "INTERNSHIP": ["internship"],
    "PLACEMENT": ["placement"],
    "ENTRY_LEVEL": ["entry level", "junior"],
    "ANY": [],
}

DEFAULT_EXPERIENCE: Experience = "GRADUATE"

WORK_MODE_LABELS: dict[WorkMode, str] = {
    "ANY": "Any",
    "ON_SITE": "On-site",
    "HYBRID": "Hybrid",
    "REMOTE": "Remote",
}

DEFAULT_WORK_MODE: WorkMode = "ANY"


def category_terms(category: str | None) -> list[str]:
    return CATEGORY_SEARCH_TERMS.get((category or "").upper(), [])  # type: ignore[arg-type]


def experience_terms(experience: str | None) -> list[str]:
    return EXPERIENCE_SEARCH_TERMS.get((experience or "").upper(), [])  # type: ignore[arg-type]


def is_uk_location(location: str | None) -> bool:
    if not location:
        return False
    normalized = location.strip().lower()
    return any(normalized == option.lower() for option in UK_LOCATIONS)


def build_search_queries(
    category: str | None,
    location: str,
    experience: str | None,
    keyword: str,
    max_queries: int = 3,
) -> list[str]:
    """Bounded query expansion: category + experience + location + keyword.

    Produces at most `max_queries` distinct search strings so the Anakin
    credit budget is respected. Falls back to a single keyword-only query
    when no category is selected.
    """
    exp_terms = experience_terms(experience) or [""]
    location_suffix = f" {location} UK".strip() if location else ""
    cat_terms = category_terms(category)

    queries: list[str] = []
    if cat_terms:
        for term in cat_terms:
            for exp_term in exp_terms:
                phrase = " ".join(filter(None, [exp_term, term, keyword])).strip()
                query = f"{phrase} jobs{location_suffix}".strip()
                if query not in queries:
                    queries.append(query)
                if len(queries) >= max_queries:
                    return queries
    else:
        phrase = " ".join(filter(None, [experience_terms(experience)[0] if experience_terms(experience) else "", keyword])).strip()
        query = f"{phrase} jobs{location_suffix}".strip() if phrase else f"jobs{location_suffix}".strip()
        queries.append(query)
    return queries[:max_queries]
