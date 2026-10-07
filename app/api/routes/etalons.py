from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.repositories import EtalonRepository
from app.schemas.etalon import EtalonOut, EtalonUpsert

router = APIRouter(prefix="/api/v1/etalons", tags=["etalons"])


@router.get(
    "",
    response_model=list[EtalonOut],
    summary="List etalon devices with their latest certificate",
)
async def list_etalons(session: AsyncSession = Depends(get_db)) -> list[EtalonOut]:
    repo = EtalonRepository(session)
    devices = await repo.list_devices()
    result: list[EtalonOut] = []
    for device in devices:
        certificate = await repo.latest_certification(device.id)
        result.append(EtalonOut.from_model(device, certificate))
    return result


@router.post(
    "",
    response_model=EtalonOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update an etalon device (key = FGIS number)",
)
async def upsert_etalon(
    payload: EtalonUpsert,
    session: AsyncSession = Depends(get_db),
) -> EtalonOut:
    repo = EtalonRepository(session)
    device = await repo.upsert_device_by_code(
        code=payload.reg_number,
        manufacture_num=payload.manufacture_num,
        values={
            "mitype_number": payload.mitype_number,
            "title": payload.title,
            "notation": payload.notation,
            "modification": payload.modification,
            "manufacture_year": payload.manufacture_year,
            "rank_code": payload.rank_code,
            "rank_title": payload.rank_title,
            "schema_title": payload.schema_title,
        },
    )

    certificate = None
    if payload.certificate_no:
        certificate = await repo.upsert_certification(
            device=device,
            certificate_no=payload.certificate_no,
            values={
                "verification_date": payload.verification_date,
                "valid_to": payload.valid_to,
                "source": "manual",
            },
        )

    await session.commit()
    if certificate is None:
        certificate = await repo.latest_certification(device.id)
    return EtalonOut.from_model(device, certificate)
