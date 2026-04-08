from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=select_autoescape(["html", "xml"])
)


def render_html(template_name: str, context: dict[str, Any]) -> str:
    tpl = _env.get_template(template_name)
    return tpl.render(**context)


async def pdf_generation_available() -> bool:
    """Return True when Playwright and the Chromium executable are available."""
    try:
        from playwright.async_api import async_playwright
    except Exception as exc:
        logger.warning("Playwright is unavailable for PDF generation: {}", exc)
        return False

    try:
        async with async_playwright() as p:
            executable_path = str(getattr(p.chromium, "executable_path", "") or "").strip()
            if executable_path and Path(executable_path).exists():
                return True
            logger.warning(
                "Playwright Chromium executable is missing for PDF generation: {}",
                executable_path or "<empty>",
            )
            return False
    except Exception as exc:
        logger.warning("Playwright is unavailable for PDF generation: {}", exc)
        return False


async def html_to_pdf_bytes(html: str) -> bytes | None:
    """
    Преобразование HTML → PDF через Playwright (Chromium).
    Вернёт None, если Playwright не установлен.
    """
    try:
        from playwright.async_api import async_playwright
    except Exception as exc:
        logger.warning("Playwright is unavailable for PDF generation: {}", exc)
        return None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            try:
                page = await browser.new_page()
                await page.set_content(html, wait_until="load")
                pdf_bytes = await page.pdf(
                    width="210mm",
                    height="297mm",
                    print_background=True,
                    margin={"top": "10mm", "bottom": "10mm", "left": "8mm", "right": "8mm"},
                    landscape=False,
                )
                return pdf_bytes
            finally:
                try:
                    await browser.close()
                except Exception as close_error:
                    logger.warning("Failed to close Playwright browser: {}", close_error)
    except Exception as exc:
        logger.error("Playwright PDF rendering failed: {}", exc)
        raise
