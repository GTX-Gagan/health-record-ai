import pytest
from types import SimpleNamespace

from exceptions import AIServiceError, DuplicatePatientError, PatientNotFoundError
from services.ai_service import AIHealthRemark, MSG_RATE_LIMIT, MSG_SERVICE_UNAVAILABLE


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


def test_patient_creation_succeeds_when_gemini_is_unavailable(service):
    """Confirm that saving patient records still works when Gemini returns 429 or 503."""
    class RateLimitAI:
        settings = type("Settings", (), {"gemini_model": "gemini-test"})()
        def generate_remark(self, *args):
            raise AIServiceError(MSG_RATE_LIMIT)

    service.ai_service = RateLimitAI()
    patient = service.create({
        "full_name": "Quota Exceeded Patient",
        "date_of_birth": "20/08/1982",
        "email": "quota.test@example.com",
        "glucose": "120",
        "haemoglobin": "13.5",
        "cholesterol": "210",
    })

    assert patient.id is not None
    assert patient.ai_status == "failed"
    assert patient.ai_error == MSG_RATE_LIMIT
    assert patient.remarks is None

    # Verify retrieval from repository confirms persistence
    saved = service.repository.get(patient.id)
    assert saved is not None
    assert saved.full_name == "Quota Exceeded Patient"
    assert saved.ai_status == "failed"
    assert saved.ai_error == MSG_RATE_LIMIT


def test_rapid_concurrent_duplicate_submission_rejected_during_ai_generation(service):
    """Verify that an identical submission is rejected as a duplicate even while the first call's AI generation is in flight."""
    attempted_duplicate = []

    class InFlightAIService:
        settings = SimpleNamespace(gemini_model="gemini-test")

        def generate_remark(self, *args):
            # Attempt a concurrent submission with the exact same identity
            try:
                service.create(patient_data("inflight@example.com"))
            except DuplicatePatientError as exc:
                attempted_duplicate.append(str(exc))
            return AIHealthRemark(
                risk="low",
                possible_risks=["None"],
                explanation="Normal vitals.",
                next_steps=["Routine care; not a diagnosis."],
            )

    service.ai_service = InFlightAIService()
    first_patient = service.create(patient_data("inflight@example.com"))

    assert first_patient.id is not None
    assert first_patient.ai_status == "completed"
    # Verify the concurrent submission was caught and rejected immediately
    assert len(attempted_duplicate) == 1
    assert "already exists" in attempted_duplicate[0]


def test_ai_failure_after_persistence_preserves_record_with_failed_status(service):
    """Verify patient record remains safely persisted in the database when AI fails after persistence."""
    class FailingAIService:
        settings = SimpleNamespace(gemini_model="gemini-test")

        def generate_remark(self, *args):
            raise AIServiceError(MSG_SERVICE_UNAVAILABLE)

    service.ai_service = FailingAIService()
    patient = service.create({
        "full_name": "Persistence Preserved Patient",
        "date_of_birth": "12/04/1988",
        "email": "preserved.patient@example.com",
        "glucose": "105",
        "haemoglobin": "14.2",
        "cholesterol": "195",
    })

    assert patient.id is not None
    assert patient.ai_status == "failed"
    assert patient.ai_error == MSG_SERVICE_UNAVAILABLE
    assert patient.remarks is None  # Never create fabricated remarks

    retrieved = service.repository.get(patient.id)
    assert retrieved is not None
    assert retrieved.full_name == "Persistence Preserved Patient"
    assert retrieved.ai_status == "failed"
    assert retrieved.remarks is None


def test_retry_updates_existing_record_and_does_not_create_new_record(service):
    """Verify retry_ai updates the existing record by ID and never creates duplicate records."""
    class RecoveringAIService:
        settings = SimpleNamespace(gemini_model="gemini-test")
        should_succeed = False

        def generate_remark(self, *args):
            if not self.should_succeed:
                raise AIServiceError(MSG_RATE_LIMIT)
            return AIHealthRemark(
                risk="low",
                possible_risks=["No abnormal findings"],
                explanation="Standard screening.",
                next_steps=["Regular follow-up; not a diagnosis."],
            )

    ai = RecoveringAIService()
    service.ai_service = ai

    patient = service.create({
        "full_name": "Retry Record Patient",
        "date_of_birth": "14/09/1992",
        "email": "retry.record@example.com",
        "glucose": "98",
        "haemoglobin": "13.6",
        "cholesterol": "175",
    })
    original_id = patient.id
    assert patient.ai_status == "failed"

    initial_total = len(service.repository.list())

    # Now recover AI service and trigger manual retry
    ai.should_succeed = True
    retried = service.retry_ai(original_id)

    assert retried.id == original_id  # Exactly the same database row
    assert retried.ai_status == "completed"
    assert retried.remarks is not None
    assert len(service.repository.list()) == initial_total  # No new record created!
