"""Explicitly load the six accepted assignment records into the demo database.

This script is opt-in and is never imported by app.py. It uses the real
application database configured in .env and intentionally skips invalid and
duplicate assignment records.

Usage:
    python scripts/load_demo_data.py
    python scripts/load_demo_data.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.connection import SessionLocal, init_db
from database.models import Patient
from database.repository import PatientRepository, normalize_email, normalize_name
from exceptions import ApplicationError, DuplicatePatientError
from services.patient_service import PatientService
from tests.assignment_records import ASSIGNMENT_RECORDS
from validators.patient_validator import validate_patient_input


def load_demo_data(dry_run: bool = False) -> tuple[list[str], list[str]]:
    init_db()
    with SessionLocal() as session:
        existing = session.scalar(select(Patient.id).limit(1))
        if existing is not None and not dry_run:
            raise RuntimeError(
                "The demonstration database is not empty. "
                "Review it first; no records were changed."
            )

        service = PatientService(PatientRepository(session), ai_service=None)
        accepted: list[str] = []
        rejected: list[str] = []
        seen: set[tuple[str, object, str]] = set()

        for number, record in enumerate(ASSIGNMENT_RECORDS, start=1):
            validated, errors = validate_patient_input(record)
            if errors:
                reason = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in errors.items())
                rejected.append(f"Record {number}: {reason}")
                continue
            try:
                if dry_run:
                    identity = (
                        normalize_name(record["full_name"]),
                        validated.date_of_birth,
                        normalize_email(record["email"]),
                    )
                    if identity in seen:
                        raise DuplicatePatientError(
                            "A patient with the same name, date of birth, and email already exists."
                        )
                    seen.add(identity)
                    accepted.append(f"Record {number}: {record['full_name']}")
                else:
                    patient = service.create(record)
                    accepted.append(f"Record {number}: {patient.full_name}")
            except ApplicationError as exc:
                rejected.append(f"Record {number}: {exc}")

        return accepted, rejected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and classify records without writing to the database",
    )
    args = parser.parse_args()

    try:
        accepted, rejected = load_demo_data(dry_run=args.dry_run)
    except RuntimeError as exc:
        parser.error(str(exc))

    print("Accepted records:")
    for item in accepted:
        print(f"  [PASS] {item}")
    print("Rejected records:")
    for item in rejected:
        print(f"  [REJECTED] {item}")
    print(f"Summary: {len(accepted)} accepted, {len(rejected)} rejected")
    if args.dry_run:
        print("Dry run: no database records were written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
