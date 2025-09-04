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
