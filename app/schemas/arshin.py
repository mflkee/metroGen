from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class VriIdOut(BaseModel):
    certificate: str
    vri_id: str | None = None
    year_used: int | None = None
    error: str | None = None


class VriIdListOut(BaseModel):
    items: list[VriIdOut]


class VriDetailOut(BaseModel):
    certificate: str | None = None
    vri_id: str | None = None
    organization: str | None = None
    vrfDate: str | None = None
    validDate: str | None = None
    applicable: bool | None = None
    protocol_url: str | None = None
    regNumber: str | None = None
    mitypeNumber: str | None = None
    mitypeTitle: str | None = None
    mitypeType: str | None = None
    mitypeType_short: str | None = None
    manufactureNum: str | None = None
    manufactureYear: int | None = None
    rankCode: str | None = None
    rankTitle: str | None = None
    etalon_line: str | None = None
    raw: dict[str, Any] | None = None
    error: str | None = None


class VriDetailListOut(BaseModel):
    items: list[VriDetailOut]

    # Дубликаты схем протоколов удалены. Используйте app.schemas.protocol.
