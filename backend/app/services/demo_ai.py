"""Deterministic, swappable demo implementations for CareerPilot AI features."""

from dataclasses import dataclass

from app.schemas.demo import ATSResponse, ATSSectionScores, InterviewPrep, JobMatch


@dataclass(frozen=True, slots=True)
class _CareerProfile:
    """Define deterministic matching criteria for a career recommendation.

    Attributes:
        title: Public-facing career title.
        salary: Indicative United Kingdom salary range.
        keywords: Resume keywords relevant to the career.
        base_match: Minimum demonstration match percentage.
    """

    title: str
    salary: str
    keywords: tuple[str, ...]
    base_match: int


_SKILL_KEYWORDS: tuple[str, ...] = (
    "python", "sql", "excel", "power bi", "tableau", "pandas", "numpy",
    "machine learning", "tensorflow", "pytorch", "scikit-learn", "fastapi",
    "django", "react", "next.js", "javascript", "typescript", "aws", "azure",
    "docker", "kubernetes", "git", "agile", "scrum",
)

_CAREER_PROFILES: tuple[_CareerProfile, ...] = (
    _CareerProfile("Data Analyst", "£35k–£45k", ("sql", "python", "excel", "power bi", "tableau", "pandas"), 67),
    _CareerProfile("Machine Learning Engineer", "£45k–£60k", ("python", "machine learning", "tensorflow", "pytorch", "scikit-learn", "docker"), 64),
    _CareerProfile("Backend Software Engineer", "£42k–£58k", ("python", "fastapi", "django", "sql", "docker", "aws"), 66),
    _CareerProfile("Frontend Software Engineer", "£38k–£55k", ("react", "next.js", "javascript", "typescript", "git", "agile"), 63),
    _CareerProfile("Cloud Engineer", "£45k–£62k", ("aws", "azure", "docker", "kubernetes", "python", "git"), 61),
    _CareerProfile("Business Intelligence Analyst", "£36k–£48k", ("sql", "excel", "power bi", "tableau", "python", "agile"), 65),
)


class DemoAIService:
    """Provide deterministic stand-ins for future AI-powered CareerPilot features."""

    def analyze_ats(self, resume_text: str) -> ATSResponse:
        """Return a repeatable ATS assessment derived from resume text.

        Args:
            resume_text: Raw text extracted from a candidate resume.

        Returns:
            A validated, deterministic ATS analysis.
        """
        normalized_text: str = self._normalize(resume_text)
        skills: tuple[str, ...] = self._detected_skills(normalized_text)
        section_scores = ATSSectionScores(
            skills=min(96, 68 + len(skills) * 4),
            experience=self._score_for_evidence(normalized_text, ("experience", "employment", "worked", "engineer", "analyst", "intern"), 64, 88),
            education=self._score_for_evidence(normalized_text, ("education", "university", "bachelor", "master", "degree", "gpa"), 70, 95),
            projects=self._score_for_evidence(normalized_text, ("project", "github", "portfolio", "built", "deployed", "implemented"), 62, 90),
            keywords=min(94, 66 + len(skills) * 3),
        )
        overall_score: int = round(
            section_scores.skills * 0.25
            + section_scores.experience * 0.30
            + section_scores.education * 0.15
            + section_scores.projects * 0.15
            + section_scores.keywords * 0.15
        )
        return ATSResponse(
            overall_score=overall_score,
            section_scores=section_scores,
            strengths=self._ats_strengths(skills, section_scores),
            improvements=self._ats_improvements(normalized_text, section_scores),
        )

    def match_jobs(self, resume_text: str) -> list[JobMatch]:
        """Return five repeatable career recommendations for resume text.

        Args:
            resume_text: Raw text extracted from a candidate resume.

        Returns:
            Five validated career recommendations, ordered by match score.
        """
        normalized_text: str = self._normalize(resume_text)
        skills: tuple[str, ...] = self._detected_skills(normalized_text)
        matches: list[JobMatch] = []
        for profile in _CAREER_PROFILES:
            relevant_skills: tuple[str, ...] = tuple(keyword for keyword in profile.keywords if keyword in skills)
            match_score: int = min(96, profile.base_match + len(relevant_skills) * 6)
            matches.append(
                JobMatch(
                    title=profile.title,
                    match=match_score,
                    salary=profile.salary,
                    reason=self._job_match_reason(profile, relevant_skills),
                )
            )
        return sorted(matches, key=lambda match: (-match.match, match.title))[:5]

    def prepare_interview(self, resume_text: str) -> InterviewPrep:
        """Return deterministic interview preparation questions for resume text.

        Args:
            resume_text: Raw text extracted from a candidate resume.

        Returns:
            A validated set of technical, behavioural, and resume-focused questions.
        """
        skills: tuple[str, ...] = self._detected_skills(self._normalize(resume_text))
        primary_skills: tuple[str, str, str] = self._three_primary_skills(skills)
        return InterviewPrep(
            technical=[
                f"Describe a production problem you solved using {primary_skills[0]}. What trade-offs did you make?",
                f"How would you validate quality and reliability when delivering work with {primary_skills[1]}?",
                f"Walk us through how you would improve the performance or maintainability of a {primary_skills[2]} solution.",
            ],
            behavioral=[
                "Tell me about a time you aligned stakeholders with different priorities around a delivery decision.",
                "Describe a challenging project. How did you identify risks and keep the work moving?",
                "Give an example of feedback that changed your approach. What did you do differently afterwards?",
            ],
            resume_questions=[
                f"Which accomplishment on your resume best demonstrates your {primary_skills[0]} capability, and how did you measure its impact?",
                "Choose one project from your resume and explain your personal ownership, the outcome, and the key lesson learned.",
                "Which resume experience is most relevant to this role, and what would you improve if you repeated it today?",
            ],
        )

    @staticmethod
    def _normalize(resume_text: str) -> str:
        """Normalize resume text for deterministic keyword matching.

        Args:
            resume_text: Raw resume text.

        Returns:
            Lowercase, whitespace-normalized resume text.
        """
        return " ".join(resume_text.casefold().split())

    @staticmethod
    def _detected_skills(normalized_text: str) -> tuple[str, ...]:
        """Extract known career keywords while preserving a defined order.

        Args:
            normalized_text: Normalized resume text.

        Returns:
            Ordered tuple of distinct supported skills found in the text.
        """
        return tuple(skill for skill in _SKILL_KEYWORDS if skill in normalized_text)

    @staticmethod
    def _score_for_evidence(normalized_text: str, evidence_terms: tuple[str, ...], absent_score: int, present_score: int) -> int:
        """Produce a deterministic section score from evidence-term coverage.

        Args:
            normalized_text: Normalized resume text.
            evidence_terms: Terms that indicate the relevant section is present.
            absent_score: Score when no terms are found.
            present_score: Maximum score when all terms are found.

        Returns:
            An integer score in the configured range.
        """
        evidence_count: int = sum(term in normalized_text for term in evidence_terms)
        if evidence_count == 0:
            return absent_score
        increment: float = (present_score - absent_score) / len(evidence_terms)
        return min(present_score, round(absent_score + increment * evidence_count))

    @staticmethod
    def _ats_strengths(skills: tuple[str, ...], section_scores: ATSSectionScores) -> list[str]:
        """Create three deterministic, evidence-based resume strengths.

        Args:
            skills: Ordered skills detected in the resume.
            section_scores: Computed section scores.

        Returns:
            Three concise strengths suitable for a demo response.
        """
        skill_summary: str = ", ".join(skills[:3]) if skills else "professional skills"
        project_message: str = (
            "Project evidence includes delivery-focused language and practical outcomes."
            if section_scores.projects >= 75
            else "The resume has a clear foundation that can be strengthened with quantified project outcomes."
        )
        return [
            f"The resume demonstrates relevant capability in {skill_summary}.",
            "The document contains role-relevant terminology that supports recruiter searchability.",
            project_message,
        ]

    @staticmethod
    def _ats_improvements(normalized_text: str, section_scores: ATSSectionScores) -> list[str]:
        """Create three deterministic, practical ATS improvement recommendations.

        Args:
            normalized_text: Normalized resume text.
            section_scores: Computed section scores.

        Returns:
            Three prioritized improvement recommendations.
        """
        recommendations: list[str] = []
        if section_scores.experience < 75:
            recommendations.append("Add measurable outcomes to work experience, such as delivery time, quality, cost, or user-impact metrics.")
        if section_scores.projects < 75:
            recommendations.append("Add a projects section with your role, technologies, scope, and a measurable result for each project.")
        if section_scores.education < 80:
            recommendations.append("Make education details easier to scan by including the qualification, institution, and completion year.")
        if "linkedin" not in normalized_text and "github" not in normalized_text:
            recommendations.append("Include a relevant professional profile or portfolio link to help reviewers verify your work.")
        recommendations.extend([
            "Tailor the professional summary and skills order to the exact language used in the target job description.",
            "Use consistent dates, headings, and bullet formatting so applicant-tracking systems can parse the document reliably.",
        ])
        return recommendations[:3]

    @staticmethod
    def _job_match_reason(profile: _CareerProfile, relevant_skills: tuple[str, ...]) -> str:
        """Explain a deterministic career match without unsupported claims.

        Args:
            profile: Career profile considered for matching.
            relevant_skills: Relevant detected skills for the profile.

        Returns:
            A concise, evidence-based match explanation.
        """
        if relevant_skills:
            evidence: str = " and ".join(relevant_skills[:2])
            return f"Relevant resume evidence includes {evidence}, which aligns with {profile.title} work."
        return f"A transferable foundation makes {profile.title} a practical role to explore and tailor towards."

    @staticmethod
    def _three_primary_skills(skills: tuple[str, ...]) -> tuple[str, str, str]:
        """Select three stable interview focus areas from detected skills.

        Args:
            skills: Ordered skills detected in the resume.

        Returns:
            Exactly three focus areas for interview question generation.
        """
        fallbacks: tuple[str, ...] = ("problem solving", "stakeholder communication", "delivery planning")
        combined: tuple[str, ...] = skills + fallbacks
        return combined[0], combined[1], combined[2]


def get_demo_ai_service() -> DemoAIService:
    """Provide the deterministic demo service through FastAPI dependency injection.

    Returns:
        A stateless demo AI service instance.
    """
    return DemoAIService()
