from __future__ import annotations

import math
import re
from datetime import datetime, date
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.arshin_client import resolve_etalon_cert_from_details
from app.services.generators.base import FixedPctTol, GenInput
from app.services.generators.registry import get_by_template
from app.services.mappings import resolve_methodology, resolve_owner_and_inn
from app.services.templates import TEMPLATES, resolve_template_id
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


def _parse_range_and_unit(
    additional_info: str | None,
) -> tuple[float | None, float | None, str | None]:
    if not additional_info:
        return None, None, None
    txt = additional_info.strip()
    m = re.search(r"(-?\d+(?:[.,]\d+)?)\s*[-–]\s*(-?\d+(?:[.,]\d+)?)\s*\)?\s*(.+)?", txt)
    if not m:
        return None, None, None
    lo = float(m.group(1).replace(",", "."))
    hi = float(m.group(2).replace(",", "."))
    unit = _norm_unit((m.group(3) or "").strip())
    return lo, hi, unit or None


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


def _split_notation(notation: str) -> tuple[str, str]:
    if not notation:
        return "", ""
    parts = [p.strip() for p in notation.split(",")]
    first = parts[0] if parts else ""
    second = parts[1] if len(parts) > 1 else ""
    return first, second


async def build_context(
    *,
    excel_row: dict[str, Any],
    details: dict[str, Any],
    methodology_points: dict[str, str],
    owner_name: str,
    owner_inn: str | None,
    allowable_error: float,
    allowable_variation: float,
    protocol_number: str | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    methodology_points = dict(methodology_points or {})
    for key in ("p1", "p2", "p3", "p4"):
        methodology_points.setdefault(key, "")

    vri = details.get("vriInfo", {}) or {}
    mi_single = (details.get("miInfo", {}) or {}).get("singleMI") or {}
    means = details.get("means", {}) or {}
    mieta_list = means.get("mieta") or []

    # Даты
    vrf_date = vri.get("vrfDate")
    valid_date_arshin = vri.get("validDate")
    verification_date = _fmt_date_ddmmyyyy(excel_row.get("Дата поверки") or vrf_date or "")
    valid_to_date = _fmt_date_ddmmyyyy(excel_row.get("Действительно до") or valid_date_arshin or "")

    # Диапазон/единица
    range_min = range_max = None
    unit = None
    range_source = None

    rng_txt = (excel_row.get("Прочие сведения") or "").strip()
    if rng_txt:
        m = re.search(
            r"\(?\s*(-?\d+(?:[.,]\d+)?)\s*[-–]\s*(-?\d+(?:[.,]\d+)?)\s*\)?\s*(.+)$", rng_txt
        )
        if m:
            range_min = float(m.group(1).replace(",", "."))
            range_max = float(m.group(2).replace(",", "."))
            unit = _norm_unit(m.group(3))
            range_source = "excel"

    if range_min is None or range_max is None or not unit:
        lo, hi, u = _parse_range_and_unit((details.get("info") or {}).get("additional_info"))
        if lo is not None and hi is not None:
            range_min, range_max, unit = lo, hi, _norm_unit(u)
            range_source = range_source or "arshin"

    # Эталон (берём первый)
    et = mieta_list[0] if mieta_list else {}
    et_reg = et.get("regNumber") or ""
    et_mitype_num = et.get("mitypeNumber") or ""
    et_title = et.get("mitypeTitle") or ""
    notation_full = (et.get("notation") or "").strip()
    notation_first, notation_second = _split_notation(notation_full)
    et_mod = et.get("modification") or ""
    et_num = et.get("manufactureNum") or ""
    et_year = str(et.get("manufactureYear") or "")
    et_rank_code = et.get("rankCode") or ""
    et_rank_title = et.get("rankTitle") or ""
    et_schema = et.get("schemaTitle") or ""

    etalon_line = "; ".join(x for x in [et_reg, et_mitype_num, et_title, notation_full] if x)
    etalon_line_top = "; ".join(x for x in [et_reg, et_mitype_num, et_title, notation_first] if x)
    if notation_second:
        etalon_line_top = f"{etalon_line_top},"
    bottom_parts = [
        notation_second or "",
        et_mod,
        et_num,
        et_year,
        et_rank_code,
        et_rank_title,
        et_schema,
    ]
    etalon_line_bottom = "; ".join([x for x in bottom_parts if x])
    if etalon_line_bottom and not etalon_line_bottom.endswith(";"):
        etalon_line_bottom += ";"

    # Свидетельство эталона: из Excel кэш или авто-поиск
    et_cert = excel_row.get("_resolved_etalon_cert") or {}
    if not et_cert and http_client:
        try:
            et_cert = await resolve_etalon_cert_from_details(http_client, details)
        except Exception:
            et_cert = {}
    et_cert_line = (et_cert or {}).get("line")

    # Свидетельство поверяемого СИ
    device_cert_line = None
    if vri.get("applicable", {}).get("certNum") and valid_date_arshin:
        device_cert_line = (
            f"свидетельство о поверке № {vri['applicable']['certNum']}; "
            f"действительно до {valid_date_arshin};"
        )

    device_info = excel_row.get("Модификация") or mi_single.get("modification") or ""
    mitype_type = (mi_single.get("mitypeType") or "").strip()
    mitype_title = (mi_single.get("mitypeTitle") or "").strip()
    if mitype_title and mitype_type:
        device_info = f"{mitype_title} {mitype_type}"
    elif mitype_title and not device_info:
        device_info = mitype_title

    context: dict[str, Any] = {
        "device_info": device_info,
        "mitypeNumber": excel_row.get("Обозначение СИ") or mi_single.get("mitypeNumber") or "",
        "manufactureNum": excel_row.get("Заводской номер") or mi_single.get("manufactureNum") or "",
        "manufactureYear": str(
            excel_row.get("Год выпуска") or mi_single.get("manufactureYear") or ""
        ),
        "owner_name": owner_name,
        "owner_inn": owner_inn or "",
        "methodology_full": excel_row.get("_methodology_full") or vri.get("docTitle") or "",
        "methodology_points": methodology_points,
        "temperature": excel_row.get("Температура") or "",
        "pressure": excel_row.get("Давление") or "",
        "humidity": excel_row.get("Влажность") or "",
        "range_min": range_min,
        "range_max": range_max,
        "unit": unit,
        "range_source": range_source,
        "measurement_range": {"min": range_min, "max": range_max},
        "measurement_unit": unit,
        "etalon_line": etalon_line,
        "etalon_line_top": etalon_line_top,
        "etalon_line_bottom": etalon_line_bottom,
        "etalon_certificate": et_cert or None,
        "etalon_certificate_line": et_cert_line,
        "etalon_rank_code": et_rank_code or None,
        "etalon_rank_title": et_rank_title or None,
        "allowable_error_pct": allowable_error,
        "allowable_error_fmt": f"{allowable_error:.2f}",
        "allowable_variation_pct": allowable_variation,
        "verification_date": verification_date,
        "valid_to_date": valid_to_date,
        "verifier_name": excel_row.get("Поверитель") or "",
        "protocol_number": protocol_number,
        "device_certificate_line": device_cert_line,
    }

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
        cert_line_text = context.get("etalon_certificate_line") or ""
        base_line = str(context.get("etalon_line") or "").replace("\n", " ").strip(" ;")
        bottom_line = str(context.get("etalon_line_bottom") or "").replace("\n", " ").strip(" ;")

        parts: list[str] = []
        if base_line:
            parts.append(base_line)
        if bottom_line:
            parts.append(bottom_line)

        combined = "; ".join(parts)
        if cert_line_text:
            combined = f"{combined}; ({cert_line_text})" if combined else f"({cert_line_text})"

        context["etalon_line_combined"] = combined
        context["etalon_line_top"] = combined
        context["etalon_line_bottom"] = ""
        context["etalon_certificate_line"] = None

        method_full = (context.get("methodology_full") or "").strip()
        target_suffix = "МП 20-221-2021"
        if method_full and target_suffix in method_full:
            idx = method_full.find(target_suffix)
            core = method_full[:idx].strip()
            suffix = method_full[idx:].strip()
            if core and not core.startswith("\""):
                core = f'"{core}"'
            context["methodology_full"] = f"{core} {suffix}".strip()
        elif method_full and not method_full.startswith("\""):
            context["methodology_full"] = f'"{method_full}"'

    ver_dt = _parse_date(context.get("verification_date"))
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
    var_tol = FixedPctTol(float(tpl.get("allowable_variation_pct", allowable_variation)))

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
        if "allowable_note" in gout:
            context["allowable_note"] = gout["allowable_note"]

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
            excel_row.get("Владелец СИ") or (details.get("vriInfo", {}) or {}).get("miOwner") or ""
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
        allowable_hint: float | None = None

        if session and method_short:
            method_info = await resolve_methodology(session, method_short)
        else:
            method_info = None

        if method_info:
            excel_row["_methodology_full"] = method_info.title
            if method_info.points:
                methodology_points.update(method_info.points)
            allowable_hint = method_info.allowable_variation_pct
        else:
            excel_row["_methodology_full"] = method_short
            methodology_points = default_points.copy()

        try:
            allowable = float(
                str(excel_row.get("Другие параметры") or allowable_hint or "1.5").replace(",", ".")
            )
        except Exception:
            allowable = float(allowable_hint or 1.5)

        return await build_context(
            excel_row=excel_row,
            details=details,
            methodology_points=methodology_points,
            owner_name=owner_name,
            owner_inn=owner_inn or "",
            allowable_error=allowable,
            allowable_variation=allowable,
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
    return f"{sn}-б-{date_part}-1"


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
