from __future__ import annotations
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
import httpx

from app.schemas.arshin import VriIdOut, VriIdListOut, VriDetailOut, VriDetailListOut
from app.services.arshin_client import(
    fetch_vri_id_by_certificate, guess_year_from_cert,
    fetch_vri_details, compose_etalon_line_from_details, extract_detail_fields
)
from app.utils.excel import read_column_as_list
from app.api.deps import get_http_client, get_semaphore

router = APIRouter(prefix="/api/v1/resolve", tags=["resolve"])

# 1) ОДИН номер -> vri_id
@router.get("/vri-id", response_model=VriIdOut)
async def resolve_single_vri_id(
    cert: str = Query(..., description="Номер свидетельства, как в Аршине"),
    year: int | None = Query(None, description="Необязательно. Если не указан — попытаемся угадать из номера."),
    client: httpx.AsyncClient = Depends(get_http_client),
):
    try:
        year_used = year or guess_year_from_cert(cert)
        data = await fetch_vri_id_by_certificate(client, cert, year_used)
        return VriIdOut(certificate=cert, vri_id=data["vri_id"], year_used=year_used)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Аршин вернул ошибку {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2) Excel (колонка P со 2 строки) -> список vri_id
@router.post("/vri-ids-by-excel", response_model=VriIdListOut)
async def resolve_vri_ids_by_excel(
    file: UploadFile = File(..., description="Excel-файл. Берём колонку P, начиная со строки 2."),
    column_letter: str = "P",
    start_row: int = 2,
    year: int | None = Query(None, description="Опционально: принудительный год для всех запросов."),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem = Depends(get_semaphore),
):
    content = await file.read()
    await file.close()
    certs = read_column_as_list(content, column_letter=column_letter, start_row=start_row)
    if not certs:
        raise HTTPException(status_code=400, detail="В Excel не найдено номеров свидетельств в указанной колонке.")

    async def worker(c: str):
        y = year or guess_year_from_cert(c)
        async with sem:
            try:
                data = await fetch_vri_id_by_certificate(client, c, y)
                return VriIdOut(certificate=c, vri_id=data["vri_id"], year_used=y)
            except Exception as e:
                return VriIdOut(certificate=c, vri_id=None, year_used=y, error=str(e))

    items = await asyncio.gather(*[worker(c) for c in certs])
    return VriIdListOut(items=items)

# 3) Детали по одному vri_id
@router.get("/vri/{vri_id}", response_model=VriDetailOut)
async def details_by_vri_id(
    vri_id: str,
    client: httpx.AsyncClient = Depends(get_http_client),
):
    try:
        data = await fetch_vri_details(client, vri_id)
        fields = extract_detail_fields(data)
        etalon_line = compose_etalon_line_from_details(data)
        return VriDetailOut(vri_id=vri_id, etalon_line=etalon_line, raw=data, **fields)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Аршин вернул ошибку {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4) Excel -> vri_id -> детали (всё сразу списком)
@router.post("/vri-details-by-excel", response_model=VriDetailListOut)
async def details_by_excel(
    file: UploadFile = File(..., description="Excel-файл. Колонка P, начиная со строки 2."),
    column_letter: str = "P",
    start_row: int = 2,
    year: int | None = Query(None, description="Опциональный фиксированный год для всех запросов."),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem = Depends(get_semaphore),
):
    content = await file.read()
    await file.close()
    certs = read_column_as_list(content, column_letter=column_letter, start_row=start_row)
    if not certs:
        raise HTTPException(status_code=400, detail="В Excel не найдено номеров свидетельств в указанной колонке.")

    async def worker(cert: str) -> VriDetailOut:
        y = year or guess_year_from_cert(cert)
        async with sem:
            try:
                # 1) резолвим vri_id
                id_data = await fetch_vri_id_by_certificate(client, cert, y)
                vri_id = id_data.get("vri_id")
            except Exception as e:
                return VriDetailOut(certificate=cert, vri_id=None, error=f"resolve error: {e}")

        if not vri_id:
            return VriDetailOut(certificate=cert, vri_id=None, error="vri_id not found")

        async with sem:
            try:
                # 2) тянем детали
                det = await fetch_vri_details(client, vri_id)
                fields = extract_detail_fields(det)
                etalon_line = compose_etalon_line_from_details(det)
                return VriDetailOut(certificate=cert, vri_id=vri_id, etalon_line=etalon_line, raw=det, **fields)
            except Exception as e:
                return VriDetailOut(certificate=cert, vri_id=vri_id, error=f"details error: {e}")

    items = await asyncio.gather(*[worker(c) for c in certs])
    return VriDetailListOut(items=items)

