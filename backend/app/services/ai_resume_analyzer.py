"""OpenAI Responses API service for validated resume analysis."""

import asyncio
from collections.abc import Awaitable, Callable

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    InternalServerError,
    RateLimitError,
)

from app.core.config import Settings, settings
from app.core.logging import get_logger
from app.schemas.analysis import AnalysisResponse

logger = get_logger(__name__)

SYSTEM_INSTRUCTIONS = """You extract factual candidate information from resume text.
Use only evidence present in the supplied resume. Do not infer employers, qualifications,
dates, skills, accomplishments, certifications, languages, or years of experience.
Return the complete schema. Use empty strings, empty arrays, or 0 when the resume does
not provide a value. Weaknesses must be phrased as factual gaps or missing evidence,
not as speculative personal judgments. Do not provide ATS scoring or job matching."""


class OpenAIAnalysisError(RuntimeError):
    """Base exception for safe, user-facing resume analysis failures."""


class OpenAIConfigurationError(OpenAIAnalysisError):
    """Raised when the OpenAI API key is unavailable."""


class OpenAIAnalysisTimeout(OpenAIAnalysisError):
    """Raised after all response attempts time out."""


class OpenAIAnalysisUnavailable(OpenAIAnalysisError):
    """Raised after retryable provider failures are exhausted."""


class OpenAIAnalysisResponseError(OpenAIAnalysisError):
    """Raised when no validated structured analysis is returned."""


RetryableCall = Callable[[], Awaitable[object]]


class ResumeAnalyzer:
    """Analyze raw resume text through the OpenAI Responses API."""

    def __init__(self, runtime_settings: Settings = settings) -> None:
        self._settings = runtime_settings
        api_key = runtime_settings.openai_api_key
        self._api_key = api_key.get_secret_value() if api_key else None
        self._client = (
            AsyncOpenAI(
                api_key=self._api_key,
                timeout=runtime_settings.openai_timeout_seconds,
                max_retries=0,
            )
            if self._api_key
            else None
        )

    async def analyze(self, resume_text: str) -> AnalysisResponse:
        """Return one Pydantic-validated analysis for supplied raw resume text."""
        if self._client is None:
            raise OpenAIConfigurationError("Resume analysis is not configured.")

        async def create_response() -> object:
            return await self._client.responses.parse(
                model=self._settings.openai_model,
                store=False,
                input=[
                    {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                    {"role": "user", "content": resume_text},
                ],
                text_format=AnalysisResponse,
            )

        try:
            response = await self._run_with_retry(create_response)
            parsed = getattr(response, "output_parsed", None)
            if not isinstance(parsed, AnalysisResponse):
                raise OpenAIAnalysisResponseError(
                    "Resume analysis did not return a valid structured result."
                )
            return parsed
        finally:
            await self._client.close()

    async def _run_with_retry(self, operation: RetryableCall) -> object:
        """Run retryable OpenAI requests with bounded exponential backoff."""
        attempts = self._settings.openai_max_retries + 1
        for attempt in range(attempts):
            try:
                return await operation()
            except APITimeoutError as error:
                if attempt == attempts - 1:
                    raise OpenAIAnalysisTimeout("Resume analysis timed out.") from error
                await self._wait_before_retry(attempt, "timeout")
            except (APIConnectionError, RateLimitError, InternalServerError) as error:
                if attempt == attempts - 1:
                    raise OpenAIAnalysisUnavailable("Resume analysis is temporarily unavailable.") from error
                await self._wait_before_retry(attempt, type(error).__name__)
            except APIStatusError as error:
                if error.status_code >= 500 and attempt < attempts - 1:
                    await self._wait_before_retry(attempt, f"http_{error.status_code}")
                    continue
                raise OpenAIAnalysisUnavailable("Resume analysis request was not accepted.") from error

        raise OpenAIAnalysisUnavailable("Resume analysis is temporarily unavailable.")

    async def _wait_before_retry(self, attempt: int, reason: str) -> None:
        """Log and apply a bounded exponential retry delay."""
        delay_seconds = 0.5 * (2**attempt)
        logger.warning(
            "resume_analysis_retry",
            extra={"attempt": attempt + 1, "reason": reason, "delay_seconds": delay_seconds},
        )
        await asyncio.sleep(delay_seconds)


def get_resume_analyzer() -> ResumeAnalyzer:
    """Create the application resume analysis service."""
    return ResumeAnalyzer()
