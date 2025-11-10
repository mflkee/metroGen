import stat

from app.services.protocol_builder import suggest_filename
from app.utils import paths
from app.utils.paths import sanitize_filename


def test_sanitize_filename_removes_invalid_characters():
    assert sanitize_filename("A:B/C?.txt") == "A-B-C-.txt"


def test_sanitize_filename_uses_default_for_empty():
    assert sanitize_filename("   ", default="fallback") == "fallback"


def test_suggest_filename_applies_sanitization():
    row = {"Заводской номер": "ABC/123", "Дата поверки": "2025-01-15"}
    assert suggest_filename(row) == "ABC-123-б-150125-1"


def test_named_exports_dir_world_writable(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)
    monkeypatch.setattr(paths.settings, "EXPORTS_DIR", "exports-test")

    target = paths.get_named_exports_dir("manometers")

    assert target.exists()
    mode = stat.S_IMODE(target.stat().st_mode)
    assert mode == 0o777


def test_output_dir_world_writable(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_project_root", lambda: tmp_path)

    out_dir = paths.get_output_dir()

    assert out_dir.exists()
    mode = stat.S_IMODE(out_dir.stat().st_mode)
    assert mode == 0o777
