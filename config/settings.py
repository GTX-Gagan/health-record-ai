from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "")
    ai_timeout_seconds: int = int(os.getenv("AI_TIMEOUT_SECONDS", "20") or "20")
    database_path: str = os.getenv("DATABASE_PATH", "data/patients.db")

    @property
    def database_url(self) -> str:
        path = Path(self.database_path)
        if not path.is_absolute():
            path = ROOT_DIR / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
