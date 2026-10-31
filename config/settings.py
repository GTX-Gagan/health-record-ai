from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _get_setting(key: str, default: str = "") -> str:
    """Retrieve setting from Streamlit secrets (Streamlit Cloud), falling back to os.environ."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            val = st.secrets[key]
            if val is not None and str(val).strip():
                return str(val).strip()
    except Exception:
        pass
    return os.getenv(key, default)


class Settings:
    @property
    def gemini_api_key(self) -> str:
        return _get_setting("GEMINI_API_KEY", "")

    @property
    def gemini_model(self) -> str:
        return _get_setting("GEMINI_MODEL", "")

    @property
    def ai_timeout_seconds(self) -> int:
        val = _get_setting("AI_TIMEOUT_SECONDS", "20")
        try:
            return int(val)
        except (ValueError, TypeError):
            return 20

    @property
    def database_path(self) -> str:
        return _get_setting("DATABASE_PATH", "data/patients.db")

    @property
    def database_url(self) -> str:
        db_url = _get_setting("DATABASE_URL", "")
        if db_url:
            return db_url
        path = Path(self.database_path)
        if not path.is_absolute():
            path = ROOT_DIR / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
