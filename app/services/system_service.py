from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import User
from app.schemas.system import ExportFileRead, ExportFolderRead, SystemStatusRead
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
        users_count = await self._users_count()
        active_users_count = await self._users_count(active_only=True)
        return SystemStatusRead(
            app_name=settings.APP_NAME,
            app_env=settings.APP_ENV,
            exports_dir=str(exports_base),
            signatures_dir=str(settings.signatures_path),
            smtp_configured=self.notifications.is_configured(),
            pdf_generation_available=await pdf_generation_available(),
            users_count=users_count,
            active_users_count=active_users_count,
            export_folders_count=len([item for item in exports_base.iterdir() if item.is_dir()])
            if exports_base.exists()
            else 0,
            generated_files_count=sum(folder.files_count for folder in recent_exports),
            recent_exports=recent_exports,
        )

    async def _users_count(self, *, active_only: bool = False) -> int:
        stmt = select(func.count(User.id))
        if active_only:
            stmt = stmt.where(User.is_active.is_(True))
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
