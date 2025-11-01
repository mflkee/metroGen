from app.services.protocol_builder import suggest_filename
from app.utils.paths import sanitize_filename


def test_sanitize_filename_removes_invalid_characters():
    assert sanitize_filename("A:B/C?.txt") == "A-B-C-.txt"


def test_sanitize_filename_uses_default_for_empty():
    assert sanitize_filename("   ", default="fallback") == "fallback"


def test_suggest_filename_applies_sanitization():
    row = {"Заводской номер": "ABC/123", "Дата поверки": "2025-01-15"}
    assert suggest_filename(row) == "ABC-123-б-150125-1"
