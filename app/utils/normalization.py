from __future__ import annotations

from typing import Any

__all__ = ("normalize_serial",)


def normalize_serial(value: Any) -> str:
    """Normalize serial numbers: strip spaces, drop separators, uppercase."""

    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    for ch in ("№", " ", "-", "/", "\\"):
        text = text.replace(ch, "")
    return text.upper()

