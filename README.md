# Health Record AI

A Streamlit patient-record application using SQLite, SQLAlchemy, Pydantic validation, and optional Google Gemini health-risk summaries.

## Features

- Create, read, update, and delete patient records.
- Persistent SQLite storage with SQLAlchemy transactions.
- Search records by name or email.
- Validation for names, dates, email addresses, and blood measurements.
- Collection of multiple validation errors in one submission.
- Duplicate detection using normalized full name, date of birth, and email.
- Official `google-genai` integration with structured response validation.
- AI failure status, understandable error messages, and retry action.
- No patient names or email addresses are sent to Gemini.
- AI output is labelled as an informational health-risk indication, not a diagnosis.

## Requirements

- Python 3.11 or newer.
- Internet access is needed only for Gemini API calls.
- A Gemini API key is optional for the CRUD application and required for live AI generation.

## Installation (Windows PowerShell)

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

The private `.env` file is ignored by Git. Never paste an API key into source code, tests, screenshots, or the repository.

## Configuration

Edit `.env` locally:

```env
GEMINI_API_KEY=your-real-key
GEMINI_MODEL=an-accessible-model-id
AI_TIMEOUT_SECONDS=20
DATABASE_PATH=data/patients.db
```

`GEMINI_MODEL` must be a model available to the configured key. Check configuration without exposing the key:

```powershell
.\.venv\Scripts\python.exe scripts\check_setup.py
```

Run the minimal live Gemini test using only a synthetic one-word prompt:

```powershell
.\.venv\Scripts\python.exe scripts\check_setup.py --api
```

The live API check must pass before claiming Gemini generation works. Temporary 5xx errors are retried with bounded exponential backoff. If Gemini remains unavailable, patients are still saved with `ai_status=failed`; the application never fabricates remarks.

## Launch

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

Open the displayed local URL, normally `http://localhost:8501`.

## Database

The application creates `data/patients.db` automatically on first launch. The database contains:

- Patient identity and date of birth.
- Glucose, haemoglobin, and cholesterol values.
- AI remarks, status, error, model, and generation timestamp.
- Created and updated timestamps.

The database and the entire `data/` directory are ignored by Git because they can contain patient data. Tests use an in-memory SQLite database and do not modify the application database.

## Validation rules

- Full name is required and accepts letters, spaces, hyphens, apostrophes, and Roman numerals.
- Date of birth accepts `dd/mm/yyyy` and `dd.mm.yyyy`.
- Impossible and future dates are rejected.
- Email must have a valid address structure, including multi-part domains such as `.com.au`.
- Glucose, haemoglobin, and cholesterol are required finite numbers greater than zero.
- All validation errors are returned together.
- A duplicate is rejected only when normalized name, date of birth, and email all match.

## CRUD workflow

1. Use **Register Patient** to enter a patient and submit the form.
2. Use **Patient Records** to search and inspect saved records.
3. Expand a record to edit values or delete it after confirmation.
4. Changing health values or date of birth triggers a new AI analysis.
5. Changing only an email does not trigger a new AI call.
6. Use **Retry AI analysis** when a previous Gemini request failed.

## Verified assignment scenario

The exact 10 records from the supplied screenshots are preserved in [tests/assignment_records.py](tests/assignment_records.py). The scenario verifies:

- 6 accepted records.
- 4 rejected records.
- Record 2: invalid email.
- Record 4: impossible calendar date.
- Record 6: duplicate of record 1.
- Record 8: future date and invalid email, collected together.
- Email update to `gokul@infocare.com`.
- Deletion of one accepted record.
- Five records remaining.

## Tests

Run the complete suite:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Run a compilation check:

```powershell
.\.venv\Scripts\python.exe -m compileall -q app.py config database validators services ui tests scripts
```

## Project structure

```text
app.py                  Streamlit entry point
config/                 Environment-backed settings
database/               SQLite connection, model, and repository
services/               Patient orchestration and Gemini integration
validators/             Reusable patient validation
ui/                     Dashboard and Streamlit pages
tests/                  Unit and assignment scenario tests
scripts/check_setup.py  Local and optional Gemini setup check
```

## Privacy and limitations

- `.env`, databases, virtual environments, caches, and logs are ignored.
- The AI receives age and anonymized measurements only; names and email addresses are excluded.
- AI output is not medical advice or a diagnosis.
- Gemini availability, quota, and network conditions are external dependencies. A failed AI request does not delete or corrupt a valid patient record.

## GitHub preparation

Before uploading, verify:

```powershell
git status --short --ignored
```

Commit source, tests, documentation, and safe configuration templates only. Do not commit `.env`, `data/patients.db`, `.venv`, caches, logs, or generated screenshots.
