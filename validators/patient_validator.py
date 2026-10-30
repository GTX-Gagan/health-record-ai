from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import math
import re

from pydantic import BaseModel, ConfigDict, Field

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")
NAME_PATTERN = re.compile(r"^[A-Za-z]+(?:[ .'-][A-Za-z]+)*$")


class PatientInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str
    date_of_birth: date
    email: str
    glucose: Decimal = Field(gt=0)
    haemoglobin: Decimal = Field(gt=0)
    cholesterol: Decimal = Field(gt=0)


def parse_date_of_birth(value: str | date) -> date:
    if isinstance(value, date):
        result = value
    else:
        result = datetime.strptime(value.strip(), "%d.%m.%Y").date() if "." in value else datetime.strptime(value.strip(), "%d/%m/%Y").date()
    if result > date.today():
        raise ValueError("Date of birth cannot be in the future.")
    return result


def validate_patient_input(data: dict) -> tuple[PatientInput | None, dict[str, list[str]]]:
    errors: dict[str, list[str]] = {}
    name = str(data.get("full_name", "")).strip()
    if not name:
        errors.setdefault("full_name", []).append("Full name is required.")
    elif not NAME_PATTERN.fullmatch(name):
        errors.setdefault("full_name", []).append("Use letters, spaces, hyphens, apostrophes, or Roman numerals.")

    parsed_date = None
    try:
        parsed_date = parse_date_of_birth(data.get("date_of_birth", ""))
    except (TypeError, ValueError):
        errors.setdefault("date_of_birth", []).append("Enter a valid date as dd/mm/yyyy or dd.mm.yyyy.")

    email = str(data.get("email", "")).strip()
    if not EMAIL_PATTERN.fullmatch(email):
        errors.setdefault("email", []).append("Enter a valid email address.")

    numeric: dict[str, Decimal] = {}
    for field in ("glucose", "haemoglobin", "cholesterol"):
        raw = data.get(field, "")
        try:
            value = Decimal(str(raw).strip())
            if not value.is_finite() or not math.isfinite(float(value)) or value <= 0:
                raise ValueError
            numeric[field] = value
        except (InvalidOperation, TypeError, ValueError):
            errors.setdefault(field, []).append("Enter a finite number greater than zero.")

    if errors:
        return None, errors
    return PatientInput(
        full_name=name,
        date_of_birth=parsed_date,
        email=email.casefold(),
        **numeric,
    ), {}
