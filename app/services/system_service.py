from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import (
    AuxiliaryVerificationInstrument,
    EtalonCertification,
    EtalonDevice,
    MeasuringInstrument,
    Methodology,
    Owner,
    Protocol,
    User,
    VerificationRegistryEntry,
)
from app.schemas.system import (
    DatabaseSnapshotRead,
    ExportFileRead,
    ExportFolderRead,
    SystemStatusRead,
)
from app.services.notification_service import NotificationService
from app.services.pdf import pdf_generation_available
from app.utils.paths import get_exports_base


class SystemService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.notifications = NotificationService()

    async def get_status(self) -> SystemStatusRead:
        exports_base = get_exports_base()
        recent_exports = _collect_recent_exports(exports_base)
        users_count, active_users_count, database_snapshot = await asyncio.gather(
            self._users_count(),
            self._users_count(active_only=True),
            self._database_snapshot(),
        )
        export_folders_count, generated_files_count = _collect_export_totals(exports_base)
        return SystemStatusRead(
            app_name=settings.APP_NAME,
            app_env=settings.APP_ENV,
            exports_dir=str(exports_base),
            signatures_dir=str(settings.signatures_path),
            smtp_configured=self.notifications.is_configured(),
            pdf_generation_available=await pdf_generation_available(),
            users_count=users_count,
            active_users_count=active_users_count,
            export_folders_count=export_folders_count,
            generated_files_count=generated_files_count,
            database=database_snapshot,
            recent_exports=recent_exports,
        )

    async def _users_count(self, *, active_only: bool = False) -> int:
        stmt = select(func.count(User.id))
        if active_only:
            stmt = stmt.where(User.is_active.is_(True))
        result = await self.session.execute(stmt)
        return int(result.scalar() or 0)

    async def _database_snapshot(self) -> DatabaseSnapshotRead:
        backend = "not-configured"
        database_name: str | None = None
        host: str | None = None
        if settings.DATABASE_URL:
            url = make_url(settings.DATABASE_URL)
            backend = url.get_backend_name()
            database_name = url.database
            host = url.host

        (
            owners_count,
            methodologies_count,
            registry_entries_count,
            active_registry_entries_count,
            auxiliary_instruments_count,
            etalon_devices_count,
            etalon_certifications_count,
            measuring_instruments_count,
            protocols_count,
        ) = await asyncio.gather(
            self._count_rows(Owner),
            self._count_rows(Methodology),
            self._count_rows(VerificationRegistryEntry),
            self._count_rows(
                VerificationRegistryEntry,
                VerificationRegistryEntry.is_active.is_(True),
            ),
            self._count_rows(AuxiliaryVerificationInstrument),
            self._count_rows(EtalonDevice),
            self._count_rows(EtalonCertification),
            self._count_rows(MeasuringInstrument),
            self._count_rows(Protocol),
        )

        return DatabaseSnapshotRead(
            backend=backend,
            database=database_name,
            host=host,
            owners_count=owners_count,
            methodologies_count=methodologies_count,
            registry_entries_count=registry_entries_count,
            active_registry_entries_count=active_registry_entries_count,
            auxiliary_instruments_count=auxiliary_instruments_count,
            etalon_devices_count=etalon_devices_count,
            etalon_certifications_count=etalon_certifications_count,
            measuring_instruments_count=measuring_instruments_count,
            protocols_count=protocols_count,
        )

    async def _count_rows(self, model: type, *conditions: object) -> int:
        stmt = select(func.count()).select_from(model)
        for condition in conditions:
            stmt = stmt.where(condition)
        result = await self.session.execute(stmt)
        return int(result.scalar() or 0)


def _collect_recent_exports(base_path: Path, *, limit: int = 6) -> list[ExportFolderRead]:
    if not base_path.exists():
        return []

    folders = sorted(
        [item for item in base_path.iterdir() if item.is_dir()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )[:limit]

    collected: list[ExportFolderRead] = []
    for folder in folders:
        files = sorted(
            [item for item in folder.iterdir() if item.is_file()],
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )[:8]
        file_items = [
            ExportFileRead(
                path=str(path),
                size_bytes=path.stat().st_size,
                modified_at=datetime.fromtimestamp(path.stat().st_mtime),
            )
            for path in files
        ]
        collected.append(
            ExportFolderRead(
                name=folder.name,
                path=str(folder),
                files_count=len([item for item in folder.iterdir() if item.is_file()]),
                modified_at=datetime.fromtimestamp(folder.stat().st_mtime),
                files=file_items,
            )
        )
    return collected


def _collect_export_totals(base_path: Path) -> tuple[int, int]:
    if not base_path.exists():
        return 0, 0

    folders_count = 0
    files_count = 0
    for item in base_path.iterdir():
        if not item.is_dir():
            continue
        folders_count += 1
        files_count += sum(1 for child in item.iterdir() if child.is_file())
    return folders_count, files_count
