"""Локальный справочник эталонов с ленивым заполнением из Аршина (cache-aside).

Идея
----
Во входном Excel (колонка «СИ, применяемые в качестве эталона») эталоны заданы
своим ФИФ-номером, например ``77090.19.2Р.00761949`` — это поле ``regNumber``
в ответе Аршина (``miInfo.etaMI`` / ``means.mieta``). Тот же ответ Аршина
содержит и все данные эталона (тип, модификация, зав. номер, год, разряд) и
его свидетельство.

Схема работы:

* первый раз эталон берётся прямо из ``details`` прибора и сохраняется в БД
  (``etalon_devices`` + ``etalon_certifications``) — без дополнительных запросов;
* далее эталон читается из БД;
* если свидетельство в БД просрочено (``valid_to < today``) или отсутствует —
  свидетельство обязательно перезапрашивается в Аршине и обновляется в БД;
* карточка эталона обновляется, если Аршин вернул более свежие данные.

Так повторные генерации не дёргают Аршин по каждому эталону, но просроченные
эталоны всегда перепроверяются.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any

import httpx
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import EtalonCertification, EtalonDevice
from app.db.repositories import EtalonRepository
from app.services.arshin_client import resolve_etalon_certs_from_details

__all__ = ("resolve_etalons",)


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _as_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _iter_etalon_sources(details: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Эталоны из ответа Аршина по прибору: ``means.mieta`` и ``miInfo.etaMI``."""
    sources: list[Mapping[str, Any]] = []

    means = details.get("means") or {}
    if isinstance(means, Mapping):
        for item in means.get("mieta") or []:
            if isinstance(item, Mapping):
                sources.append(item)

    eta = (details.get("miInfo") or {}).get("etaMI")
    if isinstance(eta, Mapping):
        sources.append(eta)

    return sources


def _device_values(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "mitype_number": _clean(source.get("mitypeNumber")) or None,
        "title": _clean(source.get("mitypeTitle")) or None,
        "notation": _clean(source.get("notation") or source.get("mitypeType")) or None,
        "modification": _clean(source.get("modification")) or None,
        "manufacture_year": _as_int(source.get("manufactureYear")),
        "rank_code": _clean(source.get("rankCode")) or None,
        "rank_title": _clean(source.get("rankTitle")) or None,
        "schema_title": _clean(source.get("schemaTitle")) or None,
        "payload": dict(source),
    }


def _mieta_from_device(device: EtalonDevice) -> dict[str, Any]:
    """Представление эталона в форме записи Аршина (mieta) для protocol_builder."""
    return {
        "regNumber": device.reg_number,
        "mitypeNumber": device.mitype_number,
        "mitypeTitle": device.title,
        "notation": device.notation,
        "mitypeType": device.notation,
        "modification": device.modification,
        "manufactureNum": device.manufacture_num,
        "manufactureYear": device.manufacture_year,
        "rankCode": device.rank_code,
        "rankTitle": device.rank_title,
        "schemaTitle": device.schema_title,
    }


def _cert_entry(
    cert: EtalonCertification, device: EtalonDevice
) -> dict[str, Any]:
    line = f"свидетельство о поверке № {cert.certificate_no}"
    if cert.verification_date:
        line = f"{line} от {cert.verification_date:%d.%m.%Y}г."
    if cert.valid_to:
        line = f"{line}; действительно до {cert.valid_to:%d.%m.%Y}г."
    else:
        line = f"{line};"

    return {
        "docnum": cert.certificate_no,
        "verification_date": (
            cert.verification_date.strftime("%d.%m.%Y") if cert.verification_date else ""
        ),
        "valid_date": cert.valid_to.strftime("%d.%m.%Y") if cert.valid_to else "",
        "line": line,
        "reg_number": device.reg_number,
        "manufacture_num": device.manufacture_num,
        "mitype_number": device.mitype_number,
    }


def _is_valid(cert: EtalonCertification, today: date) -> bool:
    return cert.valid_to is not None and cert.valid_to >= today


async def _refresh_certificates(
    repo: EtalonRepository,
    client: httpx.AsyncClient | None,
    device: EtalonDevice,
    sem: Any,
) -> None:
    """Перезапросить свидетельства эталона в Аршине и сохранить их.

    Используются уже сохранённые в карточке ``mitype_number`` и ``manufacture_num``,
    поэтому доступ к прибору (его ``details``) не нужен.
    """
    if client is None:
        return
    if not device.mitype_number or not device.manufacture_num:
        logger.warning(
            "Etalon {}: cannot refresh certificate, mitype_number/manufacture_num missing",
            device.reg_number,
        )
        return

    synthetic_details = {"means": {"mieta": [_mieta_from_device(device)]}}
    try:
        resolved = await resolve_etalon_certs_from_details(
            client,
            synthetic_details,
            sem=sem,
            preferred_reg_numbers=[device.reg_number],
        )
    except Exception as exc:  # network/parse errors не должны ронять генерацию
        logger.warning(
            "Etalon {}: Arshin certificate refresh failed: {}", device.reg_number, exc
        )
        return

    if not resolved:
        logger.info(
            "Etalon {}: Arshin has no fresh certificate for this device", device.reg_number
        )
        return

    for item in resolved:
        cert_no = _clean(item.get("docnum"))
        if not cert_no:
            continue
        await repo.upsert_certification(
            device=device,
            certificate_no=cert_no,
            values={
                "verification_date": _parse_date(item.get("verification_date")),
                "valid_to": _parse_date(item.get("valid_date")),
                "source": "arshin",
                "payload": dict(item),
            },
        )


async def resolve_etalons(
    session: AsyncSession,
    client: httpx.AsyncClient | None,
    *,
    requested_codes: Sequence[str],
    details: Mapping[str, Any],
    sem: Any = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Разрешить эталоны по кодам из входного файла с локальным кэшем.

    Возвращает ``(device_entries, certificate_entries)``:

    * ``device_entries`` — список записей в форме Аршина (mieta), который
      ожидает ``protocol_builder`` (кладётся в ``_resolved_etalon_devices``);
    * ``certificate_entries`` — список свидетельств (кладётся в
      ``_resolved_etalon_certs``).
    """
    repo = EtalonRepository(session)
    today = date.today()

    sources: dict[str, Mapping[str, Any]] = {}
    for source in _iter_etalon_sources(details):
        code = _clean(source.get("regNumber"))
        if code and code not in sources:
            sources[code] = source

    device_entries: list[dict[str, Any]] = []
    certificate_entries: list[dict[str, Any]] = []
    seen: set[str] = set()

    for raw_code in requested_codes:
        code = _clean(raw_code)
        if not code or code in seen:
            continue
        seen.add(code)

        source = sources.get(code)
        device = await repo.get_by_code(code)

        if device is None:
            if source is None:
                logger.warning(
                    "Etalon {} is absent both in DB and in Arshin details", code
                )
                continue
            device = await repo.upsert_device_by_code(
                code=code,
                manufacture_num=_clean(source.get("manufactureNum")) or None,
                values=_device_values(source),
            )
        elif source is not None:
            # Аршин дал более свежие данные по эталону — обновляем карточку
            device = await repo.upsert_device_by_code(
                code=code,
                manufacture_num=_clean(source.get("manufactureNum"))
                or device.manufacture_num,
                values=_device_values(source),
            )

        certs = await repo.list_certifications(device.id)
        if not any(_is_valid(cert, today) for cert in certs):
            await _refresh_certificates(repo, client, device, sem)
            certs = await repo.list_certifications(device.id)

        chosen = certs[0] if certs else None
        device_entries.append(_mieta_from_device(device))
        if chosen is not None:
            certificate_entries.append(_cert_entry(chosen, device))

    return device_entries, certificate_entries
