from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    from importlib.resources import files  # py3.9+
except Exception:  # pragma: no cover
    files = None  # fall back to filesystem

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _read_json(filename: str) -> dict[str, Any]:
    # пробуем загрузить как package-data, иначе — с диска
    if files is not None:
        try:
            with files("app.data").joinpath(filename).open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    with (DATA_DIR / filename).open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _methodologies() -> dict[str, Any]:
    return _read_json("methodologies.json")


@lru_cache(maxsize=1)
def _orgs() -> dict[str, Any]:
    return _read_json("orgs.json")


# -------------------- Methodologies --------------------


def get_methodology_by_code(code: str) -> dict[str, Any] | None:
    if not code:
        return None
    data = _methodologies()
    # точное совпадение ключа
    if code in data:
        return data[code]
    # пробуем по «ядру» (например, "2124-90")
    core = _core_mi_code(code)
    for k, v in data.items():
        if _core_mi_code(k) == core:
            return v
    # поиск по подстроке (на вход может приходить длинная строка)
    for k, v in data.items():
        if k in code or k.lower() in code.lower():
            return v
    return None


def _core_mi_code(s: str) -> str:
    # оставляем только цифры и дефисы, например "МИ 2124-90" -> "2124-90"
    m = re.search(r"(\d{3,5}-\d{2})", s.replace(" ", ""))
    return m.group(1) if m else s


# -------------------- Orgs / INN --------------------

_QUOTES = "«»„“‚’\"'`´˝"


def _norm_org(name: str) -> str:
    s = name.strip()
    for q in _QUOTES:
        s = s.replace(q, "")
    s = re.sub(r"\s+", " ", s)
    return s.upper()


def get_inn_by_owner(owner_name: str) -> str | None:
    if not owner_name:
        return None
    orgs = _orgs()
    # 1) точное совпадение
    if owner_name in orgs:
        inn = orgs[owner_name].get("inn")
        return str(inn) if inn else None
    # 2) нормализованное сравнение
    norm = _norm_org(owner_name)
    for k, v in orgs.items():
        if _norm_org(k) == norm:
            inn = v.get("inn")
            return str(inn) if inn else None
    return None
