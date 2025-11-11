from __future__ import annotations

import re

__all__ = (
    "normalize_owner_alias",
    "normalize_methodology_alias",
    "normalize_generic",
)

# NOTE: Кириллица часто приходит с "ё". Для поиска в базе нормализуем в "е".
_TRANSLATION_TABLE = str.maketrans(
    {
        "ё": "е",
        "Ё": "Е",
        "«": '"',
        "»": '"',
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
    }
)
_NON_WORD_RE = re.compile(r"[^0-9a-zа-я]+", re.IGNORECASE)


def normalize_generic(value: str) -> str:
    """Return a lowercase, compacted representation suitable for lookups."""
    normalized = value.translate(_TRANSLATION_TABLE).lower()
    cleaned = _NON_WORD_RE.sub(" ", normalized)
    return " ".join(cleaned.split())


def normalize_owner_alias(value: str) -> str:
    """Normalize owner aliases to align with the unique DB index."""
    return normalize_generic(value)


def normalize_methodology_alias(value: str) -> str:
    """Normalize methodology aliases used for fuzzy lookup."""
    return normalize_generic(value)
