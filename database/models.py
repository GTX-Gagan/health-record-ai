from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    glucose: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    haemoglobin: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    cholesterol: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)
    ai_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    ai_error: Mapped[str | None] = mapped_column(Text)
    ai_model: Mapped[str | None] = mapped_column(String(100))
    ai_generated_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
