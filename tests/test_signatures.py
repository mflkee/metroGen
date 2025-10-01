from __future__ import annotations

import base64
import random
import re

from app.core.config import settings
from app.utils import signatures

_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y1ek8sAAAAASUVORK5CYII="
)


def _setup_signature(monkeypatch, tmp_path, filename: str = "Большаков С.Н..png"):
    target_dir = tmp_path / "signatures"
    target_dir.mkdir()
    (target_dir / filename).write_bytes(_PIXEL_PNG)

    monkeypatch.setattr(settings, "SIGNATURES_DIR", str(target_dir))
    signatures._clear_caches_for_tests()
    return target_dir


def test_get_signature_render_returns_data(monkeypatch, tmp_path):
    _setup_signature(monkeypatch, tmp_path, filename="test большаков с.н. 1.png")

    original_rng = signatures._RNG
    signatures._RNG = random.Random(0)
    try:
        render = signatures.get_signature_render("Большаков С.Н.")
    finally:
        signatures._RNG = original_rng

    assert render is not None
    assert render.src.startswith("data:image/png;base64,")
    # Проверяем, что стиль включает все ожидаемые свойства и находится в допустимых границах
    assert "display: block" in render.style
    top_match = re.search(r"top:\s*([-0-9.]+)px", render.style)
    left_match = re.search(r"left:\s*([-0-9.]+)px", render.style)
    height_match = re.search(r"height:\s*([-0-9.]+)px", render.style)
    rotation_match = re.search(r"transform:\s*rotate\(([-0-9.]+)deg\)", render.style)

    assert top_match and 36.0 <= float(top_match.group(1)) <= 40.0
    assert left_match and 40.0 <= float(left_match.group(1)) <= 56.0
    assert height_match and 24.0 <= float(height_match.group(1)) <= 28.0
    assert rotation_match and -2.5 <= float(rotation_match.group(1)) <= 2.5


def test_get_signature_render_returns_none_when_missing(monkeypatch, tmp_path):
    _setup_signature(monkeypatch, tmp_path, filename="другой.png")
    render = signatures.get_signature_render("Несуществующий Поверитель")
    assert render is None
