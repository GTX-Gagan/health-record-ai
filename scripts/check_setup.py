"""Verify that the development environment is ready.

Usage:
    python scripts/check_setup.py          # local checks only (no network)
    python scripts/check_setup.py --api    # also test a real Gemini API call

The API key is never printed. Only whether it is set, and its length.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIRED_PYTHON = (3, 11)
REQUIRED_PACKAGES = [
    "streamlit",
    "SQLAlchemy",
    "pydantic",
    "google-genai",
    "python-dotenv",
    "pandas",
    "pytest",
]
PLACEHOLDER_KEY = "your-api-key-here"
MAX_API_RETRIES = 3


def report(ok: bool, message: str) -> bool:
    """Print one check result and return whether it passed."""
    print(f"  [{'PASS' if ok else 'FAIL'}] {message}")
    return ok


def check_python() -> bool:
    version = sys.version_info
    return report(
        version >= REQUIRED_PYTHON,
        f"Python {version.major}.{version.minor}.{version.micro} "
        f"(need {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+)",
    )


def check_virtualenv() -> bool:
    in_venv = sys.prefix != sys.base_prefix
    return report(in_venv, "Running inside a virtual environment" if in_venv
                  else "Not inside a virtual environment - activate .venv first")


def check_packages() -> bool:
    all_ok = True
    for package in REQUIRED_PACKAGES:
        try:
            version = importlib.metadata.version(package)
            report(True, f"{package} {version}")
        except importlib.metadata.PackageNotFoundError:
            all_ok = report(False, f"{package} is not installed") and all_ok
    return all_ok


def check_env_file() -> bool:
    from dotenv import load_dotenv

    env_path = PROJECT_ROOT / ".env"
    if not report(env_path.exists(), ".env file exists"):
        print("         Create it with:  copy .env.example .env   (Windows)")
        print("                          cp .env.example .env     (macOS/Linux)")
        return False
    load_dotenv(env_path)

    gitignore = PROJECT_ROOT / ".gitignore"
    ignored = gitignore.exists() and ".env" in gitignore.read_text().splitlines()
    report(ignored, ".env is listed in .gitignore")

    key = os.getenv("GEMINI_API_KEY", "").strip()
    key_ok = bool(key) and key != PLACEHOLDER_KEY
    report(key_ok, f"GEMINI_API_KEY is set ({len(key)} characters)" if key_ok
           else "GEMINI_API_KEY is missing or still the placeholder")

    model = os.getenv("GEMINI_MODEL", "").strip()
    report(bool(model), f"GEMINI_MODEL = {model}" if model
           else "GEMINI_MODEL is empty - run with --api to see available models")
    return ignored and key_ok


def check_api() -> bool:
    """List available models and make one tiny real request."""
    from google import genai
    from google.genai import errors, types

    key = os.getenv("GEMINI_API_KEY", "").strip()
    timeout_ms = int(os.getenv("AI_TIMEOUT_SECONDS", "20")) * 1000
    client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=timeout_ms))

    try:
        models = [
            m.name.removeprefix("models/")
            for m in client.models.list()
            if "generateContent" in (m.supported_actions or [])
            and "flash" in m.name
        ]
        report(True, f"Connected to Gemini API - {len(models)} Flash text models available:")
        for name in sorted(models):
            print(f"           - {name}")

        model = os.getenv("GEMINI_MODEL", "").strip()
        if not model:
            print("\n  Set GEMINI_MODEL in .env to one of the models above, then run again.")
            return False

        response = None
        for attempt in range(MAX_API_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents="Reply with exactly one word: OK",
                )
                break
            except errors.ServerError as exc:
                if attempt == MAX_API_RETRIES:
                    raise
                delay = 2 ** attempt
                print(f"  Temporary Gemini HTTP {exc.code}; retrying in {delay}s "
                      f"(attempt {attempt + 2}/{MAX_API_RETRIES + 1})...")
                time.sleep(delay)
        return report(bool(response.text), f"Test request to {model} answered: {response.text.strip()!r}")

    except errors.ClientError as exc:
        hints = {
            400: "Request rejected - often an invalid API key or model name.",
            401: "API key not accepted.",
            403: "API key lacks permission for this API or model.",
            404: "Model not found - check GEMINI_MODEL against the list above.",
            429: "Rate limit or quota reached - wait a minute and retry.",
        }
        return report(False, f"HTTP {exc.code}: {hints.get(exc.code, exc.message)}")
    except errors.ServerError as exc:
        return report(False, f"HTTP {exc.code}: Gemini service unavailable - retry later.")
    except Exception as exc:  # network failure, timeout, DNS, proxy
        return report(False, f"Could not reach Gemini ({type(exc).__name__}). Check your internet connection.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--api", action="store_true", help="also test a real Gemini API call")
    args = parser.parse_args()

    print("\n1. Python")
    ok = check_python() & check_virtualenv()
    print("\n2. Packages")
    ok &= check_packages()
    print("\n3. Configuration")
    env_ok = check_env_file()
    ok &= env_ok

    if args.api:
        print("\n4. Gemini API connectivity")
        ok &= env_ok and check_api()

    print("\nAll checks passed." if ok else "\nSome checks failed - see above.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
