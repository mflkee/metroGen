from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProtocolContextItem(BaseModel):
    certificate: str | None = None  # номер свидетельства из Excel
    vri_id: str | None = None  # найденный vri_id
    filename: str | None = None  # предлагаемое имя файла (без расширения)
    context: dict[str, Any] | None = None  # полный контекст для шаблона/рендера
    raw_details: dict[str, Any] | None = None  # сырой ответ /vri/{id} (для отладки)
    error: str | None = None


class ProtocolContextListOut(BaseModel):
    items: list[ProtocolContextItem]


class GenerationErrorItem(BaseModel):
    row: int | None = None
    serial: str | None = None
    certificate: str | None = None
    reason: str | None = None


class GenerationResultRead(BaseModel):
    files: list[str] = Field(default_factory=list)
    count: int = 0
    run_id: str | None = None
    export_folder: str | None = None
    export_folder_name: str | None = None
    errors: list[GenerationErrorItem] = Field(default_factory=list)


class GenerationJobAcceptedRead(BaseModel):
    job_id: str
    status: str
    stage: str
    started_at: datetime


class GenerationJobRead(BaseModel):
    job_id: str
    status: str
    stage: str
    total_items: int = 0
    processed_items: int = 0
    saved_count: int = 0
    failed_count: int = 0
    started_at: datetime
    updated_at: datetime
    finished_at: datetime | None = None
    error: str | None = None
    result: GenerationResultRead | None = None
