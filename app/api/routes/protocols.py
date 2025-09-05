from __future__ import annotations

import asyncio
from typing import Any

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import get_http_client, get_semaphore
from app.schemas.protocol import ProtocolContextItem, ProtocolContextListOut
from app.services.arshin_client import ARSHIN_BASE, find_etalon_certificate
from app.services.protocol_builder import build_protocol_context, suggest_filename
from app.utils.excel import read_rows_as_dicts

router = APIRouter(prefix="/api/v1/protocols", tags=["protocols"])


@router.post("/context-by-excel", response_model=ProtocolContextListOut)
async def contexts_by_excel(
    file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
) -> ProtocolContextListOut:
    """Строит контексты протоколов на основе Excel.

    На входе Excel с шапкой; на выходе список элементов:
      - certificate, vri_id, filename
      - context (всё для шаблонов/генерации)
      - raw_details (сырой ответ /vri/{id})
    """
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")

    # 1) читаем строки как список словарей (ключи — из первой строки)
    rows = read_rows_as_dicts(data)
    if not rows:
        return ProtocolContextListOut(items=[])

    async def process_row(row: dict[str, Any]) -> ProtocolContextItem:
        cert = (row.get("Номер свидетельтсва") or "").strip()
        filename = suggest_filename(row)

        if not cert:
            return ProtocolContextItem(
                certificate="",
                vri_id="",
                filename=filename,
                context={},
                raw_details={},
                error="certificate number is empty",
            )

        try:
            # 2) найти VRI по номеру свидетельства (ограничиваем параллельность)
            async with sem:
                search_resp = await client.get(f"{ARSHIN_BASE}/vri", params={"result_docnum": cert})
            search_resp.raise_for_status()
            found = (search_resp.json().get("result") or {}).get("items") or []
            if not found:
                return ProtocolContextItem(
                    certificate=cert,
                    vri_id="",
                    filename=filename,
                    context={},
                    raw_details={},
                    error="not found",
                )

            vri_id = found[0]["vri_id"]

            # 3) детали по VRI (ограничиваем параллельность)
            async with sem:
                details_resp = await client.get(f"{ARSHIN_BASE}/vri/{vri_id}")
            details_resp.raise_for_status()
            details = details_resp.json().get("result") or {}

            # 4) авто-поиск свидетельства эталона с учётом семафора
            et_cert = await find_etalon_certificate(client, details, sem=sem)
            if et_cert:
                row["_resolved_etalon_cert"] = et_cert  # билдер это подхватит

            # 5) собрать контекст
            ctx = await build_protocol_context(row, details, client)

            # 6) имя файла — по контексту или по исходной строке
            fname = suggest_filename(ctx) or filename

            return ProtocolContextItem(
                certificate=cert,
                vri_id=vri_id,
                filename=fname,
                context=ctx,
                raw_details=details,
                error=None,
            )
        except Exception as e:
            return ProtocolContextItem(
                certificate=cert,
                vri_id="",
                filename=filename,
                context={},
                raw_details={},
                error=str(e),
            )

    # Параллельная обработка строк Excel с общим семафором
    items: list[ProtocolContextItem] = await asyncio.gather(*(process_row(r) for r in rows))

    return ProtocolContextListOut(items=items)
