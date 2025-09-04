from __future__ import annotations
import re
from typing import Optional, Dict, Any

import httpx
from dateutil import parser as dtparser
from app.core.config import settings

ARSHIN_BASE = "https://fgis.gost.ru/fundmetrology/eapi"

def guess_year_from_cert(cert: str) -> Optional[int]:
    m = re.search(r"(20\d{2})", cert)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d{1,2}[./-]\d{1,2}[./-](20\d{2}))", cert)
    if m:
        try:
            return dtparser.parse(m.group(1), dayfirst=True).year
        except Exception:
            return None
    return None

async def fetch_vri_id_by_certificate(client: httpx.AsyncClient, certificate: str, year: Optional[int] = None) -> Dict[str, Any]:
    """
    Возвращает словарь: {certificate, vri_id, year_used, raw_result}
    """
    params = {"result_docnum": certificate}
    if year:
        params["year"] = year

    r = await client.get(f"{ARSHIN_BASE}/vri", params=params, timeout=settings.ARSHIN_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    items = (data.get("result") or {}).get("items") or []
    vri_id = items[0].get("vri_id") if items else None
    return {
        "certificate": certificate,
        "vri_id": vri_id,
        "year_used": year,
        "raw_result": data.get("result", {})
    }

async def fetch_vri_details(client: httpx.AsyncClient, vri_id: str) -> Dict[str, Any]:
    url = f"{ARSHIN_BASE}/vri/{vri_id}"
    r = await client.get(url, timeout=settings.ARSHIN_TIMEOUT)
    r.raise_for_status()
    return r.json()

def compose_etalon_line_from_details(details: Dict[str, Any]) -> str:
    res = (details or {}).get("result", {})
    eta = (res.get("miInfo") or {}).get("etaMI") or {}
    reg = (eta.get("regNumber") or "").strip()
    num = (eta.get("mitypeNumber") or "").strip()
    title = (eta.get("mitypeTitle") or "").strip()
    mtype = (eta.get("mitypeType") or "").strip()
    short = re.split(r"\s*,\s*", mtype)[0] if mtype else ""
    parts = [p for p in [reg, num, title, short] if p]
    return "; ".join(parts)

def extract_detail_fields(details: Dict[str, Any]) -> Dict[str, Any]:
    res = (details or {}).get("result", {})
    vri = (res.get("vriInfo") or {})
    eta = ((res.get("miInfo") or {}).get("etaMI") or {})
    applicable = bool(((vri.get("applicable") or {}).get("certNum")))
    # короткая форма типа (до запятой)
    mtype = (eta.get("mitypeType") or "").strip()
    mtype_short = re.split(r"\s*,\s*", mtype)[0] if mtype else ""
    return {
        "organization": vri.get("organization"),
        "vrfDate": vri.get("vrfDate"),
        "validDate": vri.get("validDate"),
        "applicable": applicable,
        "protocol_url": (res.get("info") or {}).get("protocol_url"),
        "regNumber": eta.get("regNumber"),
        "mitypeNumber": eta.get("mitypeNumber"),
        "mitypeTitle": eta.get("mitypeTitle"),
        "mitypeType": eta.get("mitypeType"),
        "mitypeType_short": mtype_short,
        "manufactureNum": eta.get("manufactureNum"),
        "manufactureYear": eta.get("manufactureYear"),
        "rankCode": eta.get("rankCode"),
        "rankTitle": eta.get("rankTitle"),
    }
