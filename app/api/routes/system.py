from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

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
    exports_base = get_exports_base().resolve()
    requested_path = Path(path).expanduser().resolve()
    try:
        requested_path.relative_to(exports_base)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="File is outside exports directory.") from exc

    if not requested_path.is_file():
        raise HTTPException(status_code=404, detail="Export file not found.")

    return FileResponse(requested_path)
