from datetime import date

from validators.patient_validator import parse_date_of_birth, validate_patient_input


def valid_data():
    return {"full_name": "Anne-Marie O'Neil", "date_of_birth": "29.02.2000", "email": "anne@example.com",
            "glucose": "95", "haemoglobin": "13.2", "cholesterol": "180"}


def test_accepts_both_date_formats():
    assert parse_date_of_birth("29.02.2000") == date(2000, 2, 29)
    assert parse_date_of_birth("29/02/2000") == date(2000, 2, 29)


def test_collects_multiple_errors():
    data = valid_data() | {"date_of_birth": "31.02.2020", "email": "hunter@gmail"}
    _, errors = validate_patient_input(data)
    assert {"date_of_birth", "email"} <= errors.keys()


def test_rejects_non_positive_and_non_finite_measurements():
    _, errors = validate_patient_input(valid_data() | {"glucose": "nan", "haemoglobin": "-1", "cholesterol": ""})
    assert {"glucose", "haemoglobin", "cholesterol"} <= errors.keys()
