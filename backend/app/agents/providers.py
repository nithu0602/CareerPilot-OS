import json
from typing import Any

import httpx

from app.config import Settings


class ProviderError(RuntimeError):
    """Controlled error raised when a Society provider cannot answer."""


def parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(
            line for line in cleaned.splitlines() if not line.strip().startswith("```")
        ).strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ProviderError("Provider response did not contain a JSON object.")
        try:
            value = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ProviderError("Provider response contained malformed JSON.") from exc
    if not isinstance(value, dict):
        raise ProviderError("Provider response JSON was not an object.")
    return value


class GroqClient:
    provider = "Groq"

    def __init__(self, settings: Settings, client: httpx.Client | None = None) -> None:
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.client = client or httpx.Client(timeout=45)

    def complete_json(self, prompt: str) -> dict[str, Any]:
        if not self.api_key:
            raise ProviderError("GROQ_API_KEY is not configured.")
        try:
            response = self.client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "max_tokens": 1400,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            return parse_json_object(response.json()["choices"][0]["message"]["content"])
        except ProviderError:
            raise
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError(f"Groq request failed: {type(exc).__name__}.") from exc


class OllamaClient:
    provider = "Ollama"

    def __init__(self, settings: Settings, client: httpx.Client | None = None) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.client = client or httpx.Client(timeout=60)

    def complete_json(self, prompt: str) -> dict[str, Any]:
        try:
            response = self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0},
                },
            )
            response.raise_for_status()
            return parse_json_object(response.json()["message"]["content"])
        except ProviderError:
            raise
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError(f"Ollama request failed: {type(exc).__name__}.") from exc
