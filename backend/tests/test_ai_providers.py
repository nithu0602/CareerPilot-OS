"""Temporary, manual provider connectivity checks.

Run from the backend directory:
    python -m pytest tests/test_ai_providers.py -s

This file intentionally does not test Anakin or modify CareerPilot services.
"""

from pathlib import Path

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderSettings(BaseSettings):
    """Read provider values from the same backend/.env used by the app."""

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:4b"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def _short_response(value: object) -> str:
    text = " ".join(str(value).split())
    return text[:200] + ("..." if len(text) > 200 else "")


def _safe_error(error: Exception, secret: str = "") -> str:
    message = str(error)
    if isinstance(error, httpx.HTTPStatusError):
        message = f"{message}; response={error.response.text}"
    if secret:
        message = message.replace(secret, "[REDACTED]")
    return _short_response(message)


def _report(provider: str, model: str, success: bool, response: str = "", error: str = "") -> None:
    print(f"\nProvider: {provider}")
    print(f"Model: {model}")
    print(f"Result: {'SUCCESS' if success else 'FAILURE'}")
    print(f"Short response: {response or '[none]'}")
    if error:
        print(f"Error: {error}")


def _chat_completion(
    url: str,
    api_key: str,
    model: str,
    provider: str,
    extra_headers: dict[str, str] | None = None,
) -> None:
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        if extra_headers:
            headers.update(extra_headers)
        response = httpx.post(
            url,
            headers=headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": f"Reply with exactly {provider.upper()}_OK"}],
                "temperature": 0,
                "max_tokens": 20,
            },
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        _report(provider, model, True, _short_response(content))
    except Exception as error:
        _report(provider, model, False, error=_safe_error(error, api_key))


def test_ai_providers() -> None:
    settings = ProviderSettings()
    ollama_model = settings.ollama_model if settings.ollama_model != "YOUR_MODEL" else "gemma3:4b"

    if settings.gemini_api_key:
        try:
            response = httpx.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent",
                params={"key": settings.gemini_api_key},
                json={
                    "contents": [{"parts": [{"text": "Reply with exactly GEMINI_OK"}]}],
                    "generationConfig": {"temperature": 0, "maxOutputTokens": 20},
                },
                timeout=30,
            )
            response.raise_for_status()
            content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            _report("Gemini", settings.gemini_model, True, _short_response(content))
        except Exception as error:
            _report("Gemini", settings.gemini_model, False, error=_safe_error(error, settings.gemini_api_key))
    else:
        _report("Gemini", settings.gemini_model, False, error="GEMINI_API_KEY is not configured.")

    if settings.groq_api_key:
        _chat_completion(
            "https://api.groq.com/openai/v1/chat/completions",
            settings.groq_api_key,
            settings.groq_model,
            "Groq",
        )
    else:
        _report("Groq", settings.groq_model, False, error="GROQ_API_KEY is not configured.")

    try:
        response = httpx.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/chat",
            json={
                "model": ollama_model,
                "messages": [{"role": "user", "content": "Reply with exactly OLLAMA_OK"}],
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["message"]["content"]
        _report("Ollama", ollama_model, True, _short_response(content))
    except Exception as error:
        _report("Ollama", ollama_model, False, error=_safe_error(error))
