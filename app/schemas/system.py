from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ExportFileRead(BaseModel):
    path: str
    size_bytes: int
    modified_at: datetime


class ExportFolderRead(BaseModel):
    name: str
    path: str
    files_count: int
    modified_at: datetime
    files: list[ExportFileRead]


class DatabaseSnapshotRead(BaseModel):
    backend: str
    database: str | None
    host: str | None
    owners_count: int
    methodologies_count: int
    registry_entries_count: int
    active_registry_entries_count: int
    auxiliary_instruments_count: int
    etalon_devices_count: int
    etalon_certifications_count: int
    measuring_instruments_count: int
    protocols_count: int


class SystemStatusRead(BaseModel):
    app_name: str
    app_env: str
    exports_dir: str
    signatures_dir: str
    smtp_configured: bool
    pdf_generation_available: bool
    users_count: int
    active_users_count: int
    export_folders_count: int
    generated_files_count: int
    database: DatabaseSnapshotRead
    recent_exports: list[ExportFolderRead]
