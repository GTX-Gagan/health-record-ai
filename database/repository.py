from datetime import date
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from database.models import Patient


def normalize_name(value: str) -> str:
    return " ".join(value.casefold().split())


def normalize_email(value: str) -> str:
    return value.strip().casefold()


def find_duplicate(session: Session, name: str, dob: date, email: str, exclude_id: int | None = None):
    statement = select(Patient).where(
        Patient.date_of_birth == dob,
        Patient.email == normalize_email(email),
    )
    matches = session.scalars(statement).all()
    wanted = normalize_name(name)
    return next((patient for patient in matches if normalize_name(patient.full_name) == wanted
                 and patient.id != exclude_id), None)


class PatientRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self, search: str = "") -> list[Patient]:
        statement = select(Patient).order_by(Patient.created_at.desc())
        if search.strip():
            term = f"%{search.strip()}%"
            statement = statement.where(or_(Patient.full_name.ilike(term), Patient.email.ilike(term)))
        return list(self.session.scalars(statement))

    def get(self, patient_id: int) -> Patient | None:
        return self.session.get(Patient, patient_id)

    def add(self, patient: Patient) -> Patient:
        self.session.add(patient)
        self.session.commit()
        self.session.refresh(patient)
        return patient

    def update(self, patient: Patient) -> Patient:
        self.session.commit()
        self.session.refresh(patient)
        return patient

    def delete(self, patient: Patient) -> None:
        self.session.delete(patient)
        self.session.commit()
