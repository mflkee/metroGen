from __future__ import annotations

import asyncio
from typing import Any, Iterable, Mapping
import re

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse, FileResponse

from app.api.deps import get_db, get_http_client, get_semaphore
from app.schemas.protocol import ProtocolContextItem, ProtocolContextListOut
from app.services.arshin_client import ARSHIN_BASE, find_etalon_certificate
from app.services.html_renderer import render_protocol_html
from app.services.pdf import html_to_pdf_bytes
from app.services.protocol_builder import (
    build_protocol_context,
    suggest_filename,
    make_protocol_number,
)
from app.services.registry_ingest import ingest_registry_rows
from app.utils.excel import (
    extract_certificate_number,
    read_rows_as_dicts,
    read_rows_with_required_headers,
)
from app.utils.normalization import normalize_serial
from app.db.repositories import RegistryRepository
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


def _controller_filename(ctx: dict[str, Any]) -> str:
    ver_date = str(ctx.get("verification_date") or "").strip()
    serial = str(
        ctx.get("manufactureNum")
        or ctx.get("Заводской номер")
        or ctx.get("manufacture_num")
        or ""
    ).strip()
    mpi = ctx.get("mpi_years")

    parts: list[str] = []
    if ver_date:
        parts.append(ver_date)
    if serial:
        parts.append(f"№ {serial}")
    if mpi:
        parts.append(f"(МПИ-{mpi})")

    name = " ".join(parts).strip() or "protocol"
    safe_name = re.sub(r"[\\/:]+", "-", name)
    safe_name = re.sub(r"\s+", " ", safe_name).strip()
    return safe_name


SERIAL_SOURCE_KEYS: tuple[str, ...] = (
    "Заводской номер",
    "Заводской №",
    "Заводской №/ Буквенно-цифровое обозначение",
    "Заводской №/Буквенно-цифровое обозначение",
    "Заводской № / Буквенно-цифровое обозначение",
    "Серийный номер",
)

DB_SERIAL_KEYS: tuple[str, ...] = (
    "Заводской №/ Буквенно-цифровое обозначение",
    "Заводской номер",
    "Заводской №",
    "Серийный номер",
)


def _extract_first_value(row: Mapping[str, Any], keys: Iterable[str]) -> str:
    if not isinstance(row, Mapping):
        row = dict(row)

    pairs = [
        (str(key), row[key])
        for key in row.keys()
        if isinstance(key, str)
    ]

    for candidate in keys:
        norm = candidate.strip().lower()
        for raw_key, value in pairs:
            if value is None:
                continue
            if raw_key.strip().lower() != norm:
                continue
            text = str(value).strip()
            if text:
                return text
    return ""


async def _build_context_from_db(
    row: Mapping[str, Any],
    *,
    db_index: Mapping[str, Mapping[str, Any]] | None = None,
    db_row: Mapping[str, Any] | None = None,
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    session: AsyncSession,
    strict_certificate_match: bool = False,
) -> ProtocolContextItem:
    row_data = dict(row)
    filename = suggest_filename(row_data)

    serial_value = _extract_first_value(row_data, SERIAL_SOURCE_KEYS)
    serial_key = normalize_serial(serial_value)
    if not serial_key:
        return ProtocolContextItem(
            certificate="",
            vri_id="",
            filename=filename,
            context={},
            raw_details={},
            error="serial number is empty",
        )

    if db_row is None and db_index is not None:
        db_row = db_index.get(serial_key)
    if not db_row:
        return ProtocolContextItem(
            certificate="",
            vri_id="",
            filename=filename,
            context={},
            raw_details={},
            error="serial number not found in db",
        )

    cert = str(db_row.get("Документ") or "").strip()
    if not cert:
        return ProtocolContextItem(
            certificate="",
            vri_id="",
            filename=filename,
            context={},
            raw_details={},
            error="certificate number missing in db",
        )

    protocol_number = str(db_row.get("номер_протокола") or "").strip()

    excel_cert = extract_certificate_number(row_data)
    if (
        strict_certificate_match
        and excel_cert
        and excel_cert.strip()
        and excel_cert.strip() != cert
    ):
        return ProtocolContextItem(
            certificate=excel_cert,
            vri_id="",
            filename=filename,
            context={},
            raw_details={},
            error="certificate mismatch between excel and db",
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
            row_data["_resolved_etalon_cert"] = et_cert

        ctx = await build_protocol_context(row_data, details, client, session=session)
        if protocol_number:
            ctx["protocol_number"] = protocol_number

        fname = suggest_filename(ctx) or filename

        return ProtocolContextItem(
            certificate=cert,
            vri_id=vri_id,
            filename=fname,
            context=ctx,
            raw_details=details,
            error=None,
        )
    except Exception as exc:
        return ProtocolContextItem(
            certificate=cert,
            vri_id="",
            filename=filename,
            context={},
            raw_details={},
            error=str(exc),
        )


def _unique_output_path(directory: Path, base_name: str) -> Path:
    candidate = directory / base_name
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 1
    while True:
        alternative = directory / f"{stem}({counter}){suffix}"
        if not alternative.exists():
            return alternative
        counter += 1

@router.post("/context-by-excel", response_model=ProtocolContextListOut)
async def contexts_by_excel(
    file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
    session: AsyncSession = Depends(get_db),
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
        cert = extract_certificate_number(row)
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
            ctx = await build_protocol_context(row, details, client, session=session)

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



@router.post("/html-by-excel", response_class=HTMLResponse)
async def html_by_excel(
    file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
    session: AsyncSession = Depends(get_db),
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
    cert = extract_certificate_number(row)
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
    ctx = await build_protocol_context(row, details, client, session=session)

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
    out_path = _unique_output_path(out_dir, base_name)
    out_path.write_text(html, encoding="utf-8")

    return HTMLResponse(content=html, media_type="text/html")


@router.post("/controllers/pdf-files")
async def controllers_pdf_files(
    controllers_file: UploadFile = File(...),
    db_file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
    session: AsyncSession = Depends(get_db),
):
    controllers_data = await controllers_file.read()
    db_data = await db_file.read()

    if not controllers_data:
        raise HTTPException(status_code=400, detail="empty controllers file")
    if not db_data:
        raise HTTPException(status_code=400, detail="empty db file")

    rows = read_rows_as_dicts(controllers_data)
    if not rows:
        return {"files": [], "count": 0}

    db_rows = read_rows_with_required_headers(
        db_data,
        header_row=5,
        data_start_row=6,
        required_headers=DB_SERIAL_KEYS,
    )
    if not db_rows:
        raise HTTPException(status_code=400, detail="db file has no serial entries")

    await ingest_registry_rows(
        session,
        source_file=db_file.filename or "registry.xlsx",
        rows=db_rows,
        source_sheet="controllers",
    )

    registry_repo = RegistryRepository(session)

    async def process_row(row: dict[str, Any]) -> ProtocolContextItem:
        serial = _extract_first_value(row, SERIAL_SOURCE_KEYS)
        normalized_serial = normalize_serial(serial)
        db_row: Mapping[str, Any] | None = None

        if normalized_serial:
            entries = await registry_repo.find_active_by_serial(normalized_serial)
            if entries:
                entry = entries[0]
                payload = dict(entry.payload or {})
                if entry.document_no and not payload.get("Документ"):
                    payload["Документ"] = entry.document_no
                if entry.protocol_no and not payload.get("номер_протокола"):
                    payload["номер_протокола"] = entry.protocol_no
                db_row = payload

        return await _build_context_from_db(
            row,
            db_row=db_row,
            client=client,
            sem=sem,
            session=session,
            strict_certificate_match=False,
        )

    items: list[ProtocolContextItem] = await asyncio.gather(*(process_row(r) for r in rows))

    exports_dir: Path | None = None
    pdf_unavailable = False
    saved: list[str] = []
    errors: list[dict[str, object]] = []

    for idx, (it, src_row) in enumerate(zip(items, rows), start=1):
        ctx = it.context or {}
        serial = _extract_first_value(src_row, SERIAL_SOURCE_KEYS)

        if it.error or not ctx:
            errors.append(
                {
                    "row": idx,
                    "serial": serial,
                    "certificate": it.certificate,
                    "reason": it.error or "empty context",
                }
            )
            continue

        if not ctx.get("protocol_number"):
            ctx["protocol_number"] = make_protocol_number(
                ctx.get("verifier_name"),
                ctx.get("verification_date"),
                len(saved) + 1,
            )

        html = render_protocol_html(ctx)
        pdf_bytes = await html_to_pdf_bytes(html)
        if not pdf_bytes:
            pdf_unavailable = True
            errors.append(
                {
                    "row": idx,
                    "serial": serial,
                    "certificate": it.certificate,
                    "reason": "pdf generation unavailable",
                }
            )
            continue

        if exports_dir is None:
            exports_dir = get_dated_exports_dir(date.today())

        base_name = _controller_filename(ctx)
        if not base_name.lower().endswith(".pdf"):
            base_name = f"{base_name}.pdf"
        path = _unique_output_path(exports_dir, base_name)
        path.write_bytes(pdf_bytes)
        saved.append(str(path))

    if not saved and pdf_unavailable:
        raise HTTPException(status_code=500, detail="PDF generation is unavailable (Playwright not installed)")

    return {"files": saved, "count": len(saved), "errors": errors}


@router.post("/manometers/pdf-files")
async def manometers_pdf_files(
    manometers_file: UploadFile = File(...),
    db_file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
    session: AsyncSession = Depends(get_db),
):
    manometers_data = await manometers_file.read()
    db_data = await db_file.read()

    if not manometers_data:
        raise HTTPException(status_code=400, detail="empty manometers file")
    if not db_data:
        raise HTTPException(status_code=400, detail="empty db file")

    rows = read_rows_as_dicts(manometers_data)
    if not rows:
        return {"files": [], "count": 0, "errors": []}

    db_rows = read_rows_with_required_headers(
        db_data,
        header_row=5,
        data_start_row=6,
        required_headers=DB_SERIAL_KEYS,
    )
    if not db_rows:
        raise HTTPException(status_code=400, detail="db file has no serial entries")

    await ingest_registry_rows(
        session,
        source_file=db_file.filename or "registry.xlsx",
        rows=db_rows,
        source_sheet="manometers",
    )

    registry_repo = RegistryRepository(session)

    async def process_row(row: dict[str, Any]) -> ProtocolContextItem:
        serial = _extract_first_value(row, SERIAL_SOURCE_KEYS)
        normalized_serial = normalize_serial(serial)
        db_row: Mapping[str, Any] | None = None

        if normalized_serial:
            entries = await registry_repo.find_active_by_serial(normalized_serial)
            if entries:
                entry = entries[0]
                payload = dict(entry.payload or {})
                if entry.document_no and not payload.get("Документ"):
                    payload["Документ"] = entry.document_no
                if entry.protocol_no and not payload.get("номер_протокола"):
                    payload["номер_протокола"] = entry.protocol_no
                db_row = payload

        return await _build_context_from_db(
            row,
            db_row=db_row,
            client=client,
            sem=sem,
            session=session,
            strict_certificate_match=True,
        )

    items: list[ProtocolContextItem] = await asyncio.gather(*(process_row(r) for r in rows))

    exports_dir: Path | None = None
    pdf_unavailable = False
    saved: list[str] = []
    errors: list[dict[str, object]] = []

    for idx, (it, src_row) in enumerate(zip(items, rows), start=1):
        ctx = it.context or {}
        serial = _extract_first_value(src_row, SERIAL_SOURCE_KEYS)

        if it.error or not ctx:
            errors.append(
                {
                    "row": idx,
                    "serial": serial,
                    "certificate": it.certificate,
                    "reason": it.error or "empty context",
                }
            )
            continue

        if not ctx.get("protocol_number"):
            ctx["protocol_number"] = make_protocol_number(
                ctx.get("verifier_name"),
                ctx.get("verification_date"),
                len(saved) + 1,
            )

        html = render_protocol_html(ctx)
        pdf_bytes = await html_to_pdf_bytes(html)
        if not pdf_bytes:
            pdf_unavailable = True
            errors.append(
                {
                    "row": idx,
                    "serial": serial,
                    "certificate": it.certificate,
                    "reason": "pdf generation unavailable",
                }
            )
            continue

        if exports_dir is None:
            exports_dir = get_dated_exports_dir(date.today())

        base_name = _filename_from_protocol_number(ctx.get("protocol_number") or "", ".pdf")
        path = _unique_output_path(exports_dir, base_name)
        path.write_bytes(pdf_bytes)
        saved.append(str(path))

    if not saved and pdf_unavailable:
        raise HTTPException(status_code=500, detail="PDF generation is unavailable (Playwright not installed)")

    return {"files": saved, "count": len(saved), "errors": errors}



