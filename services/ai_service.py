from datetime import date
import json
import logging
import time

from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic import BaseModel, Field, ValidationError

from config.settings import Settings, get_settings
from exceptions import AIServiceError

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RATE_LIMIT_COOLDOWN_SECONDS = 30
_last_rate_limit_timestamp: float = 0.0

MSG_RATE_LIMIT = "Gemini free-tier request limit reached. Please try again after the quota resets."
MSG_SERVICE_UNAVAILABLE = "The AI service is temporarily unavailable. Please try again later."


def reset_rate_limit_cooldown() -> None:
    """Reset the in-memory rate-limit cooldown tracker (used for tests and quota resets)."""
    global _last_rate_limit_timestamp
    _last_rate_limit_timestamp = 0.0


def is_rate_limit_error(exc: Exception) -> bool:
    """Detect HTTP 429 / RESOURCE_EXHAUSTED errors safely across genai error types."""
    code = getattr(exc, "code", None)
    status = getattr(exc, "status", None)
    exc_str = str(exc).upper()
    return (
        code == 429
        or status == "RESOURCE_EXHAUSTED"
        or "429" in exc_str
        or "RESOURCE_EXHAUSTED" in exc_str
    )


def is_service_unavailable_error(exc: Exception) -> bool:
    """Detect HTTP 503 / 504 / UNAVAILABLE errors safely across genai error types."""
    code = getattr(exc, "code", None)
    status = getattr(exc, "status", None)
    exc_str = str(exc).upper()
    return (
        code in (503, 504)
        or status in ("UNAVAILABLE", "DEADLINE_EXCEEDED")
        or "503" in exc_str
        or "504" in exc_str
        or "UNAVAILABLE" in exc_str
        or "DEADLINE_EXCEEDED" in exc_str
    )


def format_ai_error(raw_error: str | None) -> str:
    """Format stored AI error messages into clean, user-facing text.

    Ensures that raw Gemini exceptions, quota URLs, internal JSON objects,
    and tracebacks are never exposed to the frontend.
    """
    if not raw_error:
        return "AI service is not configured or offline."
    err_str = str(raw_error).strip()
    err_upper = err_str.upper()
    if (
        "429" in err_upper
        or "RESOURCE_EXHAUSTED" in err_upper
        or "REQUEST LIMIT" in err_upper
        or "QUOTA" in err_upper
        or "FREE-TIER" in err_upper
        or "FREE TIER" in err_upper
    ):
        return MSG_RATE_LIMIT
    if (
        "503" in err_upper
        or "504" in err_upper
        or "UNAVAILABLE" in err_upper
        or "DEADLINE_EXCEEDED" in err_upper
        or "GATEWAY" in err_upper
    ):
        return MSG_SERVICE_UNAVAILABLE
    if "NOT CONFIGURED" in err_upper or "API KEY" in err_upper or "GEMINI_MODEL" in err_upper:
        return err_str
    if any(
        token in err_str
        for token in ("{", "}", "http://", "https://", "Traceback", "ClientError", "ServerError", "APIError")
    ):
        return MSG_SERVICE_UNAVAILABLE
    return err_str


class AIHealthRemark(BaseModel):
    risk: str = Field(min_length=1)
    possible_risks: list[str] = Field(min_length=1)
    explanation: str = Field(min_length=1)
    next_steps: list[str] = Field(min_length=1)


class GeminiAIService:
    def __init__(self, settings: Settings | None = None, client=None):
        self.settings = settings or get_settings()
        self.client = client

    def _client(self):
        if not self.settings.gemini_api_key or self.settings.gemini_api_key == "your-api-key-here":
            raise AIServiceError("Gemini API key is not configured.")
        if self.client is None:
            self.client = genai.Client(
                api_key=self.settings.gemini_api_key,
                http_options=types.HttpOptions(timeout=self.settings.ai_timeout_seconds * 1000),
            )
        return self.client

    def generate_remark(self, dob: date, glucose, haemoglobin, cholesterol) -> AIHealthRemark:
        global _last_rate_limit_timestamp

        if not self.settings.gemini_model:
            raise AIServiceError("GEMINI_MODEL is not configured.")

        # Check if free-tier rate-limit cooldown is active to avoid unnecessary API requests
        now = time.time()
        if _last_rate_limit_timestamp > 0 and (now - _last_rate_limit_timestamp) < RATE_LIMIT_COOLDOWN_SECONDS:
            remaining = int(RATE_LIMIT_COOLDOWN_SECONDS - (now - _last_rate_limit_timestamp))
            logger.info("Free-tier quota cooldown active (%ds remaining); skipping unnecessary Gemini call.", remaining)
            raise AIServiceError(MSG_RATE_LIMIT)

        age = max(0, (date.today() - dob).days // 365)
        prompt = (
            "Return JSON only with keys risk, possible_risks, explanation, next_steps. "
            "Assess possible health risks, not a diagnosis. Include a medical disclaimer in next_steps. "
            f"Patient age: {age}. Glucose mg/dL: {glucose}. Haemoglobin g/dL: {haemoglobin}. "
            f"Total cholesterol mg/dL: {cholesterol}."
        )
        try:
            response = None
            for attempt in range(MAX_RETRIES + 1):
                try:
                    response = self._client().models.generate_content(
                        model=self.settings.gemini_model,
                        contents=prompt,
                        config={"response_mime_type": "application/json"},
                    )
                    break
                except genai_errors.ClientError as exc:
                    if is_rate_limit_error(exc):
                        _last_rate_limit_timestamp = time.time()
                        logger.warning(
                            "Gemini free-tier request limit reached (HTTP 429 / RESOURCE_EXHAUSTED). Skipping retries to respect quota."
                        )
                        raise AIServiceError(MSG_RATE_LIMIT) from exc
                    logger.error(
                        "Gemini API client error encountered (code %s).",
                        getattr(exc, "code", "4xx"),
                    )
                    raise AIServiceError(MSG_SERVICE_UNAVAILABLE) from exc
                except genai_errors.ServerError as exc:
                    if is_rate_limit_error(exc):
                        _last_rate_limit_timestamp = time.time()
                        logger.warning(
                            "Gemini rate limit error caught in ServerError. Skipping retries."
                        )
                        raise AIServiceError(MSG_RATE_LIMIT) from exc
                    if attempt == MAX_RETRIES:
                        logger.error(
                            "Gemini API server error persisted after %d retries (HTTP %s).",
                            MAX_RETRIES,
                            getattr(exc, "code", "503/504"),
                        )
                        raise AIServiceError(MSG_SERVICE_UNAVAILABLE) from exc
                    logger.info(
                        "Transient Gemini API server error on attempt %d/%d (code %s). Backing off...",
                        attempt + 1,
                        MAX_RETRIES,
                        getattr(exc, "code", "5xx"),
                    )
                    time.sleep(2 ** attempt)
            if response is None or not (response.text or "").strip():
                logger.error("Gemini API returned an empty response body.")
                raise AIServiceError(MSG_SERVICE_UNAVAILABLE)
            text = (response.text or "").strip()
            return AIHealthRemark.model_validate(json.loads(text))
        except AIServiceError:
            raise
        except genai_errors.APIError as exc:
            if is_rate_limit_error(exc):
                _last_rate_limit_timestamp = time.time()
                logger.warning("Gemini free-tier request limit reached (HTTP 429).")
                raise AIServiceError(MSG_RATE_LIMIT) from exc
            if is_service_unavailable_error(exc):
                logger.error("Gemini API service unavailable (code %s).", getattr(exc, "code", "5xx"))
                raise AIServiceError(MSG_SERVICE_UNAVAILABLE) from exc
            logger.error("Gemini API error encountered (code %s).", getattr(exc, "code", "unknown"))
            raise AIServiceError(MSG_SERVICE_UNAVAILABLE) from exc
        except (ValidationError, ValueError, json.JSONDecodeError) as exc:
            logger.error("Failed to parse Gemini response payload: %s", type(exc).__name__)
            raise AIServiceError(MSG_SERVICE_UNAVAILABLE) from exc
        except Exception as exc:
            if is_rate_limit_error(exc):
                _last_rate_limit_timestamp = time.time()
                logger.warning("Gemini free-tier request limit reached: %s", type(exc).__name__)
                raise AIServiceError(MSG_RATE_LIMIT) from exc
            if is_service_unavailable_error(exc):
                logger.error("Gemini service unavailable: %s", type(exc).__name__)
                raise AIServiceError(MSG_SERVICE_UNAVAILABLE) from exc
            logger.error("Unexpected error during AI health remark generation: %s", type(exc).__name__)
            raise AIServiceError(MSG_SERVICE_UNAVAILABLE) from exc
