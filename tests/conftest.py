import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repository import PatientRepository
from services.ai_service import reset_rate_limit_cooldown
from services.patient_service import PatientService


@pytest.fixture(autouse=True)
def clean_rate_limit_cooldown():
    """Ensure in-memory rate-limit cooldown state is isolated across test cases."""
    reset_rate_limit_cooldown()
    yield
    reset_rate_limit_cooldown()


@pytest.fixture
def service():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    yield PatientService(PatientRepository(session))
    session.close()
