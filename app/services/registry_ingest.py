from __future__ import annotations

import time
from collections.abc import Iterable, Mapping
from datetime import date, datetime
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


def _coerce_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _extract_first(row: Mapping[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
        lower_key = key.lower()
        for existing_key, existing_value in row.items():
            if not isinstance(existing_key, str):
                continue
            if existing_key.strip().lower() == lower_key and existing_value not in (None, ""):
                return existing_value
    return None


def _ensure_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = _coerce_str(value)
    if not text:
        return None

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

    deactivated = await registry_repo.deactivate_for_source(source_file)
    if deactivated:
        logger.info(
            "ingest_registry_rows[%s]: deactivated %d previous rows",
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
        protocol_no = _coerce_str(row.get("номер_протокола"))
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
                "ingest_registry_rows[%s]: processed %d rows",
                source_file,
                processed,
            )

    if processed or deactivated:
        await session.commit()

    elapsed = time.perf_counter() - start_time
    logger.info(
        "ingest_registry_rows[%s]: finished processed=%d deactivated=%d elapsed=%.2fs",
        source_file,
        processed,
        deactivated,
        elapsed,
    )
    return {"processed": processed, "deactivated": deactivated}
