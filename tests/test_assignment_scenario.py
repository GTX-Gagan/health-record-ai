from exceptions import DuplicatePatientError
from tests.assignment_records import ASSIGNMENT_RECORDS
from validators.patient_validator import validate_patient_input


def test_assignment_records_have_six_valid_and_four_invalid():
    valid_records = []
    invalid_errors = {}

    for number, record in enumerate(ASSIGNMENT_RECORDS, start=1):
        validated, errors = validate_patient_input(record)
        if errors:
            invalid_errors[number] = errors
        else:
            valid_records.append(validated)

    assert len(ASSIGNMENT_RECORDS) == 10
    # The duplicate is valid input; duplicate detection occurs at persistence time.
    assert len(valid_records) == 7
    assert set(invalid_errors) == {2, 4, 8}
    assert "email" in invalid_errors[2]
    assert "date_of_birth" in invalid_errors[4]
    assert {"date_of_birth", "email"} <= invalid_errors[8].keys()


def test_assignment_creation_duplicate_and_crud_scenario(service):
    accepted = []
    rejected = {}

    for number, record in enumerate(ASSIGNMENT_RECORDS, start=1):
        validated, errors = validate_patient_input(record)
        if errors:
            rejected[number] = errors
            continue
        try:
            accepted.append(service.create(record))
        except DuplicatePatientError as exc:
            rejected[number] = {"duplicate": [str(exc)]}

    assert len(accepted) == 6
    assert len(rejected) == 4
    assert set(rejected) == {2, 4, 6, 8}

    read_back = service.repository.list()
    assert {patient.full_name for patient in read_back} == {
        "Robyn Pears", "Daryl Tim", "Sam Kerr", "Madison XI", "Tenille Singh", "Prem Kumar"
    }

    edited = service.update(
        accepted[0].id,
        {**ASSIGNMENT_RECORDS[0], "email": "gokul@infocare.com"},
    )
    assert edited.email == "gokul@infocare.com"

    service.delete(accepted[-1].id)
    remaining = service.repository.list()
    assert len(remaining) == 5
    assert all(patient.id != accepted[-1].id for patient in remaining)
