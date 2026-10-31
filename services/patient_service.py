from database.models import utc_now

from database.models import Patient
from database.repository import PatientRepository, find_duplicate, normalize_email
from exceptions import AIServiceError, DuplicatePatientError, PatientNotFoundError, ValidationError
from services.ai_service import format_ai_error
from validators.patient_validator import PatientInput, validate_patient_input


class PatientService:
    def __init__(self, repository: PatientRepository, ai_service=None):
        self.repository = repository
        self.ai_service = ai_service

    def _validated(self, data: dict) -> PatientInput:
        patient, errors = validate_patient_input(data)
        if errors:
            raise ValidationError(errors)
        return patient

    def create(self, data: dict) -> Patient:
        values = self._validated(data)
        if find_duplicate(self.repository.session, values.full_name, values.date_of_birth, values.email):
            raise DuplicatePatientError("A patient with the same name, date of birth, and email already exists.")

        # 1. Persist validated patient record with AI status pending BEFORE calling Gemini
        patient = Patient(**values.model_dump())
        patient.ai_status = "pending"
        patient.ai_error = None
        patient = self.repository.add(patient)

        # 2. Trigger AI analysis and update the persisted record
        self._generate_ai(patient)
        return self.repository.update(patient)

    def update(self, patient_id: int, data: dict) -> Patient:
        patient = self.repository.get(patient_id)
        if patient is None:
            raise PatientNotFoundError("Patient not found.")
        values = self._validated(data)
        if find_duplicate(self.repository.session, values.full_name, values.date_of_birth, values.email, patient_id):
            raise DuplicatePatientError("A matching patient already exists.")
        health_changed = any(getattr(patient, field) != getattr(values, field)
                             for field in ("date_of_birth", "glucose", "haemoglobin", "cholesterol"))
        for field, value in values.model_dump().items():
            setattr(patient, field, value)
        patient.email = normalize_email(patient.email)
        if health_changed:
            patient.ai_status = "pending"
            patient.ai_error = None
            self.repository.update(patient)
            self._generate_ai(patient)
        return self.repository.update(patient)

    def delete(self, patient_id: int) -> None:
        patient = self.repository.get(patient_id)
        if patient is None:
            raise PatientNotFoundError("Patient not found.")
        self.repository.delete(patient)

    def _generate_ai(self, patient: Patient) -> None:
        patient.ai_status = "pending"
        patient.ai_error = None
        if self.ai_service is None:
            patient.ai_status = "failed"
            patient.ai_error = "AI service is not configured."
            return
        try:
            result = self.ai_service.generate_remark(
                patient.date_of_birth, patient.glucose, patient.haemoglobin, patient.cholesterol
            )
            patient.remarks = result.model_dump_json(indent=2)
            patient.ai_status = "completed"
            patient.ai_model = getattr(self.ai_service.settings, "gemini_model", None)
            patient.ai_generated_at = utc_now()
        except AIServiceError as exc:
            patient.ai_status = "failed"
            patient.ai_error = format_ai_error(str(exc))
            patient.remarks = None
            patient.ai_model = None
            patient.ai_generated_at = None
        except Exception as exc:
            patient.ai_status = "failed"
            patient.ai_error = format_ai_error(str(exc))
            patient.remarks = None
            patient.ai_model = None
            patient.ai_generated_at = None

    def retry_ai(self, patient_id: int) -> Patient:
        patient = self.repository.get(patient_id)
        if patient is None:
            raise PatientNotFoundError("Patient not found.")
        self._generate_ai(patient)
        return self.repository.update(patient)
