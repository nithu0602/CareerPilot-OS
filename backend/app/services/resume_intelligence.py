import re
from collections.abc import Iterable
from pathlib import Path

from pypdf import PdfReader

SECTION_NAMES = {
    "education": ("education", "academic"),
    "experience": ("experience", "employment", "work history"),
    "projects": ("projects", "portfolio"),
    "skills": ("skills", "technical skills", "technologies"),
    "certifications": ("certifications", "certificates"),
    "achievements": ("achievements", "awards", "honors"),
}

SKILL_TERMS = (
    "python", "javascript", "typescript", "java", "sql", "react", "next.js",
    "fastapi", "django", "aws", "azure", "docker", "kubernetes", "git",
    "machine learning", "data analysis", "figma", "excel", "power bi",
)


def extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return re.sub(r"[ \t]+", " ", text).strip()


def _find_section(text: str, aliases: Iterable[str]) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    start = next((i for i, line in enumerate(lines) if line.lower().rstrip(":") in aliases), None)
    if start is None:
        return ""
    content = []
    for line in lines[start + 1:]:
        normalized = line.lower().rstrip(":")
        if any(normalized in section_aliases for section_aliases in SECTION_NAMES.values()):
            break
        content.append(line)
    return "\n".join(content)


def _first_email(text: str) -> str | None:
    match = re.search(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", text)
    return match.group(0) if match else None


def _first_phone(text: str) -> str | None:
    match = re.search(r"(?:\+?\d[\d ()-]{8,}\d)", text)
    return match.group(0).strip() if match else None


def parse_resume(text: str) -> dict[str, object]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    email = _first_email(text)
    phone = _first_phone(text)
    name = next((line for line in lines[:5] if "@" not in line and not re.search(r"\d{3,}", line)), None)
    sections = {name: _find_section(text, aliases) for name, aliases in SECTION_NAMES.items()}
    skills = sorted({term for term in SKILL_TERMS if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE)})
    return {
        "name": name,
        "contact": {"email": email, "phone": phone},
        "education": sections["education"],
        "experience": sections["experience"],
        "projects": sections["projects"],
        "skills": skills,
        "certifications": sections["certifications"],
        "achievements": sections["achievements"],
        "sections_present": [name for name, value in sections.items() if value],
        "section_completeness": sum(bool(value) for value in sections.values()),
    }


def score_resume(text: str, profile: dict[str, object]) -> tuple[int, list[dict[str, object]], list[str], list[str], list[str], list[str]]:
    present = set(profile["sections_present"])
    section_score = round(len(present) / len(SECTION_NAMES) * 100)
    skills = profile["skills"]
    keyword_score = min(100, len(skills) * 12)
    bullets = [line for line in text.splitlines() if line.strip()]
    quantified = sum(bool(re.search(r"\b\d+(?:\.\d+)?%?|\$\d+", line)) for line in bullets)
    quantified_score = round(quantified / max(1, len(bullets)) * 100)
    evidence_score = 100 if profile["experience"] or profile["projects"] else 20
    formatting_flags = []
    if len(text) < 250:
        formatting_flags.append("Resume text is unusually short.")
    if len(text.split()) > 1200:
        formatting_flags.append("Resume may be longer than necessary.")
    formatting_score = 70 if not formatting_flags else 45
    components = [
        {"name": "Keyword and skill coverage", "score": keyword_score, "weight": 25, "explanation": f"Detected {len(skills)} recognized skill signals."},
        {"name": "Section completeness", "score": section_score, "weight": 25, "explanation": f"{len(present)} of {len(SECTION_NAMES)} standard sections detected."},
        {"name": "Quantified bullet ratio", "score": quantified_score, "weight": 20, "explanation": f"{quantified} lines include a measurable number or percentage."},
        {"name": "Experience and project evidence", "score": evidence_score, "weight": 20, "explanation": "Experience or project evidence was detected." if evidence_score == 100 else "No experience or project section was detected."},
        {"name": "Formatting and readability", "score": formatting_score, "weight": 10, "explanation": "Basic text extraction and length checks passed." if formatting_score == 70 else "Length/readability flags were detected."},
    ]
    overall = round(sum(item["score"] * item["weight"] for item in components) / 100)
    strengths = []
    if skills: strengths.append(f"Shows recognizable technical skill signals ({', '.join(skills[:5])}).")
    if profile["experience"]: strengths.append("Includes an experience section with role evidence.")
    if profile["projects"]: strengths.append("Includes project evidence that can support role relevance.")
    weaknesses = []
    recommendations = []
    missing = [name.title() for name in SECTION_NAMES if name not in present]
    if missing:
        weaknesses.append(f"Missing standard sections: {', '.join(missing)}.")
        recommendations.append(f"Add clearly labeled sections for: {', '.join(missing)}.")
    if quantified_score < 35:
        weaknesses.append("Few bullets contain measurable outcomes.")
        recommendations.append("Rewrite bullets with measurable impact, such as time saved, revenue, scale, or percentage improvement.")
    if not skills:
        weaknesses.append("No recognized technical skills were detected.")
        recommendations.append("Add a focused Skills section using terminology that matches your target roles.")
    if formatting_flags:
        recommendations.extend(formatting_flags)
    return overall, components, strengths, weaknesses, recommendations, formatting_flags


def analyze_resume(path: Path, resume_id: str, filename: str) -> dict[str, object]:
    text = extract_pdf_text(path)
    if not text:
        raise ValueError("No readable text was found in this PDF.")
    profile = parse_resume(text)
    overall, components, strengths, weaknesses, recommendations, flags = score_resume(text, profile)
    return {
        "resume_id": resume_id,
        "filename": filename,
        "status": "analyzed",
        "extracted_text": text,
        "profile": profile,
        "ats_estimate": overall,
        "score_breakdown": components,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "skill_signals": profile["skills"],
        "formatting_flags": flags,
    }
