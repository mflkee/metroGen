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
    monkeypatch.setattr(signatures, "_signatures_dirs", lambda: (target_dir,))
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
    bottom_match = re.search(r"bottom:\s*([-0-9.]+)px", render.style)
    left_match = re.search(r"left:\s*([-0-9.]+)px", render.style)
    height_match = re.search(r"height:\s*([-0-9.]+)px", render.style)
    rotation_match = re.search(r"rotate\(([-0-9.]+)deg\)", render.style)

    assert bottom_match and 0.0 <= float(bottom_match.group(1)) <= 25.0
    assert left_match and 120.0 <= float(left_match.group(1)) <= 280.0
    assert height_match and 20.0 <= float(height_match.group(1)) <= 32.0
    assert rotation_match and -3.0 <= float(rotation_match.group(1)) <= 3.0


def test_get_signature_render_returns_none_when_missing(monkeypatch, tmp_path):
    _setup_signature(monkeypatch, tmp_path, filename="другой.png")
    render = signatures.get_signature_render("Несуществующий Поверитель")
    assert render is None


def test_get_signature_render_prefers_last_name_on_partial_match(monkeypatch, tmp_path):
    target_dir = _setup_signature(monkeypatch, tmp_path, filename="test манджеев а.а..png")
    # Файл с фамилией поверителя, но без инициалов целиком — пересекается по фамилии.
    tiora_path = target_dir / "test тиора в.а..png"
    tiora_path.write_bytes(b"B")  # другое содержимое для уникального data URI

    signatures._clear_caches_for_tests()

    original_rng = signatures._RNG
    signatures._RNG = random.Random(0)
    try:
        render = signatures.get_signature_render("Тиора А.А.")
    finally:
        signatures._RNG = original_rng

    expected_src = signatures._data_uri_for(str(tiora_path))
    assert render is not None
    assert render.src == expected_src


def test_get_signature_render_refreshes_when_files_appear(monkeypatch, tmp_path):
    target_dir = tmp_path / "signatures"
    target_dir.mkdir()

    monkeypatch.setattr(settings, "SIGNATURES_DIR", str(target_dir))
    monkeypatch.setattr(signatures, "_signatures_dirs", lambda: (target_dir,))
    signatures._clear_caches_for_tests()

    assert signatures.get_signature_render("Большаков С.Н.") is None

    restored = target_dir / "test большаков с.н. 1.png"
    restored.write_bytes(_PIXEL_PNG)

    original_rng = signatures._RNG
    signatures._RNG = random.Random(0)
    try:
        render = signatures.get_signature_render("Большаков С.Н.")
    finally:
        signatures._RNG = original_rng

    assert render is not None
    assert render.src.startswith("data:image/png;base64,")
