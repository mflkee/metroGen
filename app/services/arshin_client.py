# app/services/arshin_client.py
from __future__ import annotations

import asyncio
import random
import re
from datetime import date, datetime
from typing import Any

import httpx
from loguru import logger

from app.core.config import settings
from app.services.cache import arshin_cache

# Важно: этот BASE дергается в тестах!
ARSHIN_BASE = "https://fgis.gost.ru/fundmetrology/eapi"


# ─────────────────────────── helpers ───────────────────────────

_RETRY_STATUS_CODES = {429, 500, 502, 503, 504}


def _exc_brief(exc: Exception) -> str:
    text = str(exc).strip()
    if not text:
        return f"{exc.__class__.__name__}"
    return f"{exc.__class__.__name__}: {text}"


async def _request_json(
    client: httpx.AsyncClient,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    sem: asyncio.Semaphore | None = None,
    description: str,
) -> dict[str, Any]:
    attempts = 1 if settings.ARSHIN_FAST_FAIL else max(settings.ARSHIN_RETRY_ATTEMPTS, 1)
    backoff = max(settings.ARSHIN_RETRY_BACKOFF_BASE, 0.1)
    max_backoff = max(settings.ARSHIN_RETRY_BACKOFF_MAX, backoff)
    jitter = max(settings.ARSHIN_RETRY_JITTER, 0.0)

    for attempt in range(1, attempts + 1):
        try:
            if sem:
                async with sem:
                    response = await client.get(url, params=params)
            else:
                response = await client.get(url, params=params)

            if response.status_code in _RETRY_STATUS_CODES:
                raise httpx.HTTPStatusError(
                    f"retryable status {response.status_code}",
                    request=response.request,
                    response=response,
                )

            response.raise_for_status()
            payload = response.json()
            return payload if isinstance(payload, dict) else {}
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code if exc.response else None
            if status not in _RETRY_STATUS_CODES or attempt == attempts:
                logger.error(
                    "Arshin request failed (status={}) on attempt {}/{} for {}: {}",
                    status,
                    attempt,
                    attempts,
                    description,
                    _exc_brief(exc),
                )
                raise
            logger.warning(
                "Retryable Arshin status {} for {} (attempt {}/{})",
                status,
                description,
                attempt,
                attempts,
            )
        except httpx.RequestError as exc:
            if attempt == attempts:
                logger.error(
                    "Arshin transport error on attempt {}/{} for {}: {}",
                    attempt,
                    attempts,
                    description,
                    _exc_brief(exc),
                )
                raise
            logger.warning(
                "Retrying Arshin transport error for {} (attempt {}/{}): {}",
                description,
                attempt,
                attempts,
                _exc_brief(exc),
            )

        delay = min(backoff, max_backoff) + (random.uniform(0, jitter) if jitter else 0.0)
        await asyncio.sleep(delay)
        backoff = min(backoff * 2, max_backoff)

    return {}


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


def _parse_date_value(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value if not isinstance(value, datetime) else value.date()
    txt = str(value).strip()
    try:
        return datetime.fromisoformat(txt.replace("Z", "")).date()
    except Exception:
        pass
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d.%m.%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(txt, fmt).date()
        except Exception:
            continue
    return None


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
    # Для архивных поверок (например, 2023 г.) Arshin иногда требует явный год в query,
    # иначе возвращает пустой список. Собираем возможные варианты параметров:
    #   1) явный year из аргумента,
    #   2) год, угаданный из номера свидетельства,
    #   3) запрос без year (исторически работал для свежих записей).
    param_candidates: list[dict[str, str]] = []
    seen: set[tuple[tuple[str, str], ...]] = set()

    def _push(params: dict[str, str]) -> None:
        key = tuple(sorted(params.items()))
        if key not in seen:
            seen.add(key)
            param_candidates.append(params)

    base_params = {"result_docnum": cert}
    if year:
        _push({**base_params, "year": str(year)})
    else:
        guessed = guess_year_from_cert(cert)
        if guessed:
            _push({**base_params, "year": str(guessed)})
    _push(base_params)

    for params in param_candidates:
        cache_key = ("vri", tuple(sorted(params.items())))
        if use_cache:
            cached = arshin_cache.get(cache_key)
            if cached is not None:
                return cached

        data = await _request_json(
            client,
            f"{ARSHIN_BASE}/vri",
            params=params,
            sem=sem,
            description=f"vri lookup cert={cert}",
        )
        items = _safe_get(data, ["result", "items"], default=[])
        if not items:
            continue
        first = items[0] or {}
        vri_id = first.get("vri_id")
        if vri_id and use_cache:
            arshin_cache.set(cache_key, vri_id)
        if vri_id:
            return vri_id

    return None


async def fetch_vri_details(
    client: httpx.AsyncClient,
    vri_id: str,
    sem: asyncio.Semaphore | None = None,
) -> dict[str, Any]:
    """
    Возвращает payload с ключом 'result' по vri_id.
    """
    data = await _request_json(
        client,
        f"{ARSHIN_BASE}/vri/{vri_id}",
        sem=sem,
        description=f"vri details vri_id={vri_id}",
    )
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
    certs = await resolve_etalon_certs_from_details(client, details, sem=sem)
    return certs[0] if certs else None


def _iter_etalon_sources(details: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all eta sources from details (means.mieta + miInfo.etaMI)."""
    candidates: list[dict[str, Any]] = []
    primary = _safe_get(details, ["means", "mieta"], []) or []
    for item in primary:
        if isinstance(item, dict):
            candidates.append(item.copy())

    eta = _safe_get(details, ["miInfo", "etaMI"], {}) or {}
    if eta:
        candidates.append(dict(eta))
    return candidates


async def resolve_etalon_certs_from_details(
    client: httpx.AsyncClient,
    details: dict[str, Any],
    sem: asyncio.Semaphore | None = None,
) -> list[dict[str, str]]:
    """
    Автопоиск свидетельств эталонов:
    GET /vri?mit_number=...&mit_title=...&mi_modification=...&mi_number=...

    Возвращает:
      [
        {
          "docnum": "...",
          "verification_date": "ДД.ММ.ГГГГ",
          "valid_date": "ДД.ММ.ГГГГ",
          "line": "...",
          "reg_number": "...",
          "manufacture_num": "...",
          "mitype_number": "...",
        },
        ...
      ]
    либо пустой список, если ничего не найдено.
    """
    candidates = _iter_etalon_sources(details)
    if not candidates:
        return []

    results: list[dict[str, str]] = []

    async def _query(params: dict[str, str]) -> dict[str, str] | None:
        cache_key = ("eta_cert_v3", tuple(sorted((str(k), str(v)) for k, v in params.items())))
        cached = arshin_cache.get(cache_key)
        if cached is not None:
            return cached

        items_all: list[dict[str, Any]] = []
        start = 0
        rows = 100
        max_total = 1000

        while True:
            page_params = dict(params)
            page_params.setdefault("rows", rows)
            page_params["start"] = start

            data = await _request_json(
                client,
                f"{ARSHIN_BASE}/vri",
                params=page_params,
                sem=sem,
                description=f"etalon certificate lookup params={params}",
            )
            items = _safe_get(data, ["result", "items"], default=[]) or []
            items_all.extend(items)

            total = _safe_get(data, ["result", "count"], default=len(items_all)) or len(items_all)
            start += rows

            if start >= total or not items or len(items_all) >= max_total:
                break

        if not items_all:
            return None

        candidates: list[dict[str, Any]] = []

        for it in items_all:
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
            valid_dt = _parse_date_value(valid_date_raw)
            vrf_dt = _parse_date_value(vrf_date_raw)
            candidates.append(
                {
                    "docnum": cert,
                    "verification_date": vrf_date,
                    "valid_date": valid_date,
                    "line": line,
                    "_valid_dt": valid_dt,
                    "_vrf_dt": vrf_dt,
                }
            )

        if not candidates:
            return None

        def _score(item: dict[str, Any]) -> tuple[date, date]:
            valid_dt = item.get("_valid_dt") or item.get("_vrf_dt") or date.min
            vrf_dt = item.get("_vrf_dt") or date.min
            return valid_dt, vrf_dt

        best = max(candidates, key=_score)
        best.pop("_valid_dt", None)
        best.pop("_vrf_dt", None)
        arshin_cache.set(cache_key, best)
        return best

    seen_queries: set[tuple[tuple[str, str], ...]] = set()

    for entry in candidates:
        reg_number = str(entry.get("regNumber") or "").strip()
        mit_number = str(entry.get("mitypeNumber") or "").strip()
        mi_number = str(entry.get("manufactureNum") or "").strip()
        if not (mit_number and mi_number):
            continue

        entry_candidates: list[dict[str, Any]] = []

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

        # Build param variants with different optional filters to avoid missing records
        optional_fields = [
            ("mit_title", base_params.get("mit_title")),
            ("mi_modification", base_params.get("mi_modification")),
            ("mit_notation", base_params.get("mit_notation")),
        ]

        mandatory_params = {"mit_number": mit_number, "mi_number": mi_number}
        param_variants: list[dict[str, str]] = []

        # All combinations of optional fields (0..2^n - 1)
        for mask in range(1 << len(optional_fields)):
            params = dict(mandatory_params)
            for idx, (key, value) in enumerate(optional_fields):
                if not value:
                    continue
                if mask & (1 << idx):
                    params[key] = value
            param_variants.append(params)

        # Add year variants
        manufacture_year = entry.get("manufactureYear")
        year_candidates: list[int | None] = [None]
        if manufacture_year:
            year_candidates.append(int(manufacture_year))
        cert_num = _safe_get(details, ["vriInfo", "applicable", "certNum"], "")
        guessed_year = guess_year_from_cert(cert_num)
        if guessed_year and guessed_year != manufacture_year:
            year_candidates.append(guessed_year)

        candidate_params: list[dict[str, str]] = []
        seen_queries: set[tuple[tuple[str, str], ...]] = set()
        for base in param_variants:
            for year in year_candidates:
                params = dict(base)
                if year:
                    params["year"] = str(year)
                key = tuple(sorted((str(k), str(v)) for k, v in params.items()))
                if key in seen_queries:
                    continue
                seen_queries.add(key)
                candidate_params.append(params)

        for params in candidate_params:
            result = await _query(params)
            if result:
                enriched = dict(result)
                enriched.setdefault("reg_number", reg_number)
                enriched.setdefault("manufacture_num", mi_number)
                enriched.setdefault("mitype_number", mit_number)
                enriched.setdefault("mitype_title", base_params.get("mit_title", ""))
                enriched["_valid_dt"] = _parse_date_value(result.get("valid_date"))
                enriched["_vrf_dt"] = _parse_date_value(result.get("verification_date"))
                entry_candidates.append(enriched)

        if entry_candidates:
            entry_candidates.sort(
                key=lambda item: (
                    item.get("_valid_dt") or item.get("_vrf_dt") or date.min,
                    item.get("_vrf_dt") or date.min,
                ),
                reverse=True,
            )
            best = dict(entry_candidates[0])
            best.pop("_valid_dt", None)
            best.pop("_vrf_dt", None)
            results.append(best)

    return results


# Алиас для совместимости со старым импортом в protocols.py
# (Теперь и старое имя, и новое работают одинаково.)
async def find_etalon_certificate(
    client: httpx.AsyncClient,
    details: dict[str, Any],
    sem: asyncio.Semaphore | None = None,
) -> dict[str, str] | None:
    certs = await resolve_etalon_certs_from_details(client, details, sem=sem)
    return certs[0] if certs else None


async def find_etalon_certificates(
    client: httpx.AsyncClient,
    details: dict[str, Any],
    sem: asyncio.Semaphore | None = None,
) -> list[dict[str, str]]:
    return await resolve_etalon_certs_from_details(client, details, sem=sem)
