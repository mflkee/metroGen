from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ProtocolContextItem(BaseModel):
    certificate: str | None = None  # номер свидетельства из Excel
    vri_id: str | None = None  # найденный vri_id
    filename: str | None = None  # предлагаемое имя файла (без расширения)
    context: dict[str, Any] | None = None  # полный контекст для шаблона/рендера
    raw_details: dict[str, Any] | None = None  # сырой ответ /vri/{id} (для отладки)
    error: str | None = None


class ProtocolContextListOut(BaseModel):
    items: list[ProtocolContextItem]
