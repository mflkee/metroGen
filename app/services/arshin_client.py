# app/services/arshin_client.py
from __future__ import annotations

import asyncio
import re
from datetime import date, datetime
from typing import Any

import httpx

from app.services.cache import arshin_cache

# Важно: этот BASE дергается в тестах!
ARSHIN_BASE = "https://fgis.gost.ru/fundmetrology/eapi"


# ─────────────────────────── helpers ───────────────────────────


def _safe_get(d: dict[str, Any], path: list[str], default: Any = None) -> Any:
    cur = d
    for k in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def guess_year_from_cert(cert: str) -> int | None:
    """
    Извлекаем год из номера свидетельства:
    'С-ВЯ/15-01-2025/402123271' → 2025
    """
    m = re.search(r"/(\d{2})-(\d{2})-(\d{4})/", cert)
    if m:
        return int(m.group(3))
    return None


def _fmt_date_ddmmyyyy(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, datetime | date):
        return value.strftime("%d.%m.%Y")

    txt = str(value).strip()
    try:
        return datetime.fromisoformat(txt.replace("Z", "")).strftime("%d.%m.%Y")
    except Exception:
        pass

    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d.%m.%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(txt, fmt).strftime("%d.%m.%Y")
        except Exception:
            continue
    return txt


def _split_first_notation(s: str) -> str:
    """
    'ЭЛМЕТРО-Паскаль-04, Паскаль-04' → 'ЭЛМЕТРО-Паскаль-04'
    """
    if not s:
        return ""
    return s.split(",")[0].strip()


# ─────────────────────────── core fetchers ───────────────────────────


async def fetch_vri_id_by_certificate(
    client: httpx.AsyncClient,
    cert: str,
    year: int | None = None,
    sem: asyncio.Semaphore | None = None,
    use_cache: bool = True,
) -> str | None:
    """
    Возвращает vri_id по номеру свидетельства.
    Тесты мокают GET {ARSHIN_BASE}/vri (без учёта query),
    поэтому здесь не критично, какие параметры мы реально передадим.
    """
    params = {"result_docnum": cert}
    if year:
        params["year"] = str(year)

    cache_key = ("vri", tuple(sorted(params.items())))
    if use_cache:
        cached = arshin_cache.get(cache_key)
        if cached is not None:
            return cached

    if sem:
        async with sem:
            resp = await client.get(f"{ARSHIN_BASE}/vri", params=params)
    else:
        resp = await client.get(f"{ARSHIN_BASE}/vri", params=params)
    resp.raise_for_status()
    data = resp.json() or {}
    items = _safe_get(data, ["result", "items"], default=[])
    if not items:
        return None
    first = items[0] or {}
    vri_id = first.get("vri_id")
    if vri_id and use_cache:
        arshin_cache.set(cache_key, vri_id)
    return vri_id


async def fetch_vri_details(
    client: httpx.AsyncClient,
    vri_id: str,
    sem: asyncio.Semaphore | None = None,
) -> dict[str, Any]:
    """
    Возвращает payload с ключом 'result' по vri_id.
    """
    if sem:
        async with sem:
            resp = await client.get(f"{ARSHIN_BASE}/vri/{vri_id}")
    else:
        resp = await client.get(f"{ARSHIN_BASE}/vri/{vri_id}")
    resp.raise_for_status()
    data = resp.json() or {}
    return data.get("result") or {}


# ─────────────────────────── details utils ───────────────────────────


def compose_etalon_line_from_details(details: dict[str, Any]) -> str:
    """
    Строка эталона в коротком формате:
    'регномер; обозначение; наименование; первая_часть_обозначения_типа'

    Поддерживает 2 варианта источника:
      - details['miInfo']['etaMI']  (как в тестах)
      - details['means']['mieta'][0] (как в реальных ответах Аршина)
    """
    eta = _safe_get(details, ["miInfo", "etaMI"], {})
    reg = eta.get("regNumber")
    mitype_num = eta.get("mitypeNumber")
    mitype_title = eta.get("mitypeTitle")
    notation_src = eta.get("mitypeType")

    if not reg:
        mieta_list = _safe_get(details, ["means", "mieta"], [])
        if mieta_list:
            m = mieta_list[0] or {}
            reg = m.get("regNumber", reg)
            mitype_num = m.get("mitypeNumber", mitype_num)
            mitype_title = m.get("mitypeTitle", mitype_title)
            notation_src = m.get("notation", notation_src)

    notation_first = _split_first_notation(notation_src or "")
    parts = [p for p in [reg, mitype_num, mitype_title, notation_first] if p]
    return "; ".join(parts)


def extract_detail_fields(details: dict[str, Any]) -> dict[str, Any]:
    """
    Выжимка, на которую опираются проверки:
      - organization
      - vrfDate
      - validDate
      - applicable (bool по наличию certNum)
    """
    vri = details.get("vriInfo", {}) or {}
    org = vri.get("organization") or ""
    vrf_date = vri.get("vrfDate")
    valid_date = vri.get("validDate")
    applicable = bool(_safe_get(vri, ["applicable", "certNum"]))
    return {
        "organization": org,
        "vrfDate": vrf_date,
        "validDate": valid_date,
        "applicable": applicable,
    }


# ─────────────────────────── etalon certificate resolver ───────────────────────────


async def resolve_etalon_cert_from_details(
    client: httpx.AsyncClient,
    details: dict[str, Any],
    sem: asyncio.Semaphore | None = None,
) -> dict[str, str] | None:
    """
    Автопоиск свидетельства эталона:
    GET /vri?mit_number=...&mit_title=...&mi_modification=...&mi_number=...

    Возвращает:
      {
        "docnum": "...",
        "verification_date": "ДД.ММ.ГГГГ",
        "valid_date": "ДД.ММ.ГГГГ",
        "line": "свидетельство о поверке № <docnum>; действительно до <valid_date>;"
      }
    либо None, если не найдено/недостаточно данных.
    """
    # Берём эталон либо из miInfo.etaMI, либо из means.mieta[0]
    candidates: list[dict[str, Any]] = []
    primary = _safe_get(details, ["means", "mieta"], []) or []
    if primary:
        candidates.extend([(item or {}).copy() for item in primary])

    eta = _safe_get(details, ["miInfo", "etaMI"], {}) or {}
    if eta:
        candidates.append(eta.copy())

    if not candidates:
        return None

    async def _query(params: dict[str, str]) -> dict[str, str] | None:
        cache_key = ("eta_cert_v2", tuple(sorted((str(k), str(v)) for k, v in params.items())))
        cached = arshin_cache.get(cache_key)
        if cached is not None:
            return cached

        if sem:
            async with sem:
                resp = await client.get(f"{ARSHIN_BASE}/vri", params=params)
        else:
            resp = await client.get(f"{ARSHIN_BASE}/vri", params=params)
        resp.raise_for_status()
        data = resp.json() or {}
        items = _safe_get(data, ["result", "items"], default=[]) or []
        if not items:
            return None

        for it in items:
            if not isinstance(it, dict):
                continue
            cert = it.get("result_docnum")
            valid_date_raw = it.get("valid_date") or it.get("validDate")
            if not (cert and valid_date_raw):
                continue
            vrf_date_raw = it.get("verification_date") or it.get("verificationDate")
            vrf_date = _fmt_date_ddmmyyyy(vrf_date_raw)
            valid_date = _fmt_date_ddmmyyyy(valid_date_raw)

            base_line = f"свидетельство о поверке № {cert}"
            if vrf_date:
                base_line = f"{base_line} от {vrf_date}г."
            line = f"{base_line}; действительно до {valid_date}г."
            result = {
                "docnum": cert,
                "verification_date": vrf_date,
                "valid_date": valid_date,
                "line": line,
            }
            arshin_cache.set(cache_key, result)
            return result

        return None

    for entry in candidates:
        mit_number = str(entry.get("mitypeNumber") or "").strip()
        mi_number = str(entry.get("manufactureNum") or "").strip()
        if not (mit_number and mi_number):
            continue

        base_params: dict[str, str] = {
            "mit_number": mit_number,
            "mi_number": mi_number,
        }
        mit_title = str(entry.get("mitypeTitle") or "").strip()
        if mit_title:
            base_params["mit_title"] = mit_title
        mi_mod = str(entry.get("modification") or "").strip()
        if mi_mod:
            base_params["mi_modification"] = mi_mod
        notation = str(entry.get("notation") or "").strip()
        if notation:
            base_params["mit_notation"] = notation

        manufacture_year = entry.get("manufactureYear")
        candidate_params: list[dict[str, str]] = []
        if manufacture_year:
            candidate_params.append({**base_params, "year": str(manufacture_year)})
        candidate_params.append(dict(base_params))

        # Optionally try guessed year from device certificate if available
        cert_num = _safe_get(details, ["vriInfo", "applicable", "certNum"], "")
        guessed_year = guess_year_from_cert(cert_num)
        if guessed_year and guessed_year != manufacture_year:
            candidate_params.insert(0, {**base_params, "year": str(guessed_year)})

        seen_queries: set[tuple[tuple[str, str], ...]] = set()
        for params in candidate_params:
            key = tuple(sorted((str(k), str(v)) for k, v in params.items()))
            if key in seen_queries:
                continue
            seen_queries.add(key)
            result = await _query(params)
            if result:
                return result

    return None


# Алиас для совместимости со старым импортом в protocols.py
# (Теперь и старое имя, и новое работают одинаково.)
async def find_etalon_certificate(
    client: httpx.AsyncClient,
    details: dict[str, Any],
    sem: asyncio.Semaphore | None = None,
) -> dict[str, str] | None:
    return await resolve_etalon_cert_from_details(client, details, sem=sem)
