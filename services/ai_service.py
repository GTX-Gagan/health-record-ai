from datetime import date
import json
import time

from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic import BaseModel, Field, ValidationError

from config.settings import Settings, get_settings
from exceptions import AIServiceError

MAX_RETRIES = 3


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
        if not self.settings.gemini_model:
            raise AIServiceError("GEMINI_MODEL is not configured.")
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
                except genai_errors.ServerError:
                    if attempt == MAX_RETRIES:
                        raise
                    time.sleep(2 ** attempt)
            text = (response.text or "").strip()
            if not text:
                raise AIServiceError("Gemini returned an empty response.")
            return AIHealthRemark.model_validate(json.loads(text))
        except AIServiceError:
            raise
        except (genai_errors.APIError, ValidationError, ValueError, json.JSONDecodeError) as exc:
            raise AIServiceError(f"Gemini request failed: {exc}") from exc
        except Exception as exc:
            raise AIServiceError(f"Gemini request failed: {type(exc).__name__}.") from exc
