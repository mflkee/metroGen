from __future__ import annotations

import math
import random
import re
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.arshin_client import resolve_etalon_certs_from_details
from app.services.generators.base import FixedPctTol, GenInput
from app.services.generators.registry import get_by_template
from app.services.mappings import resolve_methodology, resolve_owner_and_inn
from app.services.templates import TEMPLATES, resolve_template_id
from app.utils.paths import sanitize_filename
from app.utils.signatures import get_signature_render


def _norm_unit(s: str | None) -> str | None:
    if not s:
        return s
    t = s
    t = t.replace("кгc", "кгс").replace("КГC", "КГС")
    t = t.replace("кг/см²", "кгс/см²").replace("кг / см²", "кгс/см²")
    t = t.replace("см2", "см²")
    t = re.sub(r"\s+", " ", t).strip()
    return t


_RANGE_EXPR_RE = re.compile(
    r"""
    \(?\s*
    (?P<lo>[+-]?\d+(?:[.,]\d+)?)
    \s*(?:-|\.{2,})\s*
    (?P<hi>[+-]?\d+(?:[.,]\d+)?)
    \s*\)?\s*
    (?P<unit>.+)?
    """,
    re.VERBOSE,
)


def _normalized_range_text(value: str) -> str:
    text = value.replace("−", "-").replace("–", "-").replace("—", "-")
    text = text.replace("…", "..")
    text = re.sub(r"\bдо\b", "-", text, flags=re.IGNORECASE)
    return text


def _parse_range_text(text: str | None) -> tuple[float | None, float | None, str | None]:
    if not text:
        return None, None, None
    normalized = _normalized_range_text(text.strip())
    match = _RANGE_EXPR_RE.search(normalized)
    if not match:
        return None, None, None
    lo = float(match.group("lo").replace(",", "."))
    hi = float(match.group("hi").replace(",", "."))
    unit = _norm_unit((match.group("unit") or "").strip())
    return lo, hi, unit or None


def _parse_range_and_unit(
    additional_info: str | None,
) -> tuple[float | None, float | None, str | None]:
    return _parse_range_text(additional_info)


_DEFAULT_HEADER = {
    "company_name": (
        'Общество с ограниченной ответственностью "Многоцелевая Компания. Автоматизация. '
        'Исследования. Разработки"'
    ),
    "address": (
        "Ханты-Мансийский автономный округ - Югра, г.о. Нижневартовск, г Нижневартовск, "
        "ул Индустриальная, зд. 32, стр. 1, кабинет 14"
    ),
    "accreditation": (
        "Уникальный номер записи об аккредитации в реестре аккредитованных лиц №RA.RU.314356"
    ),
}

_HEADER_VARIANTS: tuple[dict[str, Any], ...] = (
    {
        "start": date(2023, 1, 1),
        "end": date(2023, 12, 31),
        "values": {
            "address": (
                "Ханты-Мансийский автономный округ - Югра, г.о. Нижневартовск, г "
                "Нижневартовск, ул. Индустриальная, дом 14, строение 11"
            )
        },
    },
)

_NAME_RNG: random.Random = random.SystemRandom()
_TRAINEE_ASSIGNMENTS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("чупин",), ("Большаков С.Н.", "Запевахин Т.Е.")),
    (("тиора",), ("Манджеев А.А.", "Кадыков П.Ю.")),
)
_TRAINEE_ORDER_NOTE = '(приказ о стажировке № 03-23-МС "09" января 2023г.)'


def _select_header(verification_dt: datetime | None) -> dict[str, str]:
    header = dict(_DEFAULT_HEADER)
    if not verification_dt:
        return header

    dt = verification_dt.date()
    for variant in _HEADER_VARIANTS:
        start: date | None = variant.get("start")
        end: date | None = variant.get("end")
        if start and dt < start:
            continue
        if end and dt > end:
            continue
        header.update(variant.get("values") or {})
        break
    return header


def _fmt_date_ddmmyyyy(s: object) -> str:
    """Возвращает дату в формате ДД.ММ.ГГГГ.

    Поддерживает входные значения:
      - datetime/date объекты
      - строки вида "ДД.ММ.ГГГГ", "ГГГГ-ММ-ДД", "ГГГГ-ММ-ДД HH:MM:SS", "ГГГГ-ММ-ДДTHH:MM:SS",
        а также "MM/DD/YYYY".
    В противном случае возвращает исходную строку.
    """
    if isinstance(s, datetime):
        return s.strftime("%d.%m.%Y")
    if isinstance(s, date):
        return s.strftime("%d.%m.%Y")

    txt = str(s or "").strip()
    if re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", txt):
        return txt

    # Популярные форматы, включая ISO с временем
    fmts = (
        "%d.%m.%Y",
        "%m/%d/%Y",
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    )
    for fmt in fmts:
        try:
            return datetime.strptime(txt, fmt).strftime("%d.%m.%Y")
        except Exception:
            continue

    # Если строка похожа на ISO, отрежем время и попробуем снова
    if re.match(r"^\d{4}-\d{2}-\d{2} ", txt):
        try:
            return datetime.strptime(txt[:10], "%Y-%m-%d").strftime("%d.%m.%Y")
        except Exception:
            pass

    return txt


def _fmt_date_ddmmyy(s: str) -> str:
    s = _fmt_date_ddmmyyyy(s or "")
    try:
        return datetime.strptime(s, "%d.%m.%Y").strftime("%d%m%y")
    except Exception:
        return ""


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(_fmt_date_ddmmyyyy(value), "%d.%m.%Y")
    except Exception:
        return None


def _normalize_person_tokens(value: str | None) -> set[str]:
    if not value:
        return set()
    lowered = str(value).lower().replace("ё", "е")
    cleaned = re.sub(r"[^0-9a-zа-я]+", " ", lowered, flags=re.UNICODE)
    return {token for token in cleaned.split() if token}


def _pick_trainee_name(
    verifier_name: str | None,
    verification_dt: datetime | None,
    template_id: str,
) -> str | None:
    if template_id != "pressure_common":
        return None
    if not verification_dt or verification_dt.year != 2023:
        return None

    tokens = _normalize_person_tokens(verifier_name)
    if not tokens:
        return None

    for key_tokens, candidates in _TRAINEE_ASSIGNMENTS:
        if set(key_tokens) <= tokens:
            return _NAME_RNG.choice(candidates)
    return None


def _split_notation(notation: str) -> tuple[str, str]:
    if not notation:
        return "", ""
    parts = [p.strip() for p in notation.split(",")]
    first = parts[0] if parts else ""
    second = parts[1] if len(parts) > 1 else ""
    return first, second


def _split_point_label(value: str) -> tuple[str, str]:
    text = (value or "").strip()
    if not text:
        return "", ""

    parts = re.split(r"\s*[–—-]\s*", text, maxsplit=1)
    if len(parts) == 2 and parts[0]:
        return parts[0].strip(), parts[1].strip()

    return text, ""


def _clean_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _first_nonempty(*values: Any) -> str:
    for value in values:
        text = _clean_str(value)
        if text:
            return text
    return ""


_ALLOWABLE_COLUMNS = ("Другие параметры", "КТ")


def _resolve_header_value(row: Mapping[str, Any], header: str) -> Any | None:
    """Return a cell value using case-insensitive header matching."""
    direct = row.get(header)
    if direct not in (None, ""):
        return direct

    target = header.casefold()
    for key, value in row.items():
        if not isinstance(key, str):
            continue
        if key.casefold() == target and value not in (None, ""):
            return value
    return None


def _raw_allowable_value(row: Mapping[str, Any]) -> Any | None:
    """Return the first non-empty allowable column resolved from an Excel row."""
    for column in _ALLOWABLE_COLUMNS:
        value = _resolve_header_value(row, column)
        if value not in (None, ""):
            return value
    return None


_ALLOWABLE_VALUE_RE = re.compile(r"-?\d+(?:[.,]\d+)?")


def _parse_allowable_value(candidate: Any, fallback: float) -> float:
    """Parse allowable tolerance from a cell or fall back to `fallback`."""
    if candidate not in (None, ""):
        if isinstance(candidate, int | float):
            return float(candidate)
        text = str(candidate).strip()
        if text:
            cleaned = text.replace("%", "").replace("‰", "").strip()
            match = _ALLOWABLE_VALUE_RE.search(cleaned)
            if match:
                number = match.group(0).replace(",", ".")
                try:
                    return float(number)
                except Exception:
                    pass
            cleaned = cleaned.replace(",", ".")
            try:
                return float(cleaned)
            except Exception:
                pass
    return fallback


def _format_allowable_str(value: float) -> str:
    return f"{float(value):.3f}".rstrip("0").rstrip(".")


def _display_allowable_value(source: Any, numeric: float) -> str:
    if source not in (None, ""):
        text = str(source).strip()
        if text:
            cleaned = text.replace("%", "").replace("‰", "").strip()
            if cleaned:
                return cleaned
    return _format_allowable_str(numeric)


_DEFAULT_POINT_DESCRIPTIONS = {
    1: "Результат внешнего осмотра",
    2: "Результат опробования",
    3: "Определение основной погрешности",
}

_OWNER_NAME_KEYS: tuple[str, ...] = (
    "Владелец СИ",
    "Владелец",
    "Организация",
    "owner_name",
)


def _fallback_point_description(position: int, idx: int) -> str:
    return _DEFAULT_POINT_DESCRIPTIONS.get(position) or _DEFAULT_POINT_DESCRIPTIONS.get(idx) or ""


def _owner_name_from_row(row: Mapping[str, Any]) -> str:
    for key in _OWNER_NAME_KEYS:
        value = row.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _etalon_sources(details: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    sources: list[Mapping[str, Any]] = []
    means = details.get("means") or {}
    if isinstance(means, Mapping):
        for entry in means.get("mieta") or []:
            if isinstance(entry, Mapping):
                sources.append(entry)
    eta = (details.get("miInfo") or {}).get("etaMI")
    if isinstance(eta, Mapping):
        sources.append(eta)
    return sources


def _build_etalon_entry(raw: Mapping[str, Any]) -> dict[str, Any]:
    et_reg = _clean_str(raw.get("regNumber"))
    et_mitype_num = _clean_str(raw.get("mitypeNumber"))
    et_title = _clean_str(raw.get("mitypeTitle"))
    notation_full = _clean_str(raw.get("notation"))
    notation_first, notation_second = _split_notation(notation_full)
    et_mod = _clean_str(raw.get("modification"))
    et_num = _clean_str(raw.get("manufactureNum"))
    et_year = _clean_str(raw.get("manufactureYear"))
    et_rank_code = _clean_str(raw.get("rankCode"))
    et_rank_title = _clean_str(raw.get("rankTitle"))
    et_schema = _clean_str(raw.get("schemaTitle"))

    line_top = "; ".join(x for x in [et_reg, et_mitype_num, et_title, notation_first] if x)
    if line_top and notation_second:
        line_top = f"{line_top},"
    line_bottom_parts = [
        notation_second or "",
        et_mod,
        et_num,
        et_year,
        et_rank_code,
        et_rank_title,
        et_schema,
    ]
    line_bottom = "; ".join(x for x in line_bottom_parts if x)
    if line_bottom and not line_bottom.endswith(";"):
        line_bottom = f"{line_bottom};"

    line_full = "; ".join(x for x in [et_reg, et_mitype_num, et_title, notation_full] if x)

    return {
        "reg_number": et_reg,
        "mitype_number": et_mitype_num,
        "mitype_title": et_title,
        "notation_full": notation_full,
        "notation_first": notation_first,
        "notation_second": notation_second,
        "modification": et_mod,
        "manufacture_num": et_num,
        "manufacture_year": et_year,
        "rank_code": et_rank_code,
        "rank_title": et_rank_title,
        "schema_title": et_schema,
        "line_full": line_full,
        "line_top": line_top,
        "line_bottom": line_bottom,
        "certificate_line": None,
        "certificate": None,
    }


def _match_certificate_for_entry(
    entry: Mapping[str, Any],
    certificates: list[Mapping[str, Any]],
    used_indices: set[int],
) -> Mapping[str, Any] | None:
    entry_serial = _clean_str(entry.get("manufacture_num"))
    entry_reg = _clean_str(entry.get("reg_number"))

    def _value_matches(cert: Mapping[str, Any], key: str, target: str | None) -> bool:
        if not target:
            return False
        value = _clean_str(cert.get(key))
        return value == target

    for idx, cert in enumerate(certificates):
        if idx in used_indices:
            continue
        if _value_matches(cert, "manufacture_num", entry_serial):
            used_indices.add(idx)
            return cert

    for idx, cert in enumerate(certificates):
        if idx in used_indices:
            continue
        if _value_matches(cert, "reg_number", entry_reg):
            used_indices.add(idx)
            return cert

    for idx, cert in enumerate(certificates):
        if idx not in used_indices:
            used_indices.add(idx)
            return cert
    return None


async def build_context(
    *,
    excel_row: dict[str, Any],
    details: dict[str, Any],
    methodology_points: dict[str, str],
    methodology_point_items: list[dict[str, Any]] | None = None,
    owner_name: str,
    owner_inn: str | None,
    allowable_error: float,
    allowable_variation: float,
    allowable_display: str | None = None,
    protocol_number: str | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    if owner_name and not (owner_inn or "").strip():
        raise ValueError(f"owner INN not found for '{owner_name}'")

    methodology_points = dict(methodology_points or {})
    point_items: list[dict[str, Any]] = []
    for idx, item in enumerate(methodology_point_items or [], start=1):
        if not isinstance(item, dict):
            continue
        raw_code = str(item.get("code") or methodology_points.get(f"p{idx}", "") or "").strip()
        code_value, label_description = _split_point_label(raw_code)
        description = str(item.get("description") or "").strip() or label_description
        position = int(item.get("position") or idx)
        point_type = str(item.get("point_type") or "clause").lower()
        if not description:
            description = _fallback_point_description(position, idx)
        point_items.append(
            {
                "position": position,
                "code": code_value,
                "description": description,
                "point_type": point_type,
            }
        )

    if not point_items:
        point_keys = sorted(
            (key for key in methodology_points if key.startswith("p")),
            key=lambda k: int(k[1:]) if k[1:].isdigit() else 0,
        )
        for idx, key in enumerate(point_keys, start=1):
            raw_label = str(methodology_points.get(key) or "").strip()
            code_value, description = _split_point_label(raw_label)
            methodology_points[key] = code_value
            fallback_pos = idx
            if key and key[1:].isdigit():
                fallback_pos = int(key[1:])
            if not description:
                description = _fallback_point_description(fallback_pos, idx)
            point_items.append(
                {
                    "position": idx,
                    "code": code_value,
                    "description": description,
                    "point_type": "clause",
                }
            )

    for key in ("p1", "p2", "p3", "p4"):
        methodology_points.setdefault(key, "")

    vri = details.get("vriInfo", {}) or {}
    mi_single = (details.get("miInfo", {}) or {}).get("singleMI") or {}

    # Даты
    vrf_date = vri.get("vrfDate")
    valid_date_arshin = vri.get("validDate")
    verification_date = _fmt_date_ddmmyyyy(excel_row.get("Дата поверки") or vrf_date or "")
    valid_to_date = _fmt_date_ddmmyyyy(excel_row.get("Действительно до") or valid_date_arshin or "")
    verification_dt = _parse_date(verification_date)

    # Диапазон/единица
    range_min = range_max = None
    unit = None
    range_source = None

    rng_txt = _clean_str(excel_row.get("Прочие сведения"))
    parsed_lo, parsed_hi, parsed_unit = _parse_range_text(rng_txt)
    if parsed_lo is not None and parsed_hi is not None:
        range_min = parsed_lo
        range_max = parsed_hi
        unit = parsed_unit
        range_source = "excel"

    if range_min is None or range_max is None or not unit:
        lo, hi, u = _parse_range_and_unit((details.get("info") or {}).get("additional_info"))
        if lo is not None and hi is not None:
            range_min, range_max, unit = lo, hi, _norm_unit(u)
            range_source = range_source or "arshin"

    # Эталоны: собираем все доступные источники
    raw_entries = [_build_etalon_entry(entry) for entry in _etalon_sources(details)]
    etalon_entries = [
        entry
        for entry in raw_entries
        if any(
            entry.get(key)
            for key in ("reg_number", "mitype_number", "mitype_title", "notation_full")
        )
    ]

    # Свидетельства эталонов: из Excel/кэша или авто-поиск
    resolved_certs = excel_row.get("_resolved_etalon_certs")
    etalon_certs: list[dict[str, Any]] = []
    if isinstance(resolved_certs, list):
        etalon_certs = [dict(item) for item in resolved_certs if isinstance(item, Mapping)]
    elif isinstance(resolved_certs, Mapping):
        etalon_certs = [dict(resolved_certs)]

    if not etalon_certs:
        single_cert = excel_row.get("_resolved_etalon_cert")
        if isinstance(single_cert, Mapping):
            etalon_certs = [dict(single_cert)]

    if not etalon_certs and http_client:
        try:
            etalon_certs = await resolve_etalon_certs_from_details(http_client, details)
            excel_row["_resolved_etalon_certs"] = etalon_certs
            if etalon_certs:
                excel_row["_resolved_etalon_cert"] = etalon_certs[0]
        except Exception:
            etalon_certs = []

    used_cert_indices: set[int] = set()
    for entry in etalon_entries:
        cert_match = _match_certificate_for_entry(entry, etalon_certs, used_cert_indices)
        if cert_match:
            entry["certificate"] = cert_match
            entry["certificate_line"] = cert_match.get("line")

    primary_entry = etalon_entries[0] if etalon_entries else {}
    etalon_line = primary_entry.get("line_full", "")
    etalon_line_top = primary_entry.get("line_top", "")
    etalon_line_bottom = primary_entry.get("line_bottom", "")
    et_rank_code = primary_entry.get("rank_code") or ""
    et_rank_title = primary_entry.get("rank_title") or ""
    primary_cert = primary_entry.get("certificate") or (etalon_certs[0] if etalon_certs else None)
    et_cert_line = primary_entry.get("certificate_line") or (primary_cert or {}).get("line")

    # Свидетельство поверяемого СИ
    device_cert_line = None
    if vri.get("applicable", {}).get("certNum") and valid_date_arshin:
        device_cert_line = (
            f"свидетельство о поверке № {vri['applicable']['certNum']}; "
            f"действительно до {valid_date_arshin};"
        )

    mitype_type = (mi_single.get("mitypeType") or "").strip()
    mitype_title = (mi_single.get("mitypeTitle") or "").strip()
    device_type_name = _first_nonempty(
        excel_row.get("Наименование типа СИ"),
        excel_row.get("Наименование СИ"),
        excel_row.get("Тип СИ"),
        excel_row.get("Тип"),
        mitype_title,
    )
    device_modification = _first_nonempty(
        excel_row.get("Модификация"),
        mi_single.get("modification"),
        mitype_type,
    )
    device_info_parts = [part for part in (device_type_name, device_modification) if part]
    device_info = ", ".join(device_info_parts)
    allowable_fmt = allowable_display or _format_allowable_str(allowable_error)

    context: dict[str, Any] = {
        "device_info": device_info,
        "device_type_name": device_type_name,
        "device_modification": device_modification,
        "mitypeNumber": excel_row.get("Обозначение СИ") or mi_single.get("mitypeNumber") or "",
        "manufactureNum": excel_row.get("Заводской номер") or mi_single.get("manufactureNum") or "",
        "manufactureYear": str(
            excel_row.get("Год выпуска") or mi_single.get("manufactureYear") or ""
        ),
        "owner_name": owner_name,
        "owner_inn": owner_inn or "",
        "methodology_full": excel_row.get("_methodology_full") or vri.get("docTitle") or "",
        "methodology_points": methodology_points,
        "methodology_point_items": point_items,
        "temperature": excel_row.get("Температура") or "",
        "pressure": excel_row.get("Давление") or "",
        "humidity": excel_row.get("Влажность") or "",
        "range_min": range_min,
        "range_max": range_max,
        "unit": unit,
        "range_source": range_source,
        "measurement_range": {"min": range_min, "max": range_max},
        "measurement_unit": unit,
        "etalon_entries": etalon_entries,
        "etalon_certificates": etalon_certs,
        "etalon_lines": [entry["line_full"] for entry in etalon_entries if entry.get("line_full")],
        "etalon_line": etalon_line,
        "etalon_line_top": etalon_line_top,
        "etalon_line_bottom": etalon_line_bottom,
        "etalon_certificate": primary_cert or None,
        "etalon_certificate_line": et_cert_line,
        "etalon_rank_code": et_rank_code or None,
        "etalon_rank_title": et_rank_title or None,
        "allowable_error_pct": allowable_error,
        "allowable_error_fmt": allowable_fmt,
        "allowable_variation_pct": allowable_variation,
        "verification_date": verification_date,
        "valid_to_date": valid_to_date,
        "verifier_name": excel_row.get("Поверитель") or "",
        "protocol_number": protocol_number,
        "device_certificate_line": device_cert_line,
    }
    context["allowable_variation"] = allowable_fmt

    header_info = _select_header(verification_dt)
    context["header"] = header_info
    context["header_name"] = header_info.get("company_name")
    context["header_address"] = header_info.get("address")
    context["header_accreditation"] = header_info.get("accreditation")

    # Выбор шаблона и генерация таблицы
    method_code = (excel_row.get("Методика поверки") or vri.get("docTitle") or "").strip()
    mitype_number = context["mitypeNumber"]
    mitype_title = (details.get("miInfo", {}) or {}).get("singleMI", {}).get("mitypeTitle") or ""

    template_id = resolve_template_id(method_code, mitype_number, mitype_title) or "pressure_common"
    tpl = TEMPLATES.get(template_id, {})
    context["template_id"] = template_id

    if template_id == "controller_43790_12":
        combined_device = " ".join(x for x in [mitype_title, mitype_type] if x).strip()
        if combined_device:
            context["device_info"] = combined_device
        entries = context.get("etalon_entries") or []
        combined_segments: list[str] = []
        if entries:
            for entry in entries:
                seg_parts = [
                    entry.get("line_top") or "",
                    entry.get("line_bottom") or "",
                    entry.get("certificate_line") or "",
                ]
                segment = "; ".join(part.strip(" ;") for part in seg_parts if part)
                if segment:
                    combined_segments.append(segment)
        else:
            base_line = str(context.get("etalon_line") or "").replace("\n", " ").strip(" ;")
            bottom_line = (
                str(context.get("etalon_line_bottom") or "").replace("\n", " ").strip(" ;")
            )
            cert_line_text = context.get("etalon_certificate_line") or ""
            parts: list[str] = []
            if base_line:
                parts.append(base_line)
            if bottom_line:
                parts.append(bottom_line)
            combined = "; ".join(parts)
            if cert_line_text:
                combined = f"{combined}; ({cert_line_text})" if combined else f"({cert_line_text})"
            if combined:
                combined_segments.append(combined)

        context["etalon_line_combined"] = " / ".join(combined_segments)
        if not entries:
            context["etalon_line_top"] = context["etalon_line_combined"]
            context["etalon_line_bottom"] = ""
            context["etalon_certificate_line"] = None

        method_full = (context.get("methodology_full") or "").strip()
        target_suffix = "МП 20-221-2021"
        if method_full and target_suffix in method_full:
            idx = method_full.find(target_suffix)
            core = method_full[:idx].strip()
            suffix = method_full[idx:].strip()
            if core and not core.startswith('"'):
                core = f'"{core}"'
            context["methodology_full"] = f"{core} {suffix}".strip()
        elif method_full and not method_full.startswith('"'):
            context["methodology_full"] = f'"{method_full}"'

    ver_dt = verification_dt
    val_dt = _parse_date(context.get("valid_to_date"))
    mpi_years: int | None = None
    if ver_dt and val_dt and val_dt >= ver_dt:
        days = max((val_dt - ver_dt).days, 0)
        if days == 0:
            mpi_years = 1
        else:
            mpi_years = max(1, math.ceil(days / 365))
    context["mpi_years"] = mpi_years

    points = int(excel_row.get("_points") or tpl.get("points", 8))
    err_tol = FixedPctTol(float(allowable_error))
    var_source = allowable_variation
    if var_source in (None, ""):
        var_source = tpl.get("allowable_variation_pct", allowable_error)
    var_tol = FixedPctTol(float(var_source))

    gen = get_by_template(template_id)
    if gen and range_min is not None and range_max is not None:
        gi = GenInput(
            range_min=float(range_min or 0.0),
            range_max=float(range_max or 0.0),
            unit=str(unit or ""),
            points=points,
            allowable_error=err_tol,
            allowable_variation=var_tol,
            ctx={
                "template_id": template_id,
                "method_code": method_code,
                "mitype_number": mitype_number,
                "mitype_title": mitype_title,
            },
        )
        gout = gen.generate(gi)
        context.update(
            {
                "table_rows": gout.get("rows", []),
                "unit": gout.get("unit_label") or context.get("unit") or "",
                "allowable_error_fmt": gout.get("allowable_error")
                or context["allowable_error_fmt"],
                "allowable_variation": gout.get("allowable_variation")
                or f"{float(context['allowable_variation_pct']):.2f}",
            }
        )
        if "point_groups" in gout:
            context["point_groups"] = gout.get("point_groups") or []
        if "allowable_note" in gout:
            context["allowable_note"] = gout["allowable_note"]
        for extra_key in (
            "r0_deviation_pct",
            "r0_allowable_pct",
            "w100_value",
            "w100_allowable",
        ):
            if extra_key in gout:
                context[extra_key] = gout[extra_key]

    trainee_name = _pick_trainee_name(
        context.get("verifier_name"),
        verification_dt,
        template_id,
    )
    context["trainee_name"] = trainee_name or ""
    context["trainee_sign_src"] = None
    context["trainee_sign_style"] = "display: none;"
    context["trainee_note"] = _TRAINEE_ORDER_NOTE if trainee_name else ""
    if trainee_name:
        trainee_signature = get_signature_render(trainee_name)
        if trainee_signature:
            context["trainee_sign_src"] = trainee_signature.src
            context["trainee_sign_style"] = trainee_signature.style

    signature = get_signature_render(context.get("verifier_name"))
    if signature:
        context["sign_src"] = signature.src
        context["sign_style"] = signature.style
    else:
        context["sign_src"] = None
        context["sign_style"] = "display: none;"

    return context


async def build_protocol_context(*args, **kwargs) -> dict[str, Any]:
    """
    Совместимо со старым вызовом: await build_protocol_context(row, details, client)
    и с новым: await build_protocol_context(excel_row=..., details=..., ...)
    """
    session: AsyncSession | None = kwargs.pop("session", None)

    if "excel_row" in kwargs:
        return await build_context(**kwargs)

    if len(args) >= 2 and not kwargs:
        excel_row: dict[str, Any] = dict(args[0] or {})
        details: dict[str, Any] = args[1] or {}
        http_client: httpx.AsyncClient | None = args[2] if len(args) >= 3 else None
        if session is None and len(args) >= 4:
            session = args[3]

        owner_name = (
            _owner_name_from_row(excel_row)
            or (details.get("vriInfo", {}) or {}).get("miOwner")
            or ""
        )
        owner_inn: str | None = None
        if session:
            resolved_name, resolved_inn = await resolve_owner_and_inn(session, owner_name)
            if resolved_name:
                owner_name = resolved_name
            owner_inn = resolved_inn

        method_short = (
            excel_row.get("Методика поверки")
            or (details.get("vriInfo", {}) or {}).get("docTitle")
            or ""
        ).strip()
        default_points = {"p1": "5.1", "p2": "5.2.3", "p3": "5.3", "p4": ""}
        methodology_points: dict[str, str] = default_points.copy()
        default_point_items = [
            {
                "position": 1,
                "code": "5.1",
                "description": "Результат внешнего осмотра",
                "point_type": "bool",
            },
            {
                "position": 2,
                "code": "5.2.3",
                "description": "Результат опробования",
                "point_type": "bool",
            },
            {
                "position": 3,
                "code": "5.3",
                "description": "Определение основной погрешности",
                "point_type": "clause",
            },
        ]
        methodology_point_items = [dict(item) for item in default_point_items]
        allowable_hint: float | None = None

        if session and method_short:
            method_info = await resolve_methodology(session, method_short)
        else:
            method_info = None

        if method_info:
            excel_row["_methodology_full"] = method_info.title
            if method_info.points:
                methodology_points.update(method_info.points)
            if method_info.point_items:
                methodology_point_items = [
                    {
                        "position": item.position,
                        "code": item.code,
                        "description": item.description or "",
                        "point_type": (item.point_type or "clause").lower(),
                    }
                    for item in method_info.point_items
                ]
            allowable_hint = method_info.allowable_variation_pct
        else:
            excel_row["_methodology_full"] = method_short
            methodology_points = default_points.copy()
            methodology_point_items = [dict(item) for item in default_point_items]

        raw_allowable = _raw_allowable_value(excel_row)
        candidate = raw_allowable if raw_allowable not in (None, "") else allowable_hint
        fallback = allowable_hint if allowable_hint not in (None, "") else 1.5
        allowable = _parse_allowable_value(candidate, float(fallback))
        allowable_display = _display_allowable_value(
            raw_allowable if raw_allowable not in (None, "") else candidate,
            allowable,
        )

        return await build_context(
            excel_row=excel_row,
            details=details,
            methodology_points=methodology_points,
            methodology_point_items=methodology_point_items,
            owner_name=owner_name,
            owner_inn=owner_inn or "",
            allowable_error=allowable,
            allowable_variation=allowable,
            allowable_display=allowable_display,
            protocol_number=None,
            http_client=http_client,
        )

    raise TypeError(
        "build_protocol_context: expected (excel_row, details[, client]) or keyword arguments"
    )


def suggest_filename(row: dict) -> str:
    sn = str(row.get("Заводской номер") or row.get("manufactureNum") or "").strip()
    date_raw = (
        row.get("Дата поверки") or row.get("verification_date") or row.get("verificationDate") or ""
    )
    date_part = _fmt_date_ddmmyy(str(date_raw))
    candidate = f"{sn}-б-{date_part}-1".strip("-")
    return sanitize_filename(candidate, default="protocol")


def _initials3(full_name: str | None) -> str:
    """Возвращает 3 буквы инициалов (Ф+И+О), например:
    "Большаков С Н" → "БСН", "Иванов И.И." → "ИИИ".
    Берём первую букву первой части (фамилии) и по одной букве из следующих частей.
    """
    if not full_name:
        return ""
    # Убираем точки/лишние пробелы
    cleaned = re.sub(r"[.]+", " ", str(full_name)).strip()
    parts = [p for p in re.split(r"\s+", cleaned) if p]
    if not parts:
        return ""
    letters: list[str] = []
    # Первая буква фамилии
    letters.append(parts[0][0])
    # Первая буква каждого из последующих компонентов
    for p in parts[1:]:
        if p:
            letters.append(p[0])
        if len(letters) >= 3:
            break
    # Если частей меньше трёх, просто вернём что есть
    return "".join(letters).upper()


def _fmt_date_ddmmyyyy_no_dots(s: str | None) -> str:
    """Дата формата ДДММГГГГ без разделителей.
    Принимает строки вида "15.01.2025", "2025-01-15" и т.п.
    """
    if not s:
        return ""
    human = _fmt_date_ddmmyyyy(str(s))  # ДД.ММ.ГГГГ
    try:
        dt = datetime.strptime(human, "%d.%m.%Y")
        return dt.strftime("%d%m%Y")
    except Exception:
        # Если не распарсилось — просто уберём точки
        return human.replace(".", "")


def make_protocol_number(verifier_name: str | None, verification_date: str | None, seq: int) -> str:
    """Строит номер протокола вида: ИНИ/ДДММГГ/N (дата без разделителей, 6 знаков).

    Пример: Большаков С Н, 15.01.2025, 1 → "БСН/150125/1".
    """
    ini = _initials3(verifier_name)
    d = _fmt_date_ddmmyy(verification_date or "")
    seq_part = max(int(seq or 1), 1)
    return f"{ini}/{d}/{seq_part}"
