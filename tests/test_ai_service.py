from datetime import date
from types import SimpleNamespace

from services.ai_service import GeminiAIService


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
