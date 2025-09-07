from __future__ import annotations

import asyncio
from typing import Any

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette.responses import HTMLResponse, FileResponse

from app.api.deps import get_http_client, get_semaphore
from app.schemas.protocol import ProtocolContextItem, ProtocolContextListOut
from app.services.arshin_client import ARSHIN_BASE, find_etalon_certificate
from app.services.html_renderer import render_protocol_html
from app.services.pdf import html_to_pdf_bytes
from app.services.protocol_builder import (
    build_protocol_context,
    suggest_filename,
    make_protocol_number,
)
from app.utils.excel import read_rows_as_dicts
from app.utils.paths import get_dated_exports_dir, get_output_dir
from pathlib import Path
from datetime import date

router = APIRouter(prefix="/api/v1/protocols", tags=["protocols"]) 


def _filename_from_protocol_number(pn: str, ext: str = ".pdf") -> str:
    """Make a filesystem-safe filename from a protocol number.

    Example: "БСН/150125/1" -> "БСН-150125-1.pdf"
    """
    name = (pn or "protocol").strip()
    # replace separators unsafe for filesystems
    for ch in ("/", "\\"):
        name = name.replace(ch, "-")
    # collapse spaces
    name = "-".join(part for part in name.split())
    if not name.lower().endswith(ext):
        name = f"{name}{ext}"
    return name

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

    # Проставим номера протоколов последовательно по файлу: 1, 2, 3, ...
    for idx, it in enumerate(items, start=1):
        ctx = it.context or {}
        if ctx:
            pn = make_protocol_number(
                ctx.get("verifier_name"),
                ctx.get("verification_date"),
                idx,
            )
            ctx["protocol_number"] = pn
            it.context = ctx

    return ProtocolContextListOut(items=items)


@router.post("/html-files-by-excel")
async def html_files_by_excel(
    file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
):
    """Генерирует и сохраняет HTML-файлы протоколов для всех строк Excel.

    - Сохраняет в каталоге `output/` в корне проекта.
    - Имя файла берётся из suggest_filename(...).html с автодобавлением суффикса при коллизии.
    - Номера протоколов формируются последовательно по файлу: ИНИ/ДДММГГГГ/N.
    - Возвращает JSON с перечнем сохранённых файлов.
    """
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")

    rows = read_rows_as_dicts(data)
    if not rows:
        return {"files": [], "count": 0}

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
            async with sem:
                details_resp = await client.get(f"{ARSHIN_BASE}/vri/{vri_id}")
            details_resp.raise_for_status()
            details = details_resp.json().get("result") or {}

            et_cert = await find_etalon_certificate(client, details, sem=sem)
            if et_cert:
                row["_resolved_etalon_cert"] = et_cert

            ctx = await build_protocol_context(row, details, client)
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

    items: list[ProtocolContextItem] = await asyncio.gather(*(process_row(r) for r in rows))

    out_dir = get_output_dir()
    saved: list[str] = []
    for idx, it in enumerate(items, start=1):
        ctx = it.context or {}
        if it.error or not ctx:
            continue
        # Номер протокола последовательный по файлу
        pn = make_protocol_number(ctx.get("verifier_name"), ctx.get("verification_date"), idx)
        ctx["protocol_number"] = pn
        # Рендер и сохранение
        html = render_protocol_html(ctx)
        base_name = it.filename or suggest_filename(ctx) or suggest_filename({}) or "protocol"
        if not base_name.lower().endswith(".html"):
            base_name = f"{base_name}.html"
        path = out_dir / base_name
        if path.exists():
            stem = path.stem
            i = 1
            while True:
                candidate = out_dir / f"{stem}({i}).html"
                if not candidate.exists():
                    path = candidate
                    break
                i += 1
        path.write_text(html, encoding="utf-8")
        saved.append(str(path))

    return {"files": saved, "count": len(saved)}
@router.post("/html-by-excel", response_class=HTMLResponse)
async def html_by_excel(
    file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
) -> HTMLResponse:
    """Возвращает HTML-протокол по первой строке Excel.

    Принимает тот же формат Excel, что и /context-by-excel.
    """
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")

    rows = read_rows_as_dicts(data)
    if not rows:
        raise HTTPException(status_code=400, detail="no rows")

    row = rows[0]
    cert = (row.get("Номер свидетельтсва") or "").strip()
    if not cert:
        raise HTTPException(status_code=400, detail="certificate number is empty")

    # 1) найти VRI по номеру свидетельства
    async with sem:
        search_resp = await client.get(f"{ARSHIN_BASE}/vri", params={"result_docnum": cert})
    search_resp.raise_for_status()
    found = (search_resp.json().get("result") or {}).get("items") or []
    if not found:
        raise HTTPException(status_code=404, detail="not found")

    vri_id = found[0]["vri_id"]

    # 2) детали по VRI
    async with sem:
        details_resp = await client.get(f"{ARSHIN_BASE}/vri/{vri_id}")
    details_resp.raise_for_status()
    details = details_resp.json().get("result") or {}

    # 3) авто-поиск свидетельства эталона
    et_cert = await find_etalon_certificate(client, details, sem=sem)
    if et_cert:
        row["_resolved_etalon_cert"] = et_cert

    # 4) собрать контекст
    ctx = await build_protocol_context(row, details, client)

    # Номер протокола: ИНИ/ДДММГГГГ/N (для одиночного запроса N=1)
    proto_num = make_protocol_number(
        ctx.get("verifier_name"),
        ctx.get("verification_date"),
        1,
    )
    ctx["protocol_number"] = proto_num

    # Рендерим HTML
    html = render_protocol_html(ctx)

    # Сохраняем файл в output/<filename>.html
    out_dir = get_output_dir()
    base_name = suggest_filename(ctx) or suggest_filename(row) or "protocol"
    if not base_name.lower().endswith(".html"):
        base_name = f"{base_name}.html"
    out_path = out_dir / base_name
    # если имя занято — добавим суффикс
    if out_path.exists():
        stem = out_path.stem
        i = 1
        while True:
            candidate = out_dir / f"{stem}({i}).html"
            if not candidate.exists():
                out_path = candidate
                break
            i += 1
    out_path.write_text(html, encoding="utf-8")

    return HTMLResponse(content=html, media_type="text/html")


@router.post("/pdf-by-excel")
async def pdf_by_excel(
    file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
):
    """Генерирует PDF-протокол (A4 книжный), сохраняет на диск и отдаёт файл.

    - Принимает Excel как /html-by-excel; берёт первую строку.
    - Сохраняет в каталоге `exports/YYYY-MM-DD/`.
    - Имя файла берётся из контекста (suggest_filename) с расширением .pdf.
    """
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")

    rows = read_rows_as_dicts(data)
    if not rows:
        raise HTTPException(status_code=400, detail="no rows")

    row = rows[0]
    cert = (row.get("Номер свидетельтсва") or "").strip()
    if not cert:
        raise HTTPException(status_code=400, detail="certificate number is empty")

    # 1) найти VRI по номеру свидетельства
    async with sem:
        search_resp = await client.get(f"{ARSHIN_BASE}/vri", params={"result_docnum": cert})
    search_resp.raise_for_status()
    found = (search_resp.json().get("result") or {}).get("items") or []
    if not found:
        raise HTTPException(status_code=404, detail="not found")

    vri_id = found[0]["vri_id"]

    # 2) детали по VRI
    async with sem:
        details_resp = await client.get(f"{ARSHIN_BASE}/vri/{vri_id}")
    details_resp.raise_for_status()
    details = details_resp.json().get("result") or {}

    # 3) авто-поиск свидетельства эталона
    et_cert = await find_etalon_certificate(client, details, sem=sem)
    if et_cert:
        row["_resolved_etalon_cert"] = et_cert

    # 4) собрать контекст, присвоить номер и рендер HTML
    ctx = await build_protocol_context(row, details, client)
    proto_num = make_protocol_number(
        ctx.get("verifier_name"),
        ctx.get("verification_date"),
        1,
    )
    ctx["protocol_number"] = proto_num
    html = render_protocol_html(ctx)

    # 5) HTML -> PDF (A4 книжный)
    pdf_bytes = await html_to_pdf_bytes(html)
    if not pdf_bytes:
        raise HTTPException(status_code=500, detail="PDF generation is unavailable (Playwright not installed)")

    # 6) Сохранение на диск в exports/YYYY-MM-DD/
    exports_dir = get_dated_exports_dir(date.today())
    base_name = _filename_from_protocol_number(ctx.get("protocol_number") or "")
    file_path = exports_dir / base_name
    # если имя занято — добавить суффикс
    suffix = 1
    stem = file_path.stem
    while file_path.exists():
        file_path = exports_dir / f"{stem}({suffix}).pdf"
        suffix += 1

    file_path.write_bytes(pdf_bytes)

    # 7) Отдаём файл как скачивание
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=file_path.name,
    )


@router.post("/pdf-files-by-excel")
async def pdf_files_by_excel(
    file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
):
    """Генерирует PDF-протоколы (A4 книжный) для всех непустых строк Excel.

    - Принимает Excel с тем же форматом, что и /context-by-excel.
    - Для каждой валидной строки строит контекст, присваивает последовательный номер протокола,
      рендерит HTML и конвертирует в PDF.
    - Сохраняет все PDF в каталоге `exports/YYYY-MM-DD/` и возвращает список путей.
    """
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")

    rows = read_rows_as_dicts(data)
    if not rows:
        return {"files": [], "count": 0}

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
            async with sem:
                details_resp = await client.get(f"{ARSHIN_BASE}/vri/{vri_id}")
            details_resp.raise_for_status()
            details = details_resp.json().get("result") or {}

            et_cert = await find_etalon_certificate(client, details, sem=sem)
            if et_cert:
                row["_resolved_etalon_cert"] = et_cert

            ctx = await build_protocol_context(row, details, client)
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

    items: list[ProtocolContextItem] = await asyncio.gather(*(process_row(r) for r in rows))

    # Сохранение всех PDF в dated exports
    exports_dir = get_dated_exports_dir(date.today())
    saved: list[str] = []
    for idx, it in enumerate(items, start=1):
        ctx = it.context or {}
        if it.error or not ctx:
            continue
        # Номер протокола последовательный по файлу
        pn = make_protocol_number(ctx.get("verifier_name"), ctx.get("verification_date"), idx)
        ctx["protocol_number"] = pn
        # Рендер HTML
        html = render_protocol_html(ctx)
        # HTML -> PDF
        pdf_bytes = await html_to_pdf_bytes(html)
        if not pdf_bytes:
            # Если окружение не поддерживает PDF — пропустим и двигаемся дальше
            # (можно также вернуть 500, но для пачки логичнее пропускать)
            continue

        base_name = _filename_from_protocol_number(ctx.get("protocol_number") or "")
        path = exports_dir / base_name
        if path.exists():
            stem = path.stem
            i = 1
            while True:
                candidate = exports_dir / f"{stem}({i}).pdf"
                if not candidate.exists():
                    path = candidate
                    break
                i += 1
        path.write_bytes(pdf_bytes)
        saved.append(str(path))

    return {"files": saved, "count": len(saved)}
