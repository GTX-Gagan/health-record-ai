import pytest

from exceptions import DuplicatePatientError, PatientNotFoundError
from services.ai_service import AIHealthRemark


def patient_data(email="anne@example.com"):
    return {"full_name": "Anne Marie", "date_of_birth": "01/01/1990", "email": email,
            "glucose": "95", "haemoglobin": "13", "cholesterol": "180"}


def test_create_read_update_delete(service):
    patient = service.create(patient_data())
    assert patient.id is not None
    updated = service.update(patient.id, patient_data("gokul@infocare.com"))
    assert updated.email == "gokul@infocare.com"
    service.delete(patient.id)
    with pytest.raises(PatientNotFoundError):
        service.delete(patient.id)


def test_duplicate_identity_is_rejected(service):
    service.create(patient_data())
    with pytest.raises(DuplicatePatientError):
        service.create(patient_data())


class FailingAI:
    def __init__(self):
        self.settings = type("Settings", (), {"gemini_model": "test-model"})()
        self.calls = 0

    def generate_remark(self, *args):
        self.calls += 1
        if self.calls == 1:
            from exceptions import AIServiceError

            raise AIServiceError("temporary Gemini failure")
        return AIHealthRemark(
            risk="low",
            possible_risks=["None identified"],
            explanation="Screening summary.",
            next_steps=["Discuss with a clinician; this is not a diagnosis."],
        )


def test_ai_failure_preserves_record_and_retry_updates_it(service):
    ai = FailingAI()
    service.ai_service = ai
    patient = service.create(patient_data())
    assert patient.id is not None
    assert patient.ai_status == "failed"
    assert patient.ai_error == "temporary Gemini failure"

    retried = service.retry_ai(patient.id)
    assert retried.ai_status == "completed"
    assert retried.remarks is not None
    assert retried.ai_model == "test-model"


def test_ai_failure_clears_stale_remarks(service):
    class AlwaysFailingAI(FailingAI):
        def generate_remark(self, *args):
            from exceptions import AIServiceError

            raise AIServiceError("service unavailable")

    ai = AlwaysFailingAI()
    service.ai_service = ai
    patient = service.create(patient_data())
    patient.remarks = '{"risk":"old"}'
    patient.ai_model = "old-model"
    patient.ai_generated_at = patient.created_at
    service.repository.update(patient)

    service.retry_ai(patient.id)
    refreshed = service.repository.get(patient.id)
    assert refreshed.ai_status == "failed"
    assert refreshed.remarks is None
    assert refreshed.ai_model is None
    assert refreshed.ai_generated_at is None
