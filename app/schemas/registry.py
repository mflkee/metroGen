from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class RegistryEntryRead(BaseModel):
    id: int
    source_file: str
    source_sheet: str | None = None
    instrument_kind: str | None = None
    row_index: int
    normalized_serial: str | None = None
    document_no: str | None = None
    protocol_no: str | None = None
    owner_name_raw: str | None = None
    methodology_raw: str | None = None
    verification_date: date | None = None
    valid_to: date | None = None
    is_active: bool
    loaded_at: datetime


class RegistryEntryListRead(BaseModel):
    total: int
    items: list[RegistryEntryRead] = Field(default_factory=list)
