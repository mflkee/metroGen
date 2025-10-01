from __future__ import annotations

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


def get_output_dir() -> Path:
    """Папка для временного сохранения HTML/сырого вывода до внедрения БД.

    По требованию — корень проекта /output.
    """
    root = get_project_root()
    out = root / "output"
    out.mkdir(parents=True, exist_ok=True)
    return out
