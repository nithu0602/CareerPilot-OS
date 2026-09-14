"""Focused tests for Groq/Ollama provider HTTP handling.

These tests mock HTTP responses with httpx.MockTransport. They never call a
real Groq or Ollama endpoint.
"""

import httpx
import pytest

from app.agents.providers import GroqClient, OllamaClient, ProviderError, parse_json_object
from app.config import Settings


def _settings(**overrides) -> Settings:
    defaults = {
        "groq_api_key": "test-groq-key",
        "groq_model": "openai/gpt-oss-20b",
        "ollama_base_url": "http://localhost:11434",
        "ollama_model": "gemma3:4b",
    }
    defaults.update(overrides)
    return Settings(**defaults)


def _groq_client(handler, api_key="test-groq-key") -> GroqClient:
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport, timeout=5)
    return GroqClient(_settings(groq_api_key=api_key), client=client)


def _ollama_client(handler) -> OllamaClient:
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport, timeout=5)
    return OllamaClient(_settings(), client=client)


def _groq_response(content: str) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})


def _ollama_response(content: str) -> httpx.Response:
    return httpx.Response(200, json={"message": {"content": content}})


# A. Valid Groq JSON -> successful Resume Agent output.
def test_groq_valid_json_succeeds():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer test-groq-key"
        return _groq_response('{"skills": ["Python"]}')

    result = _groq_client(handler).complete_json("prompt")
    assert result == {"skills": ["Python"]}


# B. Groq JSON wrapped in ```json fences -> successfully parsed.
def test_groq_json_wrapped_in_code_fence_is_parsed():
    def handler(request: httpx.Request) -> httpx.Response:
        return _groq_response('```json\n{"skills": ["SQL"]}\n```')

    result = _groq_client(handler).complete_json("prompt")
    assert result == {"skills": ["SQL"]}


# C. Groq invalid JSON -> controlled failure, not crash.
def test_groq_invalid_json_raises_controlled_provider_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return _groq_response("this is not json at all")

    with pytest.raises(ProviderError):
        _groq_client(handler).complete_json("prompt")


# D. Valid Ollama JSON -> successful Interview Agent output.
def test_ollama_valid_json_succeeds():
    def handler(request: httpx.Request) -> httpx.Response:
        return _ollama_response('{"question": "How would you validate a result?"}')

    result = _ollama_client(handler).complete_json("prompt")
    assert result == {"question": "How would you validate a result?"}


# E. Ollama JSON with surrounding text -> parse if safely possible.
def test_ollama_json_with_surrounding_text_is_parsed():
    def handler(request: httpx.Request) -> httpx.Response:
        return _ollama_response('Sure, here is the answer:\n{"question": "Explain overfitting."}\nThanks!')

    result = _ollama_client(handler).complete_json("prompt")
    assert result == {"question": "Explain overfitting."}


# F. Invalid Ollama JSON -> controlled failure.
def test_ollama_invalid_json_raises_controlled_provider_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return _ollama_response("not json")

    with pytest.raises(ProviderError):
        _ollama_client(handler).complete_json("prompt")


# G. Missing required schema field -> controlled validation failure.
def test_missing_required_field_fails_schema_validation():
    from pydantic import ValidationError

    from app.schemas.society import ResumeAgentReport

    # ResumeAgentReport has no strictly-required fields itself, so use a
    # report with a genuinely required field to prove validation failure.
    from app.schemas.society import FitCriticReport

    with pytest.raises(ValidationError):
        FitCriticReport.model_validate({"strong_evidence": []})


# H. Provider timeout -> controlled failure.
def test_groq_timeout_raises_controlled_provider_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out", request=request)

    with pytest.raises(ProviderError):
        _groq_client(handler).complete_json("prompt")


def test_ollama_timeout_raises_controlled_provider_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out", request=request)

    with pytest.raises(ProviderError):
        _ollama_client(handler).complete_json("prompt")


def test_groq_missing_api_key_raises_controlled_provider_error():
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover - should not be called
        raise AssertionError("Groq should not be called without an API key")

    with pytest.raises(ProviderError):
        _groq_client(handler, api_key="").complete_json("prompt")


def test_parse_json_object_handles_object_embedded_in_text():
    text = "Here is the result: {\"a\": 1, \"b\": 2} -- hope that helps"
    assert parse_json_object(text) == {"a": 1, "b": 2}


def test_provider_error_never_leaks_api_key_in_message():
    secret = "sk-super-secret-value"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": f"invalid key {secret}"})

    try:
        _groq_client(handler, api_key=secret).complete_json("prompt")
    except ProviderError as exc:
        assert secret not in str(exc)
    else:
        pytest.fail("Expected a ProviderError for a 401 response")
