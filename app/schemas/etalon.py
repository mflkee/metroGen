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


class EtalonUpsert(BaseModel):
    """Создание/обновление эталона. Ключ — ФИФ-номер (``reg_number``)."""

    reg_number: str = Field(..., min_length=1)
    title: str | None = None
    mitype_number: str | None = None
    notation: str | None = None
    modification: str | None = None
    manufacture_num: str | None = None
    manufacture_year: int | None = None
    rank_code: str | None = None
    rank_title: str | None = None
    schema_title: str | None = None

    certificate_no: str | None = None
    verification_date: date | None = None
    valid_to: date | None = None

    @field_validator("reg_number", mode="before")
    @classmethod
    def _strip_code(cls, value: Any) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("reg_number must not be empty")
        return text

    @field_validator(
        "title",
        "mitype_number",
        "notation",
        "modification",
        "manufacture_num",
        "rank_code",
        "rank_title",
        "schema_title",
        "certificate_no",
        mode="before",
    )
    @classmethod
    def _strip_optional(cls, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @field_validator("manufacture_year", mode="before")
    @classmethod
    def _coerce_year(cls, value: Any) -> int | None:
        if value in (None, ""):
            return None
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            raise ValueError("manufacture_year must be an integer") from None

    @field_validator("verification_date", "valid_to", mode="before")
    @classmethod
    def _coerce_date(cls, value: Any) -> date | None:
        return _parse_flexible_date(value)


class EtalonOut(BaseModel):
    id: int
    reg_number: str
    title: str | None
    mitype_number: str | None
    notation: str | None
    modification: str | None
    manufacture_num: str | None
    manufacture_year: int | None
    rank_code: str | None
    rank_title: str | None
    schema_title: str | None

    certificate_no: str | None
    verification_date: date | None
    valid_to: date | None

    @classmethod
    def from_model(cls, device: Any, certificate: Any | None = None) -> EtalonOut:
        return cls(
            id=device.id,
            reg_number=device.reg_number,
            title=device.title,
            mitype_number=device.mitype_number,
            notation=device.notation,
            modification=device.modification,
            manufacture_num=device.manufacture_num,
            manufacture_year=device.manufacture_year,
            rank_code=device.rank_code,
            rank_title=device.rank_title,
            schema_title=device.schema_title,
            certificate_no=getattr(certificate, "certificate_no", None),
            verification_date=getattr(certificate, "verification_date", None),
            valid_to=getattr(certificate, "valid_to", None),
        )
