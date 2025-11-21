from __future__ import annotations

import asyncio
import re
import time
from collections.abc import Awaitable, Callable, Iterable, Mapping, Sequence
from datetime import date, datetime
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.responses import HTMLResponse

from app.api.deps import get_db, get_http_client, get_semaphore
from app.core.config import settings
from app.db.repositories import RegistryRepository
from app.schemas.protocol import ProtocolContextItem, ProtocolContextListOut
from app.services.arshin_client import (
    fetch_vri_details,
    fetch_vri_id_by_certificate,
    find_etalon_certificates,
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

_RETRYABLE_CONTEXT_ERROR_MARKERS: tuple[str, ...] = (
    "retryable status",
    "transport error",
    "timeout",
)
_CONTEXT_RETRY_ATTEMPTS = max(0, int(settings.PROTOCOL_RETRY_ATTEMPTS))
_CONTEXT_RETRY_DELAY_SECONDS = max(0.0, float(settings.PROTOCOL_RETRY_DELAY))


def _make_worker_session_factory(
    session: AsyncSession,
) -> async_sessionmaker[AsyncSession]:
    bind = session.bind
    if bind is None:
        raise RuntimeError("database session is not bound to an engine")
    return async_sessionmaker(bind=bind, class_=AsyncSession, expire_on_commit=False)


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


def _registry_entry_sort_key(entry: Mapping[str, Any]) -> tuple:
    ver_date = entry.get("verification_date") or date.min
    loaded_at = entry.get("loaded_at") or datetime.min
    row_index = entry.get("row_index") or 0
    return (ver_date, loaded_at, row_index)


def _serialize_registry_entry(entry: Any) -> dict[str, Any]:
    payload = dict(getattr(entry, "payload", {}) or {})
    document_no = getattr(entry, "document_no", None)
    protocol_no = getattr(entry, "protocol_no", None)
    if document_no and not payload.get("Документ"):
        payload["Документ"] = document_no
    if protocol_no and not payload.get("номер_протокола"):
        payload["номер_протокола"] = protocol_no

    return {
        "payload": payload,
        "verification_date": getattr(entry, "verification_date", None),
        "valid_to": getattr(entry, "valid_to", None),
        "source_file": getattr(entry, "source_file", None),
        "row_index": getattr(entry, "row_index", None),
        "loaded_at": getattr(entry, "loaded_at", None),
    }


def _entries_to_index(entries: Mapping[str, list[Any]]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for serial, records in entries.items():
        if not records:
            continue
        serialized = [_serialize_registry_entry(entry) for entry in records if entry]
        if not serialized:
            continue
        serialized.sort(key=_registry_entry_sort_key, reverse=True)
        index[serial] = serialized
    return index


def _row_verification_date(row: Mapping[str, Any]) -> date | None:
    for key in ("Дата поверки", "verification_date", "verificationDate"):
        value = row.get(key)
        parsed = _parse_date_value(value)
        if parsed:
            return parsed
    return None


def _select_registry_entry(
    entries: Sequence[Mapping[str, Any]] | None, desired_date: date | None
) -> Mapping[str, Any] | None:
    if not entries:
        return None

    if desired_date:
        for entry in entries:
            entry_date = entry.get("verification_date")
            if isinstance(entry_date, date) and entry_date == desired_date:
                return entry

        for entry in entries:
            entry_date = entry.get("verification_date")
            if (
                isinstance(entry_date, date)
                and entry_date.year == desired_date.year
                and entry_date.month == desired_date.month
            ):
                return entry

    return entries[0]


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


async def _build_contexts_concurrently(
    rows: Sequence[dict[str, Any]],
    worker: Callable[[dict[str, Any]], Awaitable[ProtocolContextItem]],
    *,
    label: str,
) -> list[ProtocolContextItem]:
    total = len(rows)
    if total == 0:
        return []

    concurrency = max(1, int(settings.PROTOCOL_BUILD_CONCURRENCY))
    sem = asyncio.Semaphore(concurrency)
    lock = asyncio.Lock()
    completed = 0
    progress_every = max(total // 10, 1)
    started = time.perf_counter()

    logger.info(f"{label}: starting context build for {total} rows (concurrency={concurrency})")

    async def run(row: dict[str, Any]) -> ProtocolContextItem:
        nonlocal completed
        async with sem:
            result = await worker(row)

        log_now = False
        current = 0
        async with lock:
            completed += 1
            current = completed
            if current == total or current % progress_every == 0:
                log_now = True
        if log_now:
            logger.info(
                f"{label}: prepared {current}/{total} contexts "
                f"({time.perf_counter() - started:.2f}s elapsed)"
            )
        return result

    return await asyncio.gather(*(run(row) for row in rows))


def _is_retryable_context_error(error: str | None) -> bool:
    if not error:
        return False
    lowered = error.lower()
    return any(marker in lowered for marker in _RETRYABLE_CONTEXT_ERROR_MARKERS)


async def _retry_context_rows(
    rows: Sequence[dict[str, Any]],
    items: list[ProtocolContextItem],
    worker: Callable[[dict[str, Any]], Awaitable[ProtocolContextItem]],
    *,
    label: str,
    attempts: int = _CONTEXT_RETRY_ATTEMPTS,
    delay: float = _CONTEXT_RETRY_DELAY_SECONDS,
) -> list[ProtocolContextItem]:
    if attempts <= 0:
        return items

    attempt = 0
    while attempt < attempts:
        retry_indexes = [
            idx for idx, item in enumerate(items) if _is_retryable_context_error(item.error)
        ]
        if not retry_indexes:
            break
        attempt += 1
        delay_current = delay * attempt
        logger.warning(
            f"{label}: retrying {len(retry_indexes)} rows due to retryable errors "
            f"(attempt {attempt}/{attempts}, per-row delay {delay_current:.1f}s)"
        )
        for idx in retry_indexes:
            if delay_current > 0:
                await asyncio.sleep(delay_current)
            items[idx] = await worker(rows[idx])
    return items


async def _build_context_from_db(
    row: Mapping[str, Any],
    *,
    db_index: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
    db_entries: Sequence[Mapping[str, Any]] | None = None,
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    session_factory: async_sessionmaker[AsyncSession],
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

    candidates = list(db_entries or [])
    if not candidates and db_index is not None:
        candidates = list(db_index.get(serial_key) or [])

    selected_entry = _select_registry_entry(candidates, _row_verification_date(row_data))
    if not selected_entry:
        return ProtocolContextItem(
            certificate="",
            vri_id="",
            filename=filename,
            context={},
            raw_details={},
            error="serial number not found in db",
        )

    db_row = dict(selected_entry.get("payload") or {})

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
        vri_id = await fetch_vri_id_by_certificate(client, cert, sem=sem, use_cache=False)
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

        et_certs = await find_etalon_certificates(client, details, sem=sem)
        if et_certs:
            row_data["_resolved_etalon_certs"] = et_certs
            row_data["_resolved_etalon_cert"] = et_certs[0]

        async with session_factory() as worker_session:
            ctx = await build_protocol_context(
                row_data,
                details,
                client,
                session=worker_session,
            )
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


async def _build_context_from_excel_row(
    row: Mapping[str, Any],
    *,
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    session_factory: async_sessionmaker[AsyncSession],
) -> ProtocolContextItem:
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

        et_certs = await find_etalon_certificates(client, details, sem=sem)
        if et_certs:
            row_data["_resolved_etalon_certs"] = et_certs
            row_data["_resolved_etalon_cert"] = et_certs[0]

        async with session_factory() as worker_session:
            ctx = await build_protocol_context(
                row_data,
                details,
                client,
                session=worker_session,
            )

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
    session_factory = _make_worker_session_factory(session)

    async def process_row(row: dict[str, Any]) -> ProtocolContextItem:
        return await _build_context_from_excel_row(
            row,
            client=client,
            sem=sem,
            session_factory=session_factory,
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
    total = len(items)
    errors_count = total - success_count
    logger.info(
        f"contexts_by_excel: processed={total} success={success_count} "
        f"errors={errors_count}"
    )

    return ProtocolContextListOut(items=items)


_INSTRUMENT_META = {
    "manometers": {"source_sheet": "manometers", "strict_certificate_match": True},
    "controllers": {"source_sheet": "controllers", "strict_certificate_match": False},
}


def _detect_instrument_kind(row: Mapping[str, Any]) -> str:
    type_keys = (
        "Тип СИ",
        "Наименование СИ",
        "Тип",
        "Обозначение СИ",
    )
    text_parts: list[str] = []
    for key in type_keys:
        value = row.get(key)
        if not value:
            continue
        value_text = str(value).strip()
        if value_text:
            text_parts.append(value_text)
    combined = " ".join(text_parts).upper()
    if "43790-12" in combined or "КОНТРОЛЛЕР" in combined or "СГМ" in combined:
        return "controllers"
    return "manometers"


@router.post("/html-by-excel", response_class=HTMLResponse)
async def html_by_excel(
    instrument_file: UploadFile = File(..., alias="file"),
    db_file: UploadFile | None = File(default=None),
    row: int = 1,
    instrument_kind: str | None = None,
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
    session: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Возвращает HTML по тем же данным, что используются в PDF ручках."""

    instrument_data = await instrument_file.read()
    db_data = await db_file.read() if db_file is not None else None

    if not instrument_data:
        raise HTTPException(status_code=400, detail="empty instrument file")
    if db_file is not None and not db_data:
        raise HTTPException(status_code=400, detail="empty db file")

    rows = read_rows_as_dicts(instrument_data)
    if not rows:
        raise HTTPException(status_code=400, detail="no rows in instrument file")

    row_index = max(1, row)
    if row_index > len(rows):
        raise HTTPException(status_code=400, detail="row index is out of range")

    target_row = dict(rows[row_index - 1])

    kind_param = (instrument_kind or "").strip().lower()
    if kind_param and kind_param not in _INSTRUMENT_META:
        raise HTTPException(status_code=400, detail="unknown instrument kind")
    resolved_kind = kind_param or _detect_instrument_kind(target_row)
    meta = _INSTRUMENT_META.get(resolved_kind, _INSTRUMENT_META["manometers"])

    if db_data is not None:
        db_rows = read_rows_with_required_headers(
            db_data,
            header_row=5,
            data_start_row=6,
            required_headers=DB_SERIAL_KEYS,
        )
        if not db_rows:
            raise HTTPException(status_code=400, detail="db file has no serial entries")

        logger.info(
            f"html_by_excel: ingesting {len(db_rows)} registry rows "
            f"from {db_file.filename or 'registry.xlsx'} (kind={resolved_kind})"
        )
        ingest_started = time.perf_counter()
        ingest_result = await ingest_registry_rows(
            session,
            source_file=db_file.filename or "registry.xlsx",
            rows=db_rows,
            source_sheet=meta["source_sheet"],
        )
        logger.info(
            "html_by_excel: registry ingest finished "
            f"processed={ingest_result.get('processed', 0)} "
            f"deactivated={ingest_result.get('deactivated', 0)} "
            f"({time.perf_counter() - ingest_started:.2f}s)"
        )

    registry_repo = RegistryRepository(session)
    lookup_serials = {
        normalize_serial(_extract_first_value(row_data, SERIAL_SOURCE_KEYS)) for row_data in rows
    }
    registry_entries = await registry_repo.find_active_by_serials(lookup_serials)
    db_index = _entries_to_index(registry_entries)

    session_factory = _make_worker_session_factory(session)
    normalized_serial = normalize_serial(_extract_first_value(target_row, SERIAL_SOURCE_KEYS))
    db_entries = db_index.get(normalized_serial or "")

    if db_entries:
        context_item = await _build_context_from_db(
            target_row,
            db_entries=db_entries,
            client=client,
            sem=sem,
            session_factory=session_factory,
            strict_certificate_match=bool(meta["strict_certificate_match"]),
        )
    else:
        context_item = await _build_context_from_excel_row(
            target_row,
            client=client,
            sem=sem,
            session_factory=session_factory,
        )
    if context_item.error or not context_item.context:
        raise HTTPException(
            status_code=502,
            detail=context_item.error or "failed to build context",
        )

    ctx = dict(context_item.context)
    if not ctx.get("protocol_number"):
        ctx["protocol_number"] = make_protocol_number(
            ctx.get("verifier_name"),
            ctx.get("verification_date"),
            row_index,
        )

    html = render_protocol_html(ctx)
    out_dir = get_output_dir()
    base_name = suggest_filename(ctx) or suggest_filename(target_row) or "protocol"
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
    overall_started = time.perf_counter()
    controllers_data = await controllers_file.read()
    db_data = await db_file.read() if db_file is not None else None

    if not controllers_data:
        raise HTTPException(status_code=400, detail="empty controllers file")
    if db_file is not None and not db_data:
        raise HTTPException(status_code=400, detail="empty db file")

    rows = read_rows_as_dicts(controllers_data)
    if not rows:
        return {"files": [], "count": 0}

    logger.info(
        f"controllers_pdf_files: loaded {len(rows)} controller rows "
        f"(db_file={'yes' if db_file else 'no'})"
    )

    if db_data is not None:
        db_rows = read_rows_with_required_headers(
            db_data,
            header_row=5,
            data_start_row=6,
            required_headers=DB_SERIAL_KEYS,
        )
        if not db_rows:
            raise HTTPException(status_code=400, detail="db file has no serial entries")

        logger.info(
            f"controllers_pdf_files: ingesting {len(db_rows)} registry rows "
            f"from {db_file.filename or 'registry.xlsx'}"
        )
        ingest_started = time.perf_counter()
        ingest_result = await ingest_registry_rows(
            session,
            source_file=db_file.filename or "registry.xlsx",
            rows=db_rows,
            source_sheet="controllers",
        )
        logger.info(
            "controllers_pdf_files: registry ingest finished "
            f"processed={ingest_result.get('processed', 0)} "
            f"deactivated={ingest_result.get('deactivated', 0)} "
            f"({time.perf_counter() - ingest_started:.2f}s)"
        )

    registry_repo = RegistryRepository(session)

    lookup_serials = {
        normalize_serial(_extract_first_value(row, SERIAL_SOURCE_KEYS))
        for row in rows
    }
    registry_entries = await registry_repo.find_active_by_serials(lookup_serials)
    db_index = _entries_to_index(registry_entries)
    registry_matches = sum(len(v) for v in registry_entries.values())
    logger.info(
        "controllers_pdf_files: registry index ready "
        f"serials={len(lookup_serials)} entries={registry_matches}"
    )
    session_factory = _make_worker_session_factory(session)

    async def process_row(row: dict[str, Any]) -> ProtocolContextItem:
        serial = _extract_first_value(row, SERIAL_SOURCE_KEYS)
        normalized_serial = normalize_serial(serial)
        db_entries = db_index.get(normalized_serial or "")
        return await _build_context_from_db(
            row,
            db_entries=db_entries,
            client=client,
            sem=sem,
            session_factory=session_factory,
            strict_certificate_match=False,
        )

    build_started = time.perf_counter()
    items = await _build_contexts_concurrently(
        rows,
        process_row,
        label="controllers_pdf_files",
    )
    build_elapsed = time.perf_counter() - build_started
    total_items = len(items)
    success_contexts = sum(1 for item in items if not item.error)
    logger.info(
        "controllers_pdf_files: contexts ready "
        f"success={success_contexts} failed={total_items - success_contexts} "
        f"({build_elapsed:.2f}s)"
    )

    exports_dir: Path | None = None
    exports_label: str | None = None
    forced_month = _extract_month_from_filename(db_file.filename) if db_file else None
    if not forced_month:
        forced_month = _extract_month_from_filename(controllers_file.filename)
    pdf_unavailable = False
    saved: list[str] = []
    errors: list[dict[str, object]] = []

    logger.info(
        "controllers_pdf_files: starting export for "
        f"{total_items} devices (forced_month={forced_month or 'auto'})"
    )

    for idx, (it, src_row) in enumerate(zip(items, rows), start=1):
        ctx = it.context or {}
        serial = _extract_first_value(src_row, SERIAL_SOURCE_KEYS)
        logger.info(
            "controllers_pdf_files: processing "
            f"row={idx}/{total_items} serial={serial or '-'} certificate={it.certificate or '-'}"
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
                "controllers_pdf_files: skipped "
                f"serial={serial or '-'} row={idx} reason={it.error or 'empty context'}"
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
            f"controllers_pdf_files: saved serial={serial or '-'} path={path}"
        )

    if not saved and pdf_unavailable:
        raise HTTPException(
            status_code=500, detail="PDF generation is unavailable (Playwright not installed)"
        )

    failed_serials = [str(item.get("serial") or "-") for item in errors]
    if failed_serials:
        logger.warning(
            f"controllers_pdf_files: failed serials={', '.join(failed_serials)}"
        )

    logger.info(
        "controllers_pdf_files summary: "
        f"total={total_items} success={len(saved)} failed={len(errors)} "
        f"pdf_unavailable={pdf_unavailable}"
    )

    total_elapsed = time.perf_counter() - overall_started
    logger.info(
        "controllers_pdf_files: finished in "
        f"{total_elapsed:.2f}s (files={len(saved)} errors={len(errors)})"
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
    overall_started = time.perf_counter()
    manometers_data = await manometers_file.read()
    db_data = await db_file.read() if db_file is not None else None

    if not manometers_data:
        raise HTTPException(status_code=400, detail="empty manometers file")
    if db_file is not None and not db_data:
        raise HTTPException(status_code=400, detail="empty db file")

    rows = read_rows_as_dicts(manometers_data)
    if not rows:
        return {"files": [], "count": 0, "errors": []}

    logger.info(
        f"manometers_pdf_files: loaded {len(rows)} manometer rows "
        f"(db_file={'yes' if db_file else 'no'})"
    )

    if db_data is not None:
        db_rows = read_rows_with_required_headers(
            db_data,
            header_row=5,
            data_start_row=6,
            required_headers=DB_SERIAL_KEYS,
        )
        if not db_rows:
            raise HTTPException(status_code=400, detail="db file has no serial entries")

        logger.info(
            f"manometers_pdf_files: ingesting {len(db_rows)} registry rows "
            f"from {db_file.filename or 'registry.xlsx'}"
        )
        ingest_started = time.perf_counter()
        ingest_result = await ingest_registry_rows(
            session,
            source_file=db_file.filename or "registry.xlsx",
            rows=db_rows,
            source_sheet="manometers",
        )
        logger.info(
            "manometers_pdf_files: registry ingest finished "
            f"processed={ingest_result.get('processed', 0)} "
            f"deactivated={ingest_result.get('deactivated', 0)} "
            f"({time.perf_counter() - ingest_started:.2f}s)"
        )

    registry_repo = RegistryRepository(session)

    lookup_serials = {
        normalize_serial(_extract_first_value(row, SERIAL_SOURCE_KEYS))
        for row in rows
    }
    registry_entries = await registry_repo.find_active_by_serials(lookup_serials)
    db_index = _entries_to_index(registry_entries)
    registry_matches = sum(len(v) for v in registry_entries.values())
    logger.info(
        "manometers_pdf_files: registry index ready "
        f"serials={len(lookup_serials)} entries={registry_matches}"
    )
    session_factory = _make_worker_session_factory(session)

    async def process_row(row: dict[str, Any]) -> ProtocolContextItem:
        serial = _extract_first_value(row, SERIAL_SOURCE_KEYS)
        normalized_serial = normalize_serial(serial)
        db_entries = db_index.get(normalized_serial or "")
        return await _build_context_from_db(
            row,
            db_entries=db_entries,
            client=client,
            sem=sem,
            session_factory=session_factory,
            strict_certificate_match=True,
        )

    build_started = time.perf_counter()
    items = await _build_contexts_concurrently(
        rows,
        process_row,
        label="manometers_pdf_files",
    )
    items = await _retry_context_rows(
        rows,
        items,
        process_row,
        label="manometers_pdf_files",
    )
    build_elapsed = time.perf_counter() - build_started
    total_items = len(items)
    success_contexts = sum(1 for item in items if not item.error)
    logger.info(
        "manometers_pdf_files: contexts ready "
        f"success={success_contexts} failed={total_items - success_contexts} "
        f"({build_elapsed:.2f}s)"
    )

    exports_dir: Path | None = None
    exports_label: str | None = None
    forced_month = _extract_month_from_filename(db_file.filename) if db_file else None
    pdf_unavailable = False
    saved: list[str] = []
    errors: list[dict[str, object]] = []

    logger.info(
        "manometers_pdf_files: starting export for "
        f"{total_items} devices (forced_month={forced_month or 'auto'})"
    )

    for idx, (it, src_row) in enumerate(zip(items, rows), start=1):
        ctx = it.context or {}
        serial = _extract_first_value(src_row, SERIAL_SOURCE_KEYS)
        logger.info(
            "manometers_pdf_files: processing "
            f"row={idx}/{total_items} serial={serial or '-'} certificate={it.certificate or '-'}"
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
                "manometers_pdf_files: skipped "
                f"serial={serial or '-'} row={idx} reason={it.error or 'empty context'}"
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
            f"manometers_pdf_files: saved serial={serial or '-'} path={path}"
        )

    if not saved and pdf_unavailable:
        raise HTTPException(
            status_code=500, detail="PDF generation is unavailable (Playwright not installed)"
        )

    failed_serials = [str(item.get("serial") or "-") for item in errors]
    if failed_serials:
        logger.warning(
            f"manometers_pdf_files: failed serials={', '.join(failed_serials)}"
        )

    logger.info(
        "manometers_pdf_files summary: "
        f"total={total_items} success={len(saved)} failed={len(errors)} "
        f"pdf_unavailable={pdf_unavailable}"
    )

    total_elapsed = time.perf_counter() - overall_started
    logger.info(
        "manometers_pdf_files: finished in "
        f"{total_elapsed:.2f}s (files={len(saved)} errors={len(errors)})"
    )

    return {"files": saved, "count": len(saved), "errors": errors}


@router.post("/manometers/html-preview", response_class=HTMLResponse)
async def manometers_html_preview(
    manometers_file: UploadFile = File(...),
    db_file: UploadFile | None = File(default=None),
    row: int = 1,
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
    session: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Рендерит HTML по данным manometers_file/db_file для выбранной строки."""

    manometers_data = await manometers_file.read()
    db_data = await db_file.read() if db_file is not None else None

    if not manometers_data:
        raise HTTPException(status_code=400, detail="empty manometers file")
    if db_file is not None and not db_data:
        raise HTTPException(status_code=400, detail="empty db file")

    rows = read_rows_as_dicts(manometers_data)
    if not rows:
        raise HTTPException(status_code=400, detail="no rows in manometers file")

    row_index = max(1, row)
    if row_index > len(rows):
        raise HTTPException(status_code=400, detail="row index is out of range")
    target_row = dict(rows[row_index - 1])

    if db_data is not None:
        db_rows = read_rows_with_required_headers(
            db_data,
            header_row=5,
            data_start_row=6,
            required_headers=DB_SERIAL_KEYS,
        )
        if not db_rows:
            raise HTTPException(status_code=400, detail="db file has no serial entries")

        logger.info(
            f"manometers_html_preview: ingesting {len(db_rows)} registry rows "
            f"from {db_file.filename or 'registry.xlsx'}"
        )
        ingest_started = time.perf_counter()
        ingest_result = await ingest_registry_rows(
            session,
            source_file=db_file.filename or "registry.xlsx",
            rows=db_rows,
            source_sheet="manometers",
        )
        logger.info(
            "manometers_html_preview: registry ingest finished "
            f"processed={ingest_result.get('processed', 0)} "
            f"deactivated={ingest_result.get('deactivated', 0)} "
            f"({time.perf_counter() - ingest_started:.2f}s)"
        )

    registry_repo = RegistryRepository(session)
    lookup_serials = {
        normalize_serial(_extract_first_value(row_data, SERIAL_SOURCE_KEYS)) for row_data in rows
    }
    registry_entries = await registry_repo.find_active_by_serials(lookup_serials)
    db_index = _entries_to_index(registry_entries)

    session_factory = _make_worker_session_factory(session)
    normalized_serial = normalize_serial(_extract_first_value(target_row, SERIAL_SOURCE_KEYS))
    db_entries = db_index.get(normalized_serial or "")

    context_item = await _build_context_from_db(
        target_row,
        db_entries=db_entries,
        client=client,
        sem=sem,
        session_factory=session_factory,
        strict_certificate_match=True,
    )
    if context_item.error or not context_item.context:
        raise HTTPException(
            status_code=502,
            detail=context_item.error or "failed to build context",
        )

    ctx = dict(context_item.context)
    if not ctx.get("protocol_number"):
        ctx["protocol_number"] = make_protocol_number(
            ctx.get("verifier_name"),
            ctx.get("verification_date"),
            row_index,
        )

    html = render_protocol_html(ctx)

    out_dir = get_output_dir()
    base_name = suggest_filename(ctx) or suggest_filename(target_row) or "protocol-preview"
    if not base_name.lower().endswith(".html"):
        base_name = f"{base_name}.html"
    out_path = _unique_output_path(out_dir, base_name)
    out_path.write_text(html, encoding="utf-8")

    return HTMLResponse(content=html, media_type="text/html")
