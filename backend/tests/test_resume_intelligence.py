from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.main import app
from app.services.resume_intelligence import extract_pdf_text, parse_resume, score_resume


def test_parse_resume_detects_sections_and_skills():
    profile = parse_resume(
        "Alex Chen\nalex@example.com\n\nExperience\nBuilt Python APIs and improved latency by 30%.\n"
        "\nProjects\nCareerPilot dashboard\n\nSkills\nPython, React\n\nEducation\nBSc Computer Science"
    )
    assert profile["name"] == "Alex Chen"
    assert profile["contact"]["email"] == "alex@example.com"
    assert set(profile["skills"]) >= {"python", "react"}
    assert set(profile["sections_present"]) == {"experience", "projects", "skills", "education"}


def test_ats_score_is_explainable_and_bounded():
    text = "Alex Chen\nExperience\nBuilt Python APIs and improved latency by 30%.\nSkills\nPython"
    profile = parse_resume(text)
    score, components, strengths, weaknesses, recommendations, _ = score_resume(text, profile)
    assert 0 <= score <= 100
    assert {item["name"] for item in components} == {
        "Keyword and skill coverage", "Section completeness", "Quantified bullet ratio",
        "Experience and project evidence", "Formatting and readability",
    }
    assert strengths
    assert weaknesses
    assert recommendations


def test_empty_pdf_extraction_returns_empty_text(tmp_path: Path):
    pdf_path = tmp_path / "empty.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    with pdf_path.open("wb") as handle:
        writer.write(handle)
    assert extract_pdf_text(pdf_path) == ""


def test_resume_api_rejects_invalid_file():
    with TestClient(app) as client:
        response = client.post("/api/resumes/upload", files={"file": ("resume.txt", BytesIO(b"not pdf"), "text/plain")})
    assert response.status_code == 400


def test_resume_api_upload_and_analyze(tmp_path: Path, monkeypatch):
    resume_dir = tmp_path / "resumes"
    analysis_dir = tmp_path / "analyses"
    monkeypatch.setenv("RESUME_STORAGE_DIR", str(resume_dir))
    monkeypatch.setenv("ANALYSIS_STORAGE_DIR", str(analysis_dir))
    from app.config import get_settings
    get_settings.cache_clear()


def test_resume_api_reports_malformed_stored_analysis(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ANALYSIS_STORAGE_DIR", str(tmp_path / "analyses"))
    from app.config import get_settings
    get_settings.cache_clear()
    analysis_dir = tmp_path / "analyses"
    analysis_dir.mkdir()
    (analysis_dir / "broken.json").write_text("{not-json", encoding="utf-8")
    with TestClient(app) as client:
        response = client.get("/api/resumes/broken")
    assert response.status_code == 500
    get_settings.cache_clear()
    pdf_path = Path(__file__).parents[2] / "CareerPilot_Architecture_Review.pdf"
    with TestClient(app) as client:
        with pdf_path.open("rb") as handle:
            upload = client.post("/api/resumes/upload", files={"file": ("resume.pdf", handle, "application/pdf")})
        assert upload.status_code == 201
        resume_id = upload.json()["resume_id"]
        analysis = client.post(f"/api/resumes/{resume_id}/analyze")
        assert analysis.status_code == 200
        assert analysis.json()["ats_estimate"] >= 0
        retrieved = client.get(f"/api/resumes/{resume_id}")
        assert retrieved.status_code == 200
    get_settings.cache_clear()
