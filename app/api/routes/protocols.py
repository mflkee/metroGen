from __future__ import annotations

import asyncio
import re
from collections.abc import Iterable, Mapping
from datetime import date, datetime
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse

from app.api.deps import get_db, get_http_client, get_semaphore
from app.db.repositories import RegistryRepository
from app.schemas.protocol import ProtocolContextItem, ProtocolContextListOut
from app.services.arshin_client import (
    fetch_vri_details,
    fetch_vri_id_by_certificate,
    find_etalon_certificate,
)
from app.services.html_renderer import render_protocol_html
from app.services.pdf import html_to_pdf_bytes
from app.services.protocol_builder import (
    build_protocol_context,
    make_protocol_number,
    suggest_filename,
)
from app.services.registry_ingest import ingest_registry_rows
from app.utils.excel import (
    extract_certificate_number,
    read_rows_as_dicts,
    read_rows_with_required_headers,
)
from app.utils.normalization import normalize_serial
from app.utils.paths import get_named_exports_dir, get_output_dir, sanitize_filename

router = APIRouter(prefix="/api/v1/protocols", tags=["protocols"])


def _parse_date_value(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    if not text:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _extract_equipment_label_from_sources(
    *sources: Mapping[str, Any] | None,
) -> str:
    for source in sources:
        if not source:
            continue
        if not isinstance(source, Mapping):
            source = dict(source)  # type: ignore[assignment]
        for key in ("Наименование СИ", "Тип СИ", "ТипСИ", "Тип"):
            value = source.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
    return ""


SERIAL_SOURCE_KEYS: tuple[str, ...] = (
    "Заводской номер",
    "Заводской №",
    "Заводской №/ Буквенно-цифровое обозначение",
    "Заводской №/Буквенно-цифровое обозначение",
    "Заводской № / Буквенно-цифровое обозначение",
    "Серийный номер",
)


def _extract_month_from_filename(filename: str | None) -> str | None:
    if not filename:
        return None
    stem = Path(filename).stem

    pattern = re.compile(r"(0[1-9]|1[0-2])")
    for match in pattern.finditer(stem):
        start, end = match.span(1)
        left = stem[start - 1] if start > 0 else ""
        right = stem[end] if end < len(stem) else ""
        if left.isdigit() or right.isdigit():
            continue
        return match.group(1)

    for token in re.findall(r"\d+", stem):
        if len(token) == 2:
            value = int(token)
            if 1 <= value <= 12:
                return f"{value:02d}"
        if len(token) in (6, 8):
            value = int(token[-2:])
            if 1 <= value <= 12:
                return f"{value:02d}"
    return None


DB_SERIAL_KEYS: tuple[str, ...] = (
    "Заводской №/ Буквенно-цифровое обозначение",
    "Заводской номер",
    "Заводской №",
    "Серийный номер",
)


CONTEXT_SERIAL_KEYS: tuple[str, ...] = (
    "manufactureNum",
    "manufacture_num",
    "serial_number",
    "serial",
) + SERIAL_SOURCE_KEYS


def _context_serial(ctx: Mapping[str, Any]) -> str:
    for key in CONTEXT_SERIAL_KEYS:
        value = ctx.get(key) if isinstance(ctx, Mapping) else None
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _context_mpi(ctx: Mapping[str, Any]) -> int | None:
    value = ctx.get("mpi_years") if isinstance(ctx, Mapping) else None
    if value is None:
        return None
    try:
        mpi = int(value)
    except (TypeError, ValueError):
        return None
    return mpi if mpi > 0 else None


def _determine_equipment_label(ctx: Mapping[str, Any], default: str) -> str:
    for key in (
        "equipment_label",
        "Наименование СИ",
        "Тип СИ",
        "ТипСИ",
        "device_info",
        "mitype_title",
    ):
        value = ctx.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


def _extract_month_from_context(ctx: Mapping[str, Any]) -> str:
    protocol_number = str(ctx.get("protocol_number") or "").strip()
    if protocol_number:
        normalized = re.split(r"[\\/-]+", protocol_number)
        for part in normalized:
            digits = "".join(ch for ch in part if ch.isdigit())
            if not digits:
                continue
            month_candidate = int(digits[:2])
            if 1 <= month_candidate <= 12:
                return f"{month_candidate:02d}"
    ver_date = _parse_date_value(ctx.get("verification_date") or ctx.get("Дата поверки"))
    if ver_date:
        return f"{ver_date.month:02d}"
    return f"{date.today().month:02d}"


def _exports_folder_label(
    ctx: Mapping[str, Any],
    default_equipment: str,
    *,
    forced_month: str | None = None,
    use_default_only: bool = False,
) -> str:
    equipment = default_equipment if use_default_only else _determine_equipment_label(
        ctx, default_equipment
    )
    month = forced_month or _extract_month_from_context(ctx)
    return f"PDF {equipment} {month}".strip()


def _context_pdf_filename(ctx: Mapping[str, Any]) -> str:
    ver_date = _parse_date_value(ctx.get("verification_date") or ctx.get("Дата поверки"))
    date_part = ver_date.isoformat() if ver_date else "unknown-date"
    serial = _context_serial(ctx)
    mpi = _context_mpi(ctx)

    parts: list[str] = [date_part]
    if serial:
        parts.append(f"№ {serial}")
    if mpi:
        parts.append(f"(МПИ-{mpi})")

    name = " ".join(parts).strip() or "protocol"
    safe_name = sanitize_filename(name, default="protocol")
    if not safe_name.lower().endswith(".pdf"):
        safe_name = f"{safe_name}.pdf"
    return safe_name


def _entries_to_index(entries: Mapping[str, list[Any]]) -> dict[str, Mapping[str, Any]]:
    index: dict[str, Mapping[str, Any]] = {}
    for serial, records in entries.items():
        if not records:
            continue
        entry = records[0]
        payload = dict(getattr(entry, "payload", {}) or {})
        document_no = getattr(entry, "document_no", None)
        protocol_no = getattr(entry, "protocol_no", None)
        if document_no and not payload.get("Документ"):
            payload["Документ"] = document_no
        if protocol_no and not payload.get("номер_протокола"):
            payload["номер_протокола"] = protocol_no
        index[serial] = payload
    return index


def _extract_first_value(row: Mapping[str, Any], keys: Iterable[str]) -> str:
    if not isinstance(row, Mapping):
        row = dict(row)

    pairs = [(str(key), row[key]) for key in row.keys() if isinstance(key, str)]

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
        vri_id = await fetch_vri_id_by_certificate(client, cert, sem=sem)
        if not vri_id:
            return ProtocolContextItem(
                certificate=cert,
                vri_id="",
                filename=filename,
                context={},
                raw_details={},
                error="not found",
            )

        details = await fetch_vri_details(client, vri_id, sem=sem)
        if not details:
            return ProtocolContextItem(
                certificate=cert,
                vri_id="",
                filename=filename,
                context={},
                raw_details={},
                error="not found",
            )

        et_cert = await find_etalon_certificate(client, details, sem=sem)
        if et_cert:
            row_data["_resolved_etalon_cert"] = et_cert

        ctx = await build_protocol_context(row_data, details, client, session=session)
        if protocol_number:
            ctx["protocol_number"] = protocol_number
        equipment_label = _extract_equipment_label_from_sources(db_row, row_data)
        if equipment_label:
            ctx.setdefault("equipment_label", equipment_label)

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
        row_data = dict(row)
        cert = extract_certificate_number(row_data)
        filename = suggest_filename(row_data)

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
            vri_id = await fetch_vri_id_by_certificate(client, cert, sem=sem)
            if not vri_id:
                return ProtocolContextItem(
                    certificate=cert,
                    vri_id="",
                    filename=filename,
                    context={},
                    raw_details={},
                    error="not found",
                )

            details = await fetch_vri_details(client, vri_id, sem=sem)
            if not details:
                return ProtocolContextItem(
                    certificate=cert,
                    vri_id="",
                    filename=filename,
                    context={},
                    raw_details={},
                    error="not found",
                )

            # 4) авто-поиск свидетельства эталона с учётом семафора
            et_cert = await find_etalon_certificate(client, details, sem=sem)
            if et_cert:
                row_data["_resolved_etalon_cert"] = et_cert  # билдер это подхватит

            # 5) собрать контекст
            ctx = await build_protocol_context(row_data, details, client, session=session)

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

    success_count = sum(1 for it in items if not it.error)
    logger.info(
        "contexts_by_excel: processed=%d success=%d errors=%d",
        len(items),
        success_count,
        len(items) - success_count,
    )

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

    row_data = dict(rows[0])
    cert = extract_certificate_number(row_data)
    if not cert:
        raise HTTPException(status_code=400, detail="certificate number is empty")

    vri_id = await fetch_vri_id_by_certificate(client, cert, sem=sem)
    if not vri_id:
        raise HTTPException(status_code=404, detail="not found")

    details = await fetch_vri_details(client, vri_id, sem=sem)
    if not details:
        raise HTTPException(status_code=404, detail="not found")

    et_cert = await find_etalon_certificate(client, details, sem=sem)
    if et_cert:
        row_data["_resolved_etalon_cert"] = et_cert

    ctx = await build_protocol_context(row_data, details, client, session=session)

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
    base_name = suggest_filename(ctx) or suggest_filename(row_data) or "protocol"
    if not base_name.lower().endswith(".html"):
        base_name = f"{base_name}.html"
    out_path = _unique_output_path(out_dir, base_name)
    out_path.write_text(html, encoding="utf-8")

    return HTMLResponse(content=html, media_type="text/html")


@router.post("/controllers/pdf-files")
async def controllers_pdf_files(
    controllers_file: UploadFile = File(...),
    db_file: UploadFile | None = File(default=None),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
    session: AsyncSession = Depends(get_db),
):
    controllers_data = await controllers_file.read()
    db_data = await db_file.read() if db_file is not None else None

    if not controllers_data:
        raise HTTPException(status_code=400, detail="empty controllers file")
    if db_file is not None and not db_data:
        raise HTTPException(status_code=400, detail="empty db file")

    rows = read_rows_as_dicts(controllers_data)
    if not rows:
        return {"files": [], "count": 0}

    if db_data is not None:
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

    lookup_serials = {
        normalize_serial(_extract_first_value(row, SERIAL_SOURCE_KEYS))
        for row in rows
    }
    registry_entries = await registry_repo.find_active_by_serials(lookup_serials)
    db_index = _entries_to_index(registry_entries)

    async def process_row(row: dict[str, Any]) -> ProtocolContextItem:
        serial = _extract_first_value(row, SERIAL_SOURCE_KEYS)
        normalized_serial = normalize_serial(serial)
        db_row: Mapping[str, Any] | None = db_index.get(normalized_serial or "")
        return await _build_context_from_db(
            row,
            db_row=db_row,
            client=client,
            sem=sem,
            session=session,
            strict_certificate_match=False,
        )

    items: list[ProtocolContextItem] = []
    for row in rows:
        items.append(await process_row(row))
    total_items = len(items)

    exports_dir: Path | None = None
    exports_label: str | None = None
    forced_month = _extract_month_from_filename(db_file.filename) if db_file else None
    pdf_unavailable = False
    saved: list[str] = []
    errors: list[dict[str, object]] = []

    logger.info(
        "controllers_pdf_files: starting export for {} devices (forced_month={})",
        total_items,
        forced_month or "auto",
    )

    for idx, (it, src_row) in enumerate(zip(items, rows), start=1):
        ctx = it.context or {}
        serial = _extract_first_value(src_row, SERIAL_SOURCE_KEYS)
        logger.info(
            "controllers_pdf_files: processing row={}/{} serial={} certificate={}",
            idx,
            total_items,
            serial or "-",
            it.certificate or "-",
        )

        if it.error or not ctx:
            errors.append(
                {
                    "row": idx,
                    "serial": serial,
                    "certificate": it.certificate,
                    "reason": it.error or "empty context",
                }
            )
            logger.warning(
                "controllers_pdf_files: skipped serial={} row={} reason={}",
                serial or "-",
                idx,
                it.error or "empty context",
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

        folder_label = _exports_folder_label(
            ctx,
            default_equipment="Контроллеры",
            forced_month=forced_month,
            use_default_only=True,
        )
        if exports_dir is None or folder_label != exports_label:
            exports_dir = get_named_exports_dir(folder_label)
            exports_label = folder_label

        base_name = _context_pdf_filename(ctx)
        path = _unique_output_path(exports_dir, base_name)
        path.write_bytes(pdf_bytes)
        saved.append(str(path))
        logger.info(
            "controllers_pdf_files: saved serial={} path={}",
            serial or "-",
            path,
        )

    if not saved and pdf_unavailable:
        raise HTTPException(
            status_code=500, detail="PDF generation is unavailable (Playwright not installed)"
        )

    failed_serials = [str(item.get("serial") or "-") for item in errors]
    if failed_serials:
        logger.warning(
            "controllers_pdf_files: failed serials={}",
            ", ".join(failed_serials),
        )

    logger.info(
        "controllers_pdf_files summary: total={} success={} failed={} pdf_unavailable={}",
        total_items,
        len(saved),
        len(errors),
        pdf_unavailable,
    )

    return {"files": saved, "count": len(saved), "errors": errors}


@router.post("/manometers/pdf-files")
async def manometers_pdf_files(
    manometers_file: UploadFile = File(...),
    db_file: UploadFile | None = File(default=None),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
    session: AsyncSession = Depends(get_db),
):
    manometers_data = await manometers_file.read()
    db_data = await db_file.read() if db_file is not None else None

    if not manometers_data:
        raise HTTPException(status_code=400, detail="empty manometers file")
    if db_file is not None and not db_data:
        raise HTTPException(status_code=400, detail="empty db file")

    rows = read_rows_as_dicts(manometers_data)
    if not rows:
        return {"files": [], "count": 0, "errors": []}

    if db_data is not None:
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

    lookup_serials = {
        normalize_serial(_extract_first_value(row, SERIAL_SOURCE_KEYS))
        for row in rows
    }
    registry_entries = await registry_repo.find_active_by_serials(lookup_serials)
    db_index = _entries_to_index(registry_entries)

    async def process_row(row: dict[str, Any]) -> ProtocolContextItem:
        serial = _extract_first_value(row, SERIAL_SOURCE_KEYS)
        normalized_serial = normalize_serial(serial)
        db_row: Mapping[str, Any] | None = db_index.get(normalized_serial or "")
        return await _build_context_from_db(
            row,
            db_row=db_row,
            client=client,
            sem=sem,
            session=session,
            strict_certificate_match=True,
        )

    items: list[ProtocolContextItem] = []
    for row in rows:
        items.append(await process_row(row))
    total_items = len(items)

    exports_dir: Path | None = None
    exports_label: str | None = None
    forced_month = _extract_month_from_filename(db_file.filename) if db_file else None
    pdf_unavailable = False
    saved: list[str] = []
    errors: list[dict[str, object]] = []

    logger.info(
        "manometers_pdf_files: starting export for {} devices (forced_month={})",
        total_items,
        forced_month or "auto",
    )

    for idx, (it, src_row) in enumerate(zip(items, rows), start=1):
        ctx = it.context or {}
        serial = _extract_first_value(src_row, SERIAL_SOURCE_KEYS)
        logger.info(
            "manometers_pdf_files: processing row={}/{} serial={} certificate={}",
            idx,
            total_items,
            serial or "-",
            it.certificate or "-",
        )

        if it.error or not ctx:
            errors.append(
                {
                    "row": idx,
                    "serial": serial,
                    "certificate": it.certificate,
                    "reason": it.error or "empty context",
                }
            )
            logger.warning(
                "manometers_pdf_files: skipped serial={} row={} reason={}",
                serial or "-",
                idx,
                it.error or "empty context",
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

        folder_label = _exports_folder_label(
            ctx,
            default_equipment="Манометры",
            forced_month=forced_month,
            use_default_only=True,
        )
        if exports_dir is None or folder_label != exports_label:
            exports_dir = get_named_exports_dir(folder_label)
            exports_label = folder_label

        base_name = _context_pdf_filename(ctx)
        path = _unique_output_path(exports_dir, base_name)
        path.write_bytes(pdf_bytes)
        saved.append(str(path))
        logger.info(
            "manometers_pdf_files: saved serial={} path={}",
            serial or "-",
            path,
        )

    if not saved and pdf_unavailable:
        raise HTTPException(
            status_code=500, detail="PDF generation is unavailable (Playwright not installed)"
        )

    failed_serials = [str(item.get("serial") or "-") for item in errors]
    if failed_serials:
        logger.warning(
            "manometers_pdf_files: failed serials={}",
            ", ".join(failed_serials),
        )

    logger.info(
        "manometers_pdf_files summary: total={} success={} failed={} pdf_unavailable={}",
        total_items,
        len(saved),
        len(errors),
        pdf_unavailable,
    )

    return {"files": saved, "count": len(saved), "errors": errors}
