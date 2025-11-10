import builtins
import sys
import types

import pytest

from app.services.pdf import html_to_pdf_bytes


@pytest.mark.anyio
async def test_html_to_pdf_bytes_returns_none_when_playwright_missing(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("playwright"):
            raise ImportError("playwright is not installed")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    result = await html_to_pdf_bytes("<html><body>noop</body></html>")

    assert result is None


class DummyPage:
    def __init__(self):
        self.rendered = None
        self.pdf_kwargs = None

    async def set_content(self, html, wait_until):
        self.rendered = (html, wait_until)

    async def pdf(self, **kwargs):
        self.pdf_kwargs = kwargs
        return b"%PDF-FAKE%"


class DummyBrowser:
    def __init__(self):
        self.closed = False
        self.last_page: DummyPage | None = None

    async def new_page(self):
        self.last_page = DummyPage()
        return self.last_page

    async def close(self):
        self.closed = True


class DummyChromium:
    def __init__(self, browser: DummyBrowser):
        self._browser = browser

    async def launch(self):
        return self._browser


class DummyPlaywrightContext:
    def __init__(self, browser: DummyBrowser):
        self._browser = browser

    async def __aenter__(self):
        return types.SimpleNamespace(chromium=DummyChromium(self._browser))

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.anyio
async def test_html_to_pdf_bytes_generates_bytes_with_fake_playwright(monkeypatch):
    dummy_browser = DummyBrowser()

    def fake_async_playwright():
        return DummyPlaywrightContext(dummy_browser)

    async_api_module = types.ModuleType("playwright.async_api")
    async_api_module.async_playwright = fake_async_playwright
    root_module = types.ModuleType("playwright")
    root_module.async_api = async_api_module

    monkeypatch.setitem(sys.modules, "playwright", root_module)
    monkeypatch.setitem(sys.modules, "playwright.async_api", async_api_module)

    pdf_bytes = await html_to_pdf_bytes("<html><body>ok</body></html>")

    assert pdf_bytes == b"%PDF-FAKE%"
    assert dummy_browser.closed is True
    assert dummy_browser.last_page is not None
    assert dummy_browser.last_page.rendered == ("<html><body>ok</body></html>", "load")
    assert dummy_browser.last_page.pdf_kwargs["print_background"] is True
