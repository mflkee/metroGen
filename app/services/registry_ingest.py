from __future__ import annotations

import re
import time
from collections.abc import Iterable, Mapping
from datetime import date, datetime, timedelta
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import RegistryRepository
from app.services.mappings import ensure_methodology, ensure_owner
from app.utils.normalization import normalize_serial

_OWNER_KEYS = (
    "Владелец СИ",
    "Владелец",
    "Организация",
    "owner_name",
)

_OWNER_INN_KEYS = (
    "ИНН",
    "ИНН владельца",
    "ИНН владельца СИ",
    "ИНН организации",
    "inn",
)

_METHODOLOGY_KEYS = (
    "Методика поверки",
    "Методика",
    "methodology",
)

_SERIAL_KEYS = (
    "Заводской №/ Буквенно-цифровое обозначение",
    "Заводской номер",
    "Заводской №",
    "Серийный номер",
    "serial",
)

# Public alias used by API layer for header validation
REGISTRY_SERIAL_KEYS = _SERIAL_KEYS

_VERIFICATION_DATE_KEYS = (
    "Дата поверки",
    "Дата поверки по реестру",
    "verification_date",
)

_VALID_TO_KEYS = (
    "Действительно до",
    "Дата окончания",
    "valid_to",
)

_PROTOCOL_NO_KEYS = (
    "номер_протокола",
    "номер протокола",
    "№ протокола",
    "№протокола",
    "№ проток.",
    "номер прот.",
)

_ORDER_IN_MONTH_KEYS = (
    "ном_по_порядку_с_начала_месяца",
    "номер по порядку с начала месяца",
    "ном по порядку с начала месяца",
)

def _coerce_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _coerce_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value != value:
            return None
        return int(value)
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _normalize_header_key(value: str) -> str:
    text = str(value).replace("\xa0", " ").replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def _extract_first(row: Mapping[str, Any], keys: Iterable[str]) -> Any:
    normalized: dict[str, Any] = {}
    for existing_key, existing_value in row.items():
        if not isinstance(existing_key, str):
            continue
        if existing_value in (None, ""):
            continue
        normalized[_normalize_header_key(existing_key)] = existing_value

    for key in keys:
        value = normalized.get(_normalize_header_key(key))
        if value is not None:
            return value
    return None


def _extract_by_keyword(row: Mapping[str, Any], keyword: str) -> Any:
    target = _normalize_header_key(keyword)
    if not target:
        return None
    for existing_key, existing_value in row.items():
        if not isinstance(existing_key, str):
            continue
        if existing_value in (None, ""):
            continue
        normalized = _normalize_header_key(existing_key)
        if target in normalized:
            return existing_value
    return None


def _ensure_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, int | float):
        return _excel_serial_to_date(value)
    text = _coerce_str(value)
    if not text:
        return None
    if text.replace(".", "", 1).isdigit():
        serial = _coerce_int(text)
        if serial is not None:
            converted = _excel_serial_to_date(serial)
            if converted:
                return converted

    candidates = (
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
    )
    for fmt in candidates:
        try:
            return datetime.strptime(text, fmt).date()
        except Exception:
            continue
    return None


def _excel_serial_to_date(value: Any) -> date | None:
    try:
        serial = float(value)
    except (TypeError, ValueError):
        return None
    if serial <= 0:
        return None
    # Excel 1900 date system with the leap-year bug baked in.
    return (datetime(1899, 12, 30) + timedelta(days=serial)).date()


def _build_protocol_no(verification_date: date, order_in_month: int) -> str:
    return f"{verification_date.month:02d}/{order_in_month:03d}/{verification_date.year % 100:02d}"


def _sanitize_payload(row: Mapping[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            sanitized[key] = value.isoformat()
        elif isinstance(value, date):
            sanitized[key] = value.isoformat()
        else:
            sanitized[key] = value
    return sanitized


async def ingest_registry_rows(
    session: AsyncSession,
    *,
    source_file: str,
    rows: Iterable[Mapping[str, Any]],
    source_sheet: str | None = None,
    instrument_kind: str | None = None,
) -> dict[str, int]:
    """Persist registry-like rows into the database using repository helpers."""

    start_time = time.perf_counter()
    registry_repo = RegistryRepository(session)
    last_order_in_month: int | None = None

    deactivated = await registry_repo.deactivate_for_source(source_file)
    if deactivated:
        logger.info(
            "ingest_registry_rows[{}]: deactivated {} previous rows",
            source_file,
            deactivated,
        )

    processed = 0
    for processed, row in enumerate(rows, start=1):
        owner_name = _coerce_str(_extract_first(row, _OWNER_KEYS))
        owner_inn = _coerce_str(_extract_first(row, _OWNER_INN_KEYS))
        methodology_raw = _coerce_str(_extract_first(row, _METHODOLOGY_KEYS))
        verification_date = _ensure_date(_extract_first(row, _VERIFICATION_DATE_KEYS))
        valid_to = _ensure_date(_extract_first(row, _VALID_TO_KEYS))
        document_no = _coerce_str(row.get("Документ"))
        protocol_no = _coerce_str(_extract_first(row, _PROTOCOL_NO_KEYS))
        if not protocol_no:
            protocol_no = _coerce_str(_extract_by_keyword(row, "протокол"))
        order_raw = _extract_first(row, _ORDER_IN_MONTH_KEYS)
        order_in_month = _coerce_int(order_raw)
        if order_in_month is None and last_order_in_month is not None:
            order_in_month = last_order_in_month + 1
        if order_in_month is not None:
            last_order_in_month = order_in_month
        if not protocol_no and verification_date:
            if order_in_month is not None:
                protocol_no = _build_protocol_no(verification_date, order_in_month)
        serial_raw = _extract_first(row, _SERIAL_KEYS)
        normalized_serial = normalize_serial(serial_raw)

        await registry_repo.upsert_entry(
            source_file=source_file,
            row_index=processed,
            values={
                "source_sheet": source_sheet,
                "instrument_kind": instrument_kind,
                "normalized_serial": normalized_serial or None,
                "document_no": document_no,
                "protocol_no": protocol_no,
                "owner_name_raw": owner_name,
                "methodology_raw": methodology_raw,
                "verification_date": verification_date,
                "valid_to": valid_to,
                "payload": _sanitize_payload(dict(row)),
                "is_active": True,
            },
        )

        if owner_name:
            owner = await ensure_owner(
                session,
                owner_name,
                inn_hint=owner_inn,
                aliases=[owner_name],
            )
            if owner and owner.inn:
                owner_inn = owner.inn

        if methodology_raw:
            await ensure_methodology(session, methodology_raw)

        if processed and processed % 250 == 0:
            logger.info(
                "ingest_registry_rows[{}]: processed {} rows",
                source_file,
                processed,
            )

    if processed or deactivated:
        await session.commit()

    elapsed = time.perf_counter() - start_time
    logger.info(
        "ingest_registry_rows[{}]: finished processed={} deactivated={} elapsed={:.2f}s",
        source_file,
        processed,
        deactivated,
        elapsed,
    )
    return {"processed": processed, "deactivated": deactivated}
