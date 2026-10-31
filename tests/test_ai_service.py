from datetime import date
from types import SimpleNamespace
import pytest
from google.genai import errors as genai_errors

from exceptions import AIServiceError
from services.ai_service import (
    GeminiAIService,
    MSG_RATE_LIMIT,
    MSG_SERVICE_UNAVAILABLE,
    format_ai_error,
    reset_rate_limit_cooldown,
)


class FakeModels:
    def generate_content(self, **kwargs):
        assert "Anne" not in kwargs["contents"]
        return SimpleNamespace(text='{"risk":"low","possible_risks":["None identified"],"explanation":"Screening summary.","next_steps":["Discuss with a clinician; this is not a diagnosis."]}')


class FakeClient:
    models = FakeModels()


def test_ai_success():
    settings = SimpleNamespace(gemini_api_key="secret", gemini_model="gemini-test")
    result = GeminiAIService(settings, FakeClient()).generate_remark(date(1990, 1, 1), 95, 13, 180)
    assert result.risk == "low"


def test_missing_credentials_are_reported():
    settings = SimpleNamespace(gemini_api_key="", gemini_model="")
    service = GeminiAIService(settings)
    try:
        service.generate_remark(date(1990, 1, 1), 95, 13, 180)
    except Exception as exc:
        assert str(exc) == "GEMINI_MODEL is not configured."
    else:
        raise AssertionError("Missing credentials should fail clearly")


def test_http_429_resource_exhausted_raises_clean_message_without_retries(monkeypatch):
    """Verify HTTP 429 displays clean message and never enters retry loops."""
    call_count = 0

    class RateLimitModels:
        def generate_content(self, **kwargs):
            nonlocal call_count
            call_count += 1
            raise genai_errors.ClientError(
                429,
                {
                    "error": {
                        "code": 429,
                        "status": "RESOURCE_EXHAUSTED",
                        "message": "Quota exceeded for quota metric 'Generate Content API Requests Per Minute'",
                    }
                },
            )

    class RateLimitClient:
        models = RateLimitModels()

    monkeypatch.setattr("time.sleep", lambda s: None)
    settings = SimpleNamespace(gemini_api_key="secret-key", gemini_model="gemini-test", ai_timeout_seconds=5)
    service = GeminiAIService(settings, RateLimitClient())

    with pytest.raises(AIServiceError) as exc_info:
        service.generate_remark(date(1990, 1, 1), 95, 13, 180)

    assert str(exc_info.value) == MSG_RATE_LIMIT
    assert call_count == 1  # Only 1 attempt; no automatic retry loop for 429


def test_http_503_service_unavailable_retries_and_raises_clean_message(monkeypatch):
    """Verify HTTP 503 retries transient error and displays clean message once exhausted."""
    call_count = 0

    class ServerError503Models:
        def generate_content(self, **kwargs):
            nonlocal call_count
            call_count += 1
            raise genai_errors.ServerError(
                503,
                {"error": {"code": 503, "status": "UNAVAILABLE", "message": "The service is temporarily unavailable"}},
            )

    class ServerError503Client:
        models = ServerError503Models()

    monkeypatch.setattr("time.sleep", lambda s: None)
    settings = SimpleNamespace(gemini_api_key="secret-key", gemini_model="gemini-test", ai_timeout_seconds=5)
    service = GeminiAIService(settings, ServerError503Client())

    with pytest.raises(AIServiceError) as exc_info:
        service.generate_remark(date(1990, 1, 1), 95, 13, 180)

    assert str(exc_info.value) == MSG_SERVICE_UNAVAILABLE
    assert call_count == 4  # Initial attempt + 3 retries (MAX_RETRIES = 3)


def test_http_504_gateway_timeout_retries_and_raises_clean_message(monkeypatch):
    """Verify HTTP 504 retries transient gateway timeout and displays clean message."""
    call_count = 0

    class ServerError504Models:
        def generate_content(self, **kwargs):
            nonlocal call_count
            call_count += 1
            raise genai_errors.ServerError(
                504,
                {"error": {"code": 504, "status": "DEADLINE_EXCEEDED", "message": "Gateway timeout"}},
            )

    class ServerError504Client:
        models = ServerError504Models()

    monkeypatch.setattr("time.sleep", lambda s: None)
    settings = SimpleNamespace(gemini_api_key="secret-key", gemini_model="gemini-test", ai_timeout_seconds=5)
    service = GeminiAIService(settings, ServerError504Client())

    with pytest.raises(AIServiceError) as exc_info:
        service.generate_remark(date(1990, 1, 1), 95, 13, 180)

    assert str(exc_info.value) == MSG_SERVICE_UNAVAILABLE
    assert call_count == 4  # Initial attempt + 3 retries


def test_format_ai_error_sanitizes_raw_exceptions_and_preserves_clean_text():
    """Verify format_ai_error completely hides raw URLs, internal JSON, and error types."""
    raw_429 = "Gemini request failed: 429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'Quota reached', 'details': ['https://cloud.google.com/docs']}}"
    assert format_ai_error(raw_429) == MSG_RATE_LIMIT

    raw_503 = "Gemini request failed: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'Backend unavailable'}}"
    assert format_ai_error(raw_503) == MSG_SERVICE_UNAVAILABLE

    raw_504 = "504 DEADLINE_EXCEEDED: upstream timeout"
    assert format_ai_error(raw_504) == MSG_SERVICE_UNAVAILABLE

    # Raw traceback or json
    raw_traceback = "{'internal_error': True, 'traceback': 'Traceback (most recent call last)...'}"
    assert format_ai_error(raw_traceback) == MSG_SERVICE_UNAVAILABLE

    # Clean non-sensitive messages preserved
    assert format_ai_error(None) == "AI service is not configured or offline."
    assert format_ai_error("AI service is not configured.") == "AI service is not configured."
    assert format_ai_error("Custom clinical note") == "Custom clinical note"


def test_cooldown_skips_unnecessary_gemini_calls_when_quota_exhausted(monkeypatch):
    """Verify that hitting a 429 activates a 30-second cooldown that blocks redundant API calls."""
    call_count = 0

    class CountingModels:
        def generate_content(self, **kwargs):
            nonlocal call_count
            call_count += 1
            raise genai_errors.ClientError(
                429,
                {"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "message": "Quota exceeded"}},
            )

    class CountingClient:
        models = CountingModels()

    monkeypatch.setattr("time.sleep", lambda s: None)
    settings = SimpleNamespace(gemini_api_key="secret-key", gemini_model="gemini-test", ai_timeout_seconds=5)
    service = GeminiAIService(settings, CountingClient())

    # 1. First call: hits Gemini, fails with 429, sets cooldown
    with pytest.raises(AIServiceError) as exc_1:
        service.generate_remark(date(1990, 1, 1), 95, 13, 180)
    assert str(exc_1.value) == MSG_RATE_LIMIT
    assert call_count == 1

    # 2. Second call immediately after: cooldown is active, raises immediately without calling Gemini
    with pytest.raises(AIServiceError) as exc_2:
        service.generate_remark(date(1990, 1, 1), 95, 13, 180)
    assert str(exc_2.value) == MSG_RATE_LIMIT
    assert call_count == 1  # No additional network attempt!

    # 3. When cooldown expires / is reset, call attempts network again
    reset_rate_limit_cooldown()
    with pytest.raises(AIServiceError):
        service.generate_remark(date(1990, 1, 1), 95, 13, 180)
    assert call_count == 2


def test_error_logging_never_exposes_secrets_or_pii(monkeypatch, caplog):
    """Verify server logs do not leak API credentials or patient PII."""
    class ErrorClient:
        class models:
            @staticmethod
            def generate_content(**kwargs):
                raise genai_errors.ClientError(429, {"error": {"code": 429, "status": "RESOURCE_EXHAUSTED"}})

    monkeypatch.setattr("time.sleep", lambda s: None)
    settings = SimpleNamespace(gemini_api_key="super-secret-key-12345", gemini_model="gemini-test", ai_timeout_seconds=5)
    service = GeminiAIService(settings, ErrorClient())

    with caplog.at_level("DEBUG"):
        with pytest.raises(AIServiceError):
            service.generate_remark(date(1990, 1, 1), 95, 13, 180)

    log_text = caplog.text
    assert "super-secret-key-12345" not in log_text
    assert "1990-01-01" not in log_text
