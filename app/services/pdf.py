from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=select_autoescape(["html", "xml"])
)


def render_html(template_name: str, context: dict[str, Any]) -> str:
    tpl = _env.get_template(template_name)
    return tpl.render(**context)


async def html_to_pdf_bytes(html: str) -> bytes | None:
    """
    Преобразование HTML → PDF через Playwright (Chromium).
    Вернёт None, если Playwright не установлен.
    """
    try:
        from playwright.async_api import async_playwright
    except Exception:
        return None

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="load")
        pdf_bytes = await page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "12mm", "bottom": "12mm", "left": "15mm", "right": "15mm"},
        )
        await browser.close()
        return pdf_bytes
