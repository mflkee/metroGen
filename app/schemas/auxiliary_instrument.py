from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


def _parse_flexible_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    if not text:
        return None

    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError("invalid date format, expected DD.MM.YYYY, YYYY-MM-DD or MM/DD/YYYY")


class AuxiliaryInstrumentCreate(BaseModel):
    title: str = Field(..., min_length=1)
    reg_number: str = Field(..., min_length=1)
    modification: str | None = None
    manufacture_num: str = Field(..., min_length=1)
    certificate_no: str | None = None
    verification_date: date | None = None
    valid_to: date | None = None

    @field_validator("title", "reg_number", "manufacture_num", mode="before")
    @classmethod
    def _strip_required(cls, value: Any) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("field must not be empty")
        return text

    @field_validator("modification", "certificate_no", mode="before")
    @classmethod
    def _strip_optional(cls, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @field_validator("verification_date", "valid_to", mode="before")
    @classmethod
    def _coerce_date(cls, value: Any) -> date | None:
        return _parse_flexible_date(value)


class AuxiliaryInstrumentOut(BaseModel):
    id: int
    title: str
    reg_number: str
    modification: str | None
    manufacture_num: str
    certificate_no: str | None
    verification_date: date | None
    valid_to: date | None

    @classmethod
    def from_model(cls, model: Any) -> AuxiliaryInstrumentOut:
        return cls(
            id=model.id,
            title=model.title,
            reg_number=model.reg_number,
            modification=model.modification,
            manufacture_num=model.manufacture_num or "",
            certificate_no=model.certificate_no,
            verification_date=model.verification_date,
            valid_to=model.valid_to,
        )


class AuxiliaryInstrumentBulkUpsert(BaseModel):
    items: list[AuxiliaryInstrumentCreate] = Field(default_factory=list)
    replace_all: bool = False


class AuxiliaryInstrumentBulkResult(BaseModel):
    upserted: int
    deleted: int
