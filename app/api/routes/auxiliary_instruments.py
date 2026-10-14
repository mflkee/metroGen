from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.repositories import AuxiliaryInstrumentRepository
from app.schemas.auxiliary_instrument import (
    AuxiliaryInstrumentBulkResult,
    AuxiliaryInstrumentBulkUpsert,
    AuxiliaryInstrumentCreate,
    AuxiliaryInstrumentOut,
    AuxiliaryInstrumentUpdate,
)
from app.utils.normalization import normalize_serial

router = APIRouter(prefix="/api/v1/auxiliary-instruments", tags=["auxiliary-instruments"])


@router.post(
    "",
    response_model=AuxiliaryInstrumentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update auxiliary verification instrument",
)
async def create_auxiliary_instrument(
    payload: AuxiliaryInstrumentCreate,
    session: AsyncSession = Depends(get_db),
) -> AuxiliaryInstrumentOut:
    repo = AuxiliaryInstrumentRepository(session)
    instrument = await repo.upsert_instrument(
        reg_number=payload.reg_number,
        manufacture_num=payload.manufacture_num,
        values={
            "title": payload.title,
            "modification": payload.modification,
            "certificate_no": payload.certificate_no,
            "verification_date": payload.verification_date,
            "valid_to": payload.valid_to,
        },
    )
    await session.commit()
    await session.refresh(instrument)
    return AuxiliaryInstrumentOut.from_model(instrument)


@router.get(
    "",
    response_model=list[AuxiliaryInstrumentOut],
    summary="List auxiliary verification instruments",
)
async def list_auxiliary_instruments(
    session: AsyncSession = Depends(get_db),
) -> list[AuxiliaryInstrumentOut]:
    repo = AuxiliaryInstrumentRepository(session)
    rows = await repo.list_all()
    return [AuxiliaryInstrumentOut.from_model(row) for row in rows]


@router.post(
    "/bulk",
    response_model=AuxiliaryInstrumentBulkResult,
    summary="Bulk upsert auxiliary instruments with optional full replace",
)
async def bulk_upsert_auxiliary_instruments(
    payload: AuxiliaryInstrumentBulkUpsert,
    session: AsyncSession = Depends(get_db),
) -> AuxiliaryInstrumentBulkResult:
    repo = AuxiliaryInstrumentRepository(session)

    items = [
        {
            "reg_number": item.reg_number,
            "manufacture_num": item.manufacture_num,
            "title": item.title,
            "modification": item.modification,
            "certificate_no": item.certificate_no,
            "verification_date": item.verification_date,
            "valid_to": item.valid_to,
        }
        for item in payload.items
    ]

    updated, created = await repo.bulk_upsert_instruments(items)

    pairs = [(item.reg_number, item.manufacture_num) for item in payload.items]
    deleted = 0
    if payload.replace_all:
        deleted = await repo.prune_to_pairs(pairs)

    await session.commit()
    return AuxiliaryInstrumentBulkResult(upserted=updated + created, deleted=deleted)


@router.patch(
    "/{instrument_id}",
    response_model=AuxiliaryInstrumentOut,
    summary="Update an auxiliary verification instrument",
)
async def update_auxiliary_instrument(
    instrument_id: int,
    payload: AuxiliaryInstrumentUpdate,
    session: AsyncSession = Depends(get_db),
) -> AuxiliaryInstrumentOut:
    repo = AuxiliaryInstrumentRepository(session)
    instrument = await repo.get_by_id(instrument_id)
    if instrument is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="instrument not found")

    data = payload.model_dump(exclude_unset=True)
    if data.get("reg_number"):
        instrument.reg_number = data.pop("reg_number")
    if data.get("manufacture_num"):
        instrument.manufacture_num = data.pop("manufacture_num")
        instrument.normalized_serial = normalize_serial(instrument.manufacture_num)
    for key, value in data.items():
        setattr(instrument, key, value)

    await session.commit()
    await session.refresh(instrument)
    return AuxiliaryInstrumentOut.from_model(instrument)


@router.delete(
    "/{instrument_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an auxiliary verification instrument",
)
async def delete_auxiliary_instrument(
    instrument_id: int,
    session: AsyncSession = Depends(get_db),
) -> Response:
    repo = AuxiliaryInstrumentRepository(session)
    instrument = await repo.get_by_id(instrument_id)
    if instrument is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="instrument not found")

    await repo.delete(instrument)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
