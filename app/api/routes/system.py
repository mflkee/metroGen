from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.api.deps import CurrentUser, DbSession
from app.schemas.system import SystemStatusRead
from app.services.system_service import SystemService
from app.utils.paths import get_exports_base

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/status", response_model=SystemStatusRead)
async def system_status(_: CurrentUser, db: DbSession) -> SystemStatusRead:
    return await SystemService(db).get_status()


@router.get("/export-file")
async def export_file(
    _: CurrentUser,
    path: str = Query(..., min_length=1),
) -> FileResponse:
    requested_path = _resolve_export_path(path)
    if not requested_path.is_file():
        raise HTTPException(status_code=404, detail="Export file not found.")

    return FileResponse(requested_path)


@router.get("/export-folder-archive")
async def export_folder_archive(
    _: CurrentUser,
    path: str = Query(..., min_length=1),
) -> FileResponse:
    requested_path = _resolve_export_path(path)
    if not requested_path.is_dir():
        raise HTTPException(status_code=404, detail="Export folder not found.")

    archive_path = _build_export_archive(requested_path)
    return FileResponse(
        archive_path,
        media_type="application/zip",
        filename=f"{requested_path.name}.zip",
        background=BackgroundTask(_cleanup_archive, archive_path),
    )


def _resolve_export_path(path: str) -> Path:
    exports_base = get_exports_base().resolve()
    requested_path = Path(path).expanduser().resolve()
    try:
        requested_path.relative_to(exports_base)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="File is outside exports directory.") from exc
    return requested_path


def _build_export_archive(folder_path: Path) -> Path:
    temp_file = NamedTemporaryFile(prefix="metrogen-export-", suffix=".zip", delete=False)
    archive_path = Path(temp_file.name)
    temp_file.close()

    with ZipFile(archive_path, mode="w", compression=ZIP_DEFLATED) as archive:
        for item in sorted(folder_path.rglob("*")):
            if item.is_file():
                archive.write(item, arcname=item.relative_to(folder_path))

    return archive_path


def _cleanup_archive(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
