from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.repositories import EtalonRepository
from app.schemas.etalon import (
    EtalonCertificationIn,
    EtalonCertificationOut,
    EtalonOut,
    EtalonUpdate,
    EtalonUpsert,
)

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


@router.patch(
    "/{etalon_id}",
    response_model=EtalonOut,
    summary="Update an etalon device",
)
async def update_etalon(
    etalon_id: int,
    payload: EtalonUpdate,
    session: AsyncSession = Depends(get_db),
) -> EtalonOut:
    repo = EtalonRepository(session)
    device = await repo.get_device_by_id(etalon_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="etalon not found")

    data = payload.model_dump(
        exclude_unset=True,
        exclude={"certificate_no", "verification_date", "valid_to"},
    )
    for key, value in data.items():
        setattr(device, key, value)

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


@router.delete(
    "/{etalon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an etalon device together with its certificates",
)
async def delete_etalon(etalon_id: int, session: AsyncSession = Depends(get_db)) -> Response:
    repo = EtalonRepository(session)
    device = await repo.get_device_by_id(etalon_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="etalon not found")

    await repo.delete(device)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{etalon_id}/certifications",
    response_model=list[EtalonCertificationOut],
    summary="List an etalon's certificates",
)
async def list_etalon_certifications(
    etalon_id: int,
    session: AsyncSession = Depends(get_db),
) -> list[EtalonCertificationOut]:
    repo = EtalonRepository(session)
    device = await repo.get_device_by_id(etalon_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="etalon not found")
    rows = await repo.list_certifications(etalon_id)
    return [EtalonCertificationOut.from_model(row) for row in rows]


@router.post(
    "/{etalon_id}/certifications",
    response_model=EtalonCertificationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add or update an etalon certificate",
)
async def add_etalon_certification(
    etalon_id: int,
    payload: EtalonCertificationIn,
    session: AsyncSession = Depends(get_db),
) -> EtalonCertificationOut:
    repo = EtalonRepository(session)
    device = await repo.get_device_by_id(etalon_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="etalon not found")

    certificate = await repo.upsert_certification(
        device=device,
        certificate_no=payload.certificate_no,
        values={
            "verification_date": payload.verification_date,
            "valid_to": payload.valid_to,
            "source": payload.source or "manual",
        },
    )
    await session.commit()
    await session.refresh(certificate)
    return EtalonCertificationOut.from_model(certificate)


@router.delete(
    "/{etalon_id}/certifications/{certification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an etalon certificate",
)
async def delete_etalon_certification(
    etalon_id: int,
    certification_id: int,
    session: AsyncSession = Depends(get_db),
) -> Response:
    repo = EtalonRepository(session)
    certificate = await repo.get_certification(etalon_id, certification_id)
    if certificate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="certificate not found")

    await repo.delete(certificate)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
