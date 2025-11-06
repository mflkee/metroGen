from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from app.core.config import settings


def get_project_root() -> Path:
    # app/utils/paths.py -> utils -> app -> project root
    return Path(__file__).resolve().parents[2]


def get_exports_base() -> Path:
    root = get_project_root()
    base = root / settings.EXPORTS_DIR
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_dated_exports_dir(today: date | None = None) -> Path:
    d = today or date.today()
    base = get_exports_base()
    target = base / d.isoformat()
    target.mkdir(parents=True, exist_ok=True)
    return target


def get_named_exports_dir(name: str) -> Path:
    """Return export directory named after `name`, creating it if missing."""
    base = get_exports_base()
    safe_name = sanitize_filename(name, default="exports")
    target = base / safe_name
    target.mkdir(parents=True, exist_ok=True)
    return target


def get_output_dir() -> Path:
    """Папка для временного сохранения HTML/сырого вывода до внедрения БД.

    По требованию — корень проекта /output.
    """
    root = get_project_root()
    out = root / "output"
    out.mkdir(parents=True, exist_ok=True)
    return out


_INVALID_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|]')
_WHITESPACE_RE = re.compile(r"\s+")


def sanitize_filename(
    name: str,
    *,
    default: str = "file",
    replacement: str = "-",
) -> str:
    """Return filesystem-safe name, keeping ASCII/UTF-8 text intact."""
    text = (name or "").strip()
    if not text:
        return default
    cleaned = _INVALID_FILENAME_CHARS.sub(replacement, text)
    cleaned = _WHITESPACE_RE.sub(" ", cleaned).strip()
    cleaned = cleaned.strip(".")
    return cleaned or default
