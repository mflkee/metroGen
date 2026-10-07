"""Локальный справочник вспомогательных СИ с ленивым обновлением из Аршина.

Аналог ``etalon_registry`` для таблицы ``auxiliary_verification_instruments``:
во входном Excel вспомогательные СИ заданы парой ``рег-номер/зав-номер``
(например ``71394-18/83243``). Если свидетельство в БД просрочено (или записи
нет) — перезапрашиваем его в Аршине по ``mit_number``/``mi_number`` и
сохраняем; иначе используем данные из БД.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

import httpx
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import AuxiliaryInstrumentRepository
from app.services.arshin_client import ARSHIN_BASE, _parse_date_value, _request_json
from app.utils.normalization import normalize_serial

__all__ = ("resolve_auxiliary",)


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _fixture_from_details(
    details: Mapping[str, Any], reg: str, serial: str
) -> Mapping[str, Any] | None:
    """Найти запись вспом. СИ в ответе Аршина по прибору (``means.mis``)."""
    means = details.get("means") or {}
    if not isinstance(means, Mapping):
        return None
    for item in means.get("mis") or []:
        if not isinstance(item, Mapping):
            continue
        num = _clean(item.get("number") or item.get("factoryNum"))
        if _clean(item.get("mitypeNumber")) == reg and num == serial:
            return item
    return None


async def _fetch_certificate(
    client: httpx.AsyncClient, reg: str, serial: str, sem: Any
) -> Mapping[str, Any] | None:
    """Свежее свидетельство вспом. СИ из Аршина по (mit_number, mi_number)."""
    data = await _request_json(
        client,
        f"{ARSHIN_BASE}/vri",
        params={"mit_number": reg, "mi_number": serial, "rows": 20},
        sem=sem,
        description=f"aux certificate {reg}/{serial}",
    )
    items = ((data or {}).get("result") or {}).get("items") or []
    best: Mapping[str, Any] | None = None
    best_date = date.min
    for item in items:
        if not isinstance(item, Mapping):
            continue
        if not _clean(item.get("result_docnum")):
            continue
        valid = _parse_date_value(item.get("valid_date") or item.get("validDate"))
        if valid is None:
            continue
        if valid > best_date:
            best = item
            best_date = valid
    return best


def _entry(row: Any, reg: str, serial: str) -> dict[str, Any]:
    if row is None:
        return {
            "title": "",
            "modification": "",
            "manufacture_num": serial,
            "reg_number": reg,
            "certificate_no": "",
            "verification_date": "",
            "valid_to": "",
        }
    return {
        "title": row.title,
        "modification": row.modification,
        "manufacture_num": row.manufacture_num,
        "reg_number": row.reg_number,
        "certificate_no": row.certificate_no,
        "verification_date": row.verification_date,
        "valid_to": row.valid_to,
    }


async def resolve_auxiliary(
    session: AsyncSession,
    client: httpx.AsyncClient | None,
    *,
    requested_pairs: Sequence[tuple[str, str]],
    details: Mapping[str, Any],
    sem: Any = None,
) -> list[dict[str, Any]]:
    """Разрешить вспом. СИ с проверкой срока свидетельства и обновлением.

    Возвращает список записей для ``protocol_builder`` (кладётся в
    ``_resolved_auxiliary_instruments``).
    """
    repo = AuxiliaryInstrumentRepository(session)
    today = date.today()

    pairs = [(_clean(reg), _clean(serial)) for reg, serial in requested_pairs]
    pairs = [(reg, serial) for reg, serial in pairs if reg and serial]
    if not pairs:
        return []

    existing = await repo.find_by_pairs(pairs)
    entries: list[dict[str, Any]] = []

    for reg, serial in pairs:
        row = existing.get((reg, normalize_serial(serial)))
        expired = row is None or row.valid_to is None or row.valid_to < today

        if expired and client is not None:
            item = await _fetch_certificate(client, reg, serial, sem)
            if item is not None:
                fixture = _fixture_from_details(details, reg, serial) or {}
                title = (
                    (row.title if row is not None else None)
                    or _clean(fixture.get("mitypeTitle"))
                    or _clean(item.get("mit_title"))
                    or ""
                )
                modification = (
                    row.modification if row is not None else None
                ) or _clean(item.get("mi_modification")) or None
                try:
                    row = await repo.upsert_instrument(
                        reg_number=reg,
                        manufacture_num=serial,
                        values={
                            "title": title,
                            "modification": modification,
                            "certificate_no": _clean(item.get("result_docnum")) or None,
                            "verification_date": _parse_date_value(
                                item.get("verification_date") or item.get("verificationDate")
                            ),
                            "valid_to": _parse_date_value(
                                item.get("valid_date") or item.get("validDate")
                            ),
                        },
                    )
                except Exception as exc:  # сбой кэша не должен ронять генерацию
                    logger.warning(
                        "Auxiliary {} / {} certificate update failed: {}",
                        reg,
                        serial,
                        exc,
                    )

        entries.append(_entry(row, reg, serial))

    return entries
