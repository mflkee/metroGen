from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db
from app.db.repositories import RegistryRepository
from app.schemas.registry import RegistryEntryListRead, RegistryEntryRead
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


@router.get("/entries", response_model=RegistryEntryListRead)
async def list_registry_entries(
    _: CurrentUser,
    *,
    search: str | None = Query(
        None,
        min_length=1,
        description="Свободный поиск по серийнику, документу или источнику",
    ),
    instrument_kind: str | None = Query(None, description="Фильтр по типу прибора"),
    active_only: bool = Query(True, description="Показывать только активные записи"),
    limit: int = Query(300, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
) -> RegistryEntryListRead:
    total, entries = await RegistryRepository(session).list_entries(
        search=search,
        instrument_kind=instrument_kind,
        active_only=active_only,
        limit=limit,
    )
    return RegistryEntryListRead(
        total=total,
        items=[
            RegistryEntryRead(
                id=entry.id,
                source_file=entry.source_file,
                source_sheet=entry.source_sheet,
                instrument_kind=entry.instrument_kind,
                row_index=entry.row_index,
                normalized_serial=entry.normalized_serial,
                document_no=entry.document_no,
                protocol_no=entry.protocol_no,
                owner_name_raw=entry.owner_name_raw,
                methodology_raw=entry.methodology_raw,
                verification_date=entry.verification_date,
                valid_to=entry.valid_to,
                is_active=entry.is_active,
                loaded_at=entry.loaded_at,
            )
            for entry in entries
        ],
    )
