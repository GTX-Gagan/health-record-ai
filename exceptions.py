class ApplicationError(Exception):
    """Base class for expected application errors."""


class ValidationError(ApplicationError):
    def __init__(self, errors: dict[str, str | list[str]]):
        self.errors = errors
        super().__init__("; ".join(f"{key}: {value}" for key, value in errors.items()))


class DuplicatePatientError(ApplicationError):
    """Raised when a normalized patient identity already exists."""


class PatientNotFoundError(ApplicationError):
    """Raised when a requested patient does not exist."""


class AIServiceError(ApplicationError):
    """Raised when Gemini cannot produce a validated result."""
