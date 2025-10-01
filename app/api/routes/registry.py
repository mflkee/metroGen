from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.registry_ingest import (
    REGISTRY_SERIAL_KEYS,
    ingest_registry_rows,
)
from app.utils.excel import read_rows_with_required_headers

router = APIRouter(prefix="/api/v1/registry", tags=["registry"])


@router.post("/import")
async def import_registry_file(
    db_file: UploadFile = File(...),
    *,
    source_sheet: str | None = Query(
        None,
        description="Имя листа в Excel, если нужно жёстко указать",
    ),
    instrument_kind: str | None = Query(
        None,
        description="Тип средств измерений (например, controllers, manometers)",
    ),
    header_row: int = Query(5, ge=1, description="Номер строки с заголовками"),
    data_start_row: int = Query(6, ge=1, description="Первая строка с данными"),
    session: AsyncSession = Depends(get_db),
):
    payload = await db_file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="empty registry file")

    rows = read_rows_with_required_headers(
        payload,
        header_row=header_row,
        data_start_row=data_start_row,
        required_headers=REGISTRY_SERIAL_KEYS,
    )
    if not rows:
        raise HTTPException(status_code=400, detail="registry file has no serial entries")

    result = await ingest_registry_rows(
        session,
        source_file=db_file.filename or "registry.xlsx",
        rows=rows,
        source_sheet=source_sheet,
        instrument_kind=instrument_kind,
    )

    await session.commit()

    return {
        "processed": result["processed"],
        "deactivated": result["deactivated"],
        "instrument_kind": instrument_kind or source_sheet,
        "source_file": db_file.filename or "registry.xlsx",
    }
