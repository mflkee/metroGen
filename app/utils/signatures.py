from __future__ import annotations

import base64
import random
import re
from collections.abc import Iterator
from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path

from app.core.config import settings
from app.utils.paths import get_project_root

_SIGN_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

# Вертикальная точка опоры относительно нижней границы слота.
_BOTTOM_BASE = 6.5
_BOTTOM_JITTER = 8.5  # px ≈ диапазон -2..15

# Горизонтальная позиция задаётся в пикселях от левого края слота.
_LEFT_BASE = 210.0
_LEFT_JITTER = 110.0  # px ≈ диапазон 100..320

# Диапазон высоты подписи (px).
_HEIGHT_BASE = 33.0
_HEIGHT_JITTER = 3.0

# Поворот/масштаб/наклон подписи.
_ROTATION_BASE = 0.0
_ROTATION_JITTER = 3.0
_SCALE_X_BASE = 0.75
_SCALE_X_JITTER = 0.05  # 0.7..0.8
_SCALE_Y_BASE = 1.25
_SCALE_Y_JITTER = 0.25  # 1.0..1.5
_SKEW_BASE = 0.0
_SKEW_JITTER = 10.0

_HEIGHT_SCALE_OVERRIDES: dict[tuple[str, ...], float] = {
    ("большаков",): 0.75,
}
_VERTICAL_OFFSET_OVERRIDES: dict[tuple[str, ...], float] = {}


@dataclass(frozen=True)
class SignatureRender:
    src: str
    style: str


@dataclass(frozen=True)
class _SignatureEntry:
    path: Path
    normalized_tokens: tuple[str, ...]


def _normalize(text: str) -> str:
    lowered = text.lower().replace("ё", "е")
    cleaned = re.sub(r"[^0-9a-zа-я]+", " ", lowered, flags=re.UNICODE)
    return " ".join(cleaned.split())


def _signatures_dirs() -> tuple[Path, ...]:
    root = get_project_root()
    configured = Path(settings.SIGNATURES_DIR)
    if not configured.is_absolute():
        configured = root / configured
    candidates: list[Path] = [configured]

    fallback = root / "data" / "signatures"
    if fallback not in candidates:
        candidates.append(fallback)

    existing = [p for p in candidates if p.exists()]
    return tuple(existing)


def _iter_signature_files() -> Iterator[Path]:
    for base in _signatures_dirs():
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in _SIGN_EXTENSIONS:
                yield path


@lru_cache(maxsize=1)
def _signature_entries() -> tuple[_SignatureEntry, ...]:
    entries: list[_SignatureEntry] = []
    for path in _iter_signature_files():
        normalized = _normalize(path.stem)
        if not normalized:
            continue
        tokens = tuple(normalized.split())
        if not tokens:
            continue
        entries.append(_SignatureEntry(path=path, normalized_tokens=tokens))
    return tuple(entries)


@cache
def _data_uri_for(path_str: str) -> str:
    path = Path(path_str)
    data = path.read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        mime = "image/jpeg"
    elif suffix == ".webp":
        mime = "image/webp"
    else:
        mime = "image/png"
    return f"data:{mime};base64,{encoded}"


_RNG: random.Random = random.SystemRandom()


def _with_jitter(base: float, jitter: float) -> float:
    if jitter <= 0:
        return base
    return base + _RNG.uniform(-jitter, jitter)


def _match_override(
    overrides: dict[tuple[str, ...], float],
    name: str,
    entry: _SignatureEntry,
) -> float | None:
    tokens_name = set(_normalize(name).split())
    tokens_entry = set(entry.normalized_tokens)
    for key_tokens, value in overrides.items():
        key_set = set(key_tokens)
        if key_set <= tokens_name or key_set <= tokens_entry:
            return value
    return None


def _height_scale_for(name: str, entry: _SignatureEntry) -> float:
    matched = _match_override(_HEIGHT_SCALE_OVERRIDES, name, entry)
    if matched is None:
        return 1.0
    return max(0.3, float(matched))


def _vertical_offset_for(name: str, entry: _SignatureEntry) -> float:
    matched = _match_override(_VERTICAL_OFFSET_OVERRIDES, name, entry)
    if matched is None:
        return 0.0
    return float(matched)


def _best_matching_entries(name: str) -> list[_SignatureEntry]:
    target_normalized = _normalize(name)
    if not target_normalized:
        return []
    target_tokens = set(target_normalized.split())
    if not target_tokens:
        return []

    exact: list[_SignatureEntry] = []
    partial: list[tuple[int, int, _SignatureEntry]] = []

    for entry in _signature_entries():
        entry_tokens = set(entry.normalized_tokens)
        if target_tokens.issubset(entry_tokens):
            exact.append(entry)
            continue
        common = target_tokens & entry_tokens
        if common:
            partial.append((len(common), len(entry_tokens), entry))

    if exact:
        return exact

    if partial:
        partial.sort(key=lambda item: (-item[0], item[1]))
        best_score = partial[0][0]
        return [entry for score, _, entry in partial if score == best_score]

    return []


def get_signature_render(verifier_name: str | None) -> SignatureRender | None:
    if not verifier_name:
        return None

    candidates = _best_matching_entries(verifier_name)
    if not candidates:
        return None

    entry = _RNG.choice(candidates)
    src = _data_uri_for(str(entry.path))

    bottom = _with_jitter(_BOTTOM_BASE, _BOTTOM_JITTER) + _vertical_offset_for(
        verifier_name, entry
    )
    left_px = _with_jitter(_LEFT_BASE, _LEFT_JITTER)
    scale = _height_scale_for(verifier_name, entry)
    raw_height = _with_jitter(_HEIGHT_BASE, _HEIGHT_JITTER)
    height = max(10.0, raw_height * scale)
    rotation = _with_jitter(_ROTATION_BASE, _ROTATION_JITTER)

    scale_x = max(0.7, _with_jitter(_SCALE_X_BASE, _SCALE_X_JITTER))
    scale_y = max(0.8, _with_jitter(_SCALE_Y_BASE, _SCALE_Y_JITTER))
    skew = _with_jitter(_SKEW_BASE, _SKEW_JITTER)

    transform_value = " ".join(
        [
            "translate(-50%, 0)",
            f"rotate({rotation:.1f}deg)",
            f"scaleX({scale_x:.2f})",
            f"scaleY({scale_y:.2f})",
            f"skewX({skew:.1f}deg)",
        ]
    )

    style = (
        "display: block; "
        f"bottom: {bottom:.1f}px; "
        f"left: {left_px:.1f}px; "
        f"height: {height:.1f}px; "
        f"transform: {transform_value};"
    )

    return SignatureRender(src=src, style=style)


def _clear_caches_for_tests() -> None:
    _signature_entries.cache_clear()
    _data_uri_for.cache_clear()
