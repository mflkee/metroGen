# Project Export for LLM

- Root: `/home/mflkee/project/metrologenerator`
- Generated: 2025-10-14 11:55:37
- Files included: 86
- Per-file limit: 1.5 MB

## Project Tree

```
metrologenerator/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── arshin.py
│   │   │   ├── methodologies.py
│   │   │   ├── protocols.py
│   │   │   └── registry.py
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── routes
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── data/
│   │   ├── mappings.py
│   │   ├── methodologies.json
│   │   └── orgs.json
│   ├── db/
│   │   ├── repositories/
│   │   │   ├── core.py
│   │   │   └── utils.py
│   │   ├── base.py
│   │   ├── models.py
│   │   ├── repositories
│   │   ├── seed.py
│   │   └── session.py
│   ├── schemas/
│   │   ├── arshin.py
│   │   ├── methodology.py
│   │   └── protocol.py
│   ├── services/
│   │   ├── generators/
│   │   │   ├── base.py
│   │   │   ├── controller_43790_12.py
│   │   │   ├── pressure_common.py
│   │   ├── arshin_client.py
│   │   ├── cache.py
│   │   ├── generators
│   │   ├── html_renderer.py
│   │   ├── pdf.py
│   │   ├── protocol_builder.py
│   │   ├── registry_ingest.py
│   │   └── templates.py
│   ├── templates/
│   │   ├── controller_43790_12.html
│   │   └── manometer.html
│   ├── utils/
│   │   ├── excel.py
│   │   ├── normalization.py
│   │   ├── paths.py
│   │   └── signatures.py
│   ├── .env.example
│   ├── __init__.py
│   ├── api
│   ├── cli.py
│   ├── core
│   ├── data
│   ├── db
│   ├── main.py
│   ├── schemas
│   ├── services
│   ├── templates
│   └── utils
├── data/
│   ├── attachments/
│   │   ├── Davlenie.html
│   │   ├── DavlenieSuccessDocumentCreator.cs
│   │   ├── DocumentCreatorBase.cs
│   │   ├── Forms.cs
│   │   ├── HTMLCreationResult.cs
│   │   ├── Manometr.html
│   │   ├── ManometrDocumentCreator.cs
│   │   └── PageManipulationExtensions.cs
│   ├── input/
│   │   ├── .~lock.Поверка манометры 06.2025 (copy 1).xlsm#
│   │   └── .~lock.Поверка манометры 06.2025.xlsm#
│   ├── attachments
│   └── input
├── migrations/
│   ├── versions/
│   │   ├── 20250906_000001_init.py
│   │   ├── 20251001_000002_data_model.py
│   │   ├── 20251001_000003_methodology.py
│   │   └── 20251010_000004_add_instrument_kind.py
│   ├── env.py
│   └── versions
├── scripts/
│   └── run_quality_checks.py
├── tests/
│   ├── conftest.py
│   ├── test_arshin_routes.py
│   ├── test_arshin_service.py
│   ├── test_excel_utils.py
│   ├── test_methodologies_routes.py
│   ├── test_protocols_html.py
│   ├── test_protocols_routes.py
│   ├── test_registry_ingest.py
│   ├── test_repository_utils.py
│   ├── test_signatures.py
│   └── test_style.py
├── .env
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── AGENTS.md
├── README.md
├── alembic.ini
├── app
├── migrations
├── pyproject.toml
├── pytest.ini
├── scripts
├── tests
└── uv.lock
```

## Files

### 1. `.env`

```ini
APP_NAME="Arshin helper API"
ARSHIN_TIMEOUT=30
ARSHIN_CONCURRENCY=8
USER_AGENT=arshin-fastapi/0.1
DATABASE_URL=postgresql+asyncpg://postgres:7405@127.0.0.1:5432/metrologenerator

```

### 2. `.gitignore`

```gitignore
project_source_code.txt

```

### 3. `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.5
    hooks:
      - id: ruff
        args: ["--fix", "--exit-non-zero-on-fix"]
      - id: ruff-format

  # Опционально: включить Black, если хотите использовать именно его форматирование
  # Вместо ruff-format (или вместе, если стили совпадают в проекте)
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
        language_version: python3


```

### 4. `.python-version`

```
3.13

```

### 5. `AGENTS.md`

```markdown
# Repository Guidelines

## Project Structure & Module Organization
- `app/` contains the FastAPI code; routes live in `app/api/routes/`, services in `app/services/`, schemas in `app/schemas/`, utilities in `app/utils/`, and shared config/logging in `app/core/`.
- Copy `.env.example` to `.env` for local secrets; adjust `ARSHIN_TIMEOUT`, `ARSHIN_CONCURRENCY`, and `USER_AGENT` before hitting external APIs.
- Packaging metadata and lockfiles reside in `pyproject.toml` and `uv.lock`; keep them in sync when dependencies change.
- Tests live in `tests/` and rely on async fixtures plus `respx` mocks for outbound HTTP.

## Build, Test, and Development Commands
- `uv sync` installs dependencies exactly as locked; prefer this over `pip`.
- `uvicorn app.main:app --reload` starts the API on `http://127.0.0.1:8000`.
- `pytest -q` runs the suite; add `--cov=app` for coverage checks.
- Run `ruff check .` and `black .` before committing to confirm linting and formatting.

## Coding Style & Naming Conventions
- Target Python 3.13, four-space indents, and type hints for public APIs.
- Use `snake_case` for modules/functions, `PascalCase` for classes and Pydantic models.
- Keep FastAPI routes lean: delegate external IO to services and validation to schemas.
- Prefer explicit logging via `app.core.logging.setup_logging()` and configurations through `app.core.config.settings`.

## Testing Guidelines
- Write async pytest tests; name files `tests/test_*.py` and mirror module paths when feasible.
- Use `respx` to stub HTTPX calls; ensure scenarios cover success, failure, and timeout paths.
- Treat new endpoints or services as requiring coverage; run `pytest --cov=app` before PR submission.

## Commit & Pull Request Guidelines
- Follow imperative commit subjects under 72 chars, e.g., `feat(api): add /resolve/vri-details-by-excel`.
- PRs must list purpose, linked issues, test evidence, and sample requests/responses (curl snippets or JSON).
- Update documentation, schemas, and changelog entries whenever API contracts shift.

## Security & Configuration Tips
- Never commit `.env`; rely on `.env.example` for defaults.
- Honor timeout and concurrency settings when creating new HTTP clients.
- Validate external responses with Pydantic models to guard against schema drift.

```

### 6. `README.md`

```markdown
Protocol generator for mkair

Quick start
- Install deps: `uv sync` (preferred) or `pip install -e .[dev]`
- Run API: `uvicorn app.main:app --reload` → http://127.0.0.1:8000
- Run tests: `pytest -q` or with coverage `pytest --cov=app -q`

Database setup
- Copy `app/.env.example` to `.env` and set `DATABASE_URL` (e.g. `postgresql+asyncpg://postgres:password@localhost:5432/metrologenerator`).
- Apply migrations before the first run: `uv run alembic upgrade head`.
- Seed lookup data (owners, methodologies) once: `uv run python -m app.db.seed`. The FastAPI app also seeds automatically on startup, so the manual command is optional when bootstrapping CI/local environments.
- Controllers/manometers endpoints ingest the provided registry Excel into Postgres (rows are normalized before upsert), so repeated uploads reuse cached data.

Database overview
- Core registry data lives in the new PostgreSQL tables created by Alembic migrations.
- `verification_registry_entries` caches rows from the official БД выгрузки with lookup indexes on serial, документ and протокол.
- `measuring_instruments` stores parsed приборы from рабочие Excel файлы and links them to owners, methodologies and registry entries.
- `etalon_devices` + `etalon_certifications` persist эталоны returned by Аршин so repeated генерации reuse cached certificates.
- `methodologies`, `methodology_aliases`, `methodology_points` describe МП, their псевдонимы и набор пунктов (переключатель bool/клауза/custom).
- `owners` and `owner_aliases` replace Python маппинги, giving a single источник правды (название + ИНН).

Code style
- Lint/format via Ruff: `ruff check .` and `ruff format .`
- Optionally Black: `black .`

Pre-commit
- Install: `pip install pre-commit` then `pre-commit install`
- Hooks: Ruff (lint+format), optional Black (see `.pre-commit-config.yaml`)

```

### 7. `alembic.ini`

```ini
[alembic]
script_location = migrations
sqlalchemy.url = %(DATABASE_URL)s

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers = console
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s

```

### 8. `app/.env.example`

```
APP_NAME=Arshin helper API
ARSHIN_TIMEOUT=30
ARSHIN_CONCURRENCY=8
USER_AGENT=arshin-fastapi/0.1
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/metrologenerator

```

### 9. `app/__init__.py`

```python

```

### 10. `app/api/__init__.py`

```python

```

### 11. `app/api/deps.py`

```python
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import httpx

from app.core.config import settings
from app.db.session import get_db

__all__ = ("get_http_client", "get_semaphore", "get_db")

# Глобальный семафор для ограничения параллельности исходящих запросов
_SEM = asyncio.Semaphore(settings.ARSHIN_CONCURRENCY)


async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    """Возвращает новый httpx.AsyncClient на время обработки запроса.

    Такой подход упрощает тестирование с respx (моки подхватываются всегда)
    и не создаёт зависимостей от времени импорта.
    """
    async with httpx.AsyncClient(
        headers={"User-Agent": settings.USER_AGENT},
        timeout=settings.ARSHIN_TIMEOUT,
    ) as client:
        yield client


def get_semaphore() -> asyncio.Semaphore:
    """Возвращает общий семафор для ограничения параллельности."""
    return _SEM

```

### 12. `app/api/routes/__init__.py`

```python

```

### 13. `app/api/routes/arshin.py`

```python
"""Routes for Arshin resolution endpoints."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import get_http_client, get_semaphore
from app.services.arshin_client import (
    compose_etalon_line_from_details,
    extract_detail_fields,
    fetch_vri_details,
    fetch_vri_id_by_certificate,
    guess_year_from_cert,
)
from app.utils.excel import CERTIFICATE_HEADER_KEYS

router = APIRouter(prefix="/api/v1/resolve", tags=["arshin"])


@router.get("/vri-id")
async def get_vri_id(
    cert: str,
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
) -> dict[str, str | None]:
    """Возвращает vri_id по номеру свидетельства.

    - Проверяем входные данные
    - Определяем год из номера (если удаётся)
    - Ищем vri_id через Аршин
    """
    if not cert:
        raise HTTPException(status_code=400, detail="cert is required")

    year = guess_year_from_cert(cert)
    vri_id = await fetch_vri_id_by_certificate(client, cert, year=year, sem=sem, use_cache=False)
    if not vri_id:
        # возвращаем 200 с пустым vri_id — тестам это не критично,
        # но пусть будет информативнее
        return {"vri_id": None}
    return {"vri_id": vri_id}


@router.get("/vri/{vri_id}")
async def get_vri_details(
    vri_id: str,
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
) -> dict[str, Any]:
    """Возвращает краткую информацию по vri_id, включая строку эталона.

    - Проверяем входные данные
    - Запрашиваем детали по vri_id
    - Готовим строку эталона и ключевые поля
    """
    if not vri_id:
        raise HTTPException(status_code=400, detail="vri_id is required")

    details = await fetch_vri_details(client, vri_id, sem=sem)
    if not details:
        raise HTTPException(status_code=404, detail="not found")

    etalon_line = compose_etalon_line_from_details(details)
    fields = extract_detail_fields(details)
    return {
        "vri_id": vri_id,
        "etalon_line": etalon_line,
        "fields": fields,
        "result": details,  # на будущее
    }


# ───────────────────────── excel endpoint ─────────────────────────


def _read_cert_list_from_excel(file: UploadFile) -> list[str]:
    """Читает список сертификатов из Excel.

    - Ищет колонку по заголовку 'Номер свидетельства' (или частый вариант с опечаткой)
    - Возвращает непустые значения со 2-й строки и ниже
    """
    from openpyxl import load_workbook  # локальный импорт, чтобы не грузить при старте

    wb = load_workbook(file.file, read_only=True, data_only=True)
    ws = wb.active

    # Найти индекс колонки по заголовку
    header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
    col_idx = None
    accepted_headers = {header.lower() for header in CERTIFICATE_HEADER_KEYS}
    for i, v in enumerate(header_row):
        if not isinstance(v, str):
            continue
        header = v.strip()
        if header and header.lower() in accepted_headers:
            col_idx = i
            break
    if col_idx is None:
        return []

    certs: list[str] = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row is None:
            continue
        val = row[col_idx] if col_idx < len(row) else None
        if val is None:
            continue
        cert = str(val).strip()
        if cert:
            certs.append(cert)
    return certs


@router.post("/vri-details-by-excel")
async def post_vri_details_by_excel(
    file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
) -> dict[str, Any]:
    """Принимает Excel и возвращает список найденных vri_id по сертификатам.

    Для каждого сертификата:
      - ищем vri_id (через /vri)
      - при наличии — подтягиваем детали (через /vri/{id})
    """
    certs = _read_cert_list_from_excel(file)

    # Обрабатываем строки параллельно, ограничение — через семафор
    async def process(cert: str) -> dict[str, Any]:
        try:
            vri_id = await fetch_vri_id_by_certificate(
                client, cert, year=guess_year_from_cert(cert), sem=sem, use_cache=False
            )
            details: dict[str, Any] = {}
            if vri_id:
                details = await fetch_vri_details(client, vri_id, sem=sem)
            return {"certificate": cert, "vri_id": vri_id, "details": details or None}
        except httpx.HTTPError as e:
            return {
                "certificate": cert,
                "vri_id": None,
                "details": None,
                "error": f"http error: {e}",
            }

    items = await asyncio.gather(*(process(c) for c in certs))

    return {"items": items}

```

### 14. `app/api/routes/methodologies.py`

```python
from __future__ import annotations

import re
from collections.abc import Iterable

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.models import MethodologyPointType
from app.db.repositories import MethodologyPointPayload, MethodologyRepository
from app.schemas.methodology import (
    MethodologyCreate,
    MethodologyOut,
    MethodologyPointIn,
)

router = APIRouter(prefix="/api/v1/methodologies", tags=["methodologies"])


def _infer_point_type(payload: MethodologyPointIn) -> MethodologyPointType:
    if payload.point_type:
        return payload.point_type

    label = payload.label.strip().lower()
    if "____" in label or "__" in label:
        return MethodologyPointType.CUSTOM

    if "соответствует" in label:
        if "не соответствует" in label or "соответствует/не соответствует" in label:
            return MethodologyPointType.BOOL
        return MethodologyPointType.BOOL

    return MethodologyPointType.CLAUSE


def _strip_label(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    return cleaned


def _payload_points(points: Iterable[MethodologyPointIn]) -> list[MethodologyPointPayload]:
    payload: list[MethodologyPointPayload] = []
    for point in points:
        label = _strip_label(point.label)
        if not label:
            continue
        payload.append(
            MethodologyPointPayload(
                position=point.position,
                label=label,
                point_type=_infer_point_type(point),
            )
        )
    return payload


@router.post("", response_model=MethodologyOut, status_code=201)
async def create_methodology(
    body: MethodologyCreate,
    session: AsyncSession = Depends(get_db),
) -> MethodologyOut:
    if not body.points:
        raise HTTPException(status_code=400, detail="points are required")

    repo = MethodologyRepository(session)
    methodology = await repo.upsert_methodology(
        code=body.code,
        title=body.title or body.code,
        document=body.document,
        notes=body.notes,
        allowable_variation_pct=body.allowable_variation_pct,
    )

    alias_payload = [(body.code, 100)]
    if body.title and body.title != body.code:
        alias_payload.append((body.title, 90))
    for alias in body.aliases:
        alias_payload.append((alias, 80))

    await repo.ensure_aliases(methodology, alias_payload)

    payload_points = _payload_points(body.points)
    if not payload_points:
        raise HTTPException(status_code=400, detail="at least one point must have non-empty label")

    await repo.replace_points(methodology, payload_points)
    await session.commit()

    refreshed = await repo.get_by_code(body.code)
    if refreshed is None:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="failed to load methodology")

    return MethodologyOut.from_orm_obj(refreshed)

```

### 15. `app/api/routes/protocols.py`

```python
from __future__ import annotations

import asyncio
import re
from collections.abc import Iterable, Mapping
from datetime import date
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse

from app.api.deps import get_db, get_http_client, get_semaphore
from app.db.repositories import RegistryRepository
from app.schemas.protocol import ProtocolContextItem, ProtocolContextListOut
from app.services.arshin_client import ARSHIN_BASE, find_etalon_certificate
from app.services.html_renderer import render_protocol_html
from app.services.pdf import html_to_pdf_bytes
from app.services.protocol_builder import (
    build_protocol_context,
    make_protocol_number,
    suggest_filename,
)
from app.services.registry_ingest import ingest_registry_rows
from app.utils.excel import (
    extract_certificate_number,
    read_rows_as_dicts,
    read_rows_with_required_headers,
)
from app.utils.normalization import normalize_serial
from app.utils.paths import get_dated_exports_dir, get_output_dir

router = APIRouter(prefix="/api/v1/protocols", tags=["protocols"])


def _filename_from_protocol_number(pn: str, ext: str = ".pdf") -> str:
    """Make a filesystem-safe filename from a protocol number.

    Example: "БСН/150125/1" -> "БСН-150125-1.pdf"
    """
    name = (pn or "protocol").strip()
    # replace separators unsafe for filesystems
    for ch in ("/", "\\"):
        name = name.replace(ch, "-")
    # collapse spaces
    name = "-".join(part for part in name.split())
    if not name.lower().endswith(ext):
        name = f"{name}{ext}"
    return name


def _controller_filename(ctx: dict[str, Any]) -> str:
    ver_date = str(ctx.get("verification_date") or "").strip()
    serial = str(
        ctx.get("manufactureNum") or ctx.get("Заводской номер") or ctx.get("manufacture_num") or ""
    ).strip()
    mpi = ctx.get("mpi_years")

    parts: list[str] = []
    if ver_date:
        parts.append(ver_date)
    if serial:
        parts.append(f"№ {serial}")
    if mpi:
        parts.append(f"(МПИ-{mpi})")

    name = " ".join(parts).strip() or "protocol"
    safe_name = re.sub(r"[\\/:]+", "-", name)
    safe_name = re.sub(r"\s+", " ", safe_name).strip()
    return safe_name


SERIAL_SOURCE_KEYS: tuple[str, ...] = (
    "Заводской номер",
    "Заводской №",
    "Заводской №/ Буквенно-цифровое обозначение",
    "Заводской №/Буквенно-цифровое обозначение",
    "Заводской № / Буквенно-цифровое обозначение",
    "Серийный номер",
)

DB_SERIAL_KEYS: tuple[str, ...] = (
    "Заводской №/ Буквенно-цифровое обозначение",
    "Заводской номер",
    "Заводской №",
    "Серийный номер",
)


def _extract_first_value(row: Mapping[str, Any], keys: Iterable[str]) -> str:
    if not isinstance(row, Mapping):
        row = dict(row)

    pairs = [(str(key), row[key]) for key in row.keys() if isinstance(key, str)]

    for candidate in keys:
        norm = candidate.strip().lower()
        for raw_key, value in pairs:
            if value is None:
                continue
            if raw_key.strip().lower() != norm:
                continue
            text = str(value).strip()
            if text:
                return text
    return ""


async def _build_context_from_db(
    row: Mapping[str, Any],
    *,
    db_index: Mapping[str, Mapping[str, Any]] | None = None,
    db_row: Mapping[str, Any] | None = None,
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    session: AsyncSession,
    strict_certificate_match: bool = False,
) -> ProtocolContextItem:
    row_data = dict(row)
    filename = suggest_filename(row_data)

    serial_value = _extract_first_value(row_data, SERIAL_SOURCE_KEYS)
    serial_key = normalize_serial(serial_value)
    if not serial_key:
        return ProtocolContextItem(
            certificate="",
            vri_id="",
            filename=filename,
            context={},
            raw_details={},
            error="serial number is empty",
        )

    if db_row is None and db_index is not None:
        db_row = db_index.get(serial_key)
    if not db_row:
        return ProtocolContextItem(
            certificate="",
            vri_id="",
            filename=filename,
            context={},
            raw_details={},
            error="serial number not found in db",
        )

    cert = str(db_row.get("Документ") or "").strip()
    if not cert:
        return ProtocolContextItem(
            certificate="",
            vri_id="",
            filename=filename,
            context={},
            raw_details={},
            error="certificate number missing in db",
        )

    protocol_number = str(db_row.get("номер_протокола") or "").strip()

    excel_cert = extract_certificate_number(row_data)
    if (
        strict_certificate_match
        and excel_cert
        and excel_cert.strip()
        and excel_cert.strip() != cert
    ):
        return ProtocolContextItem(
            certificate=excel_cert,
            vri_id="",
            filename=filename,
            context={},
            raw_details={},
            error="certificate mismatch between excel and db",
        )

    try:
        async with sem:
            search_resp = await client.get(f"{ARSHIN_BASE}/vri", params={"result_docnum": cert})
        search_resp.raise_for_status()
        found = (search_resp.json().get("result") or {}).get("items") or []
        if not found:
            return ProtocolContextItem(
                certificate=cert,
                vri_id="",
                filename=filename,
                context={},
                raw_details={},
                error="not found",
            )

        vri_id = found[0]["vri_id"]
        async with sem:
            details_resp = await client.get(f"{ARSHIN_BASE}/vri/{vri_id}")
        details_resp.raise_for_status()
        details = details_resp.json().get("result") or {}

        et_cert = await find_etalon_certificate(client, details, sem=sem)
        if et_cert:
            row_data["_resolved_etalon_cert"] = et_cert

        ctx = await build_protocol_context(row_data, details, client, session=session)
        if protocol_number:
            ctx["protocol_number"] = protocol_number

        fname = suggest_filename(ctx) or filename

        return ProtocolContextItem(
            certificate=cert,
            vri_id=vri_id,
            filename=fname,
            context=ctx,
            raw_details=details,
            error=None,
        )
    except Exception as exc:
        return ProtocolContextItem(
            certificate=cert,
            vri_id="",
            filename=filename,
            context={},
            raw_details={},
            error=str(exc),
        )


def _unique_output_path(directory: Path, base_name: str) -> Path:
    candidate = directory / base_name
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 1
    while True:
        alternative = directory / f"{stem}({counter}){suffix}"
        if not alternative.exists():
            return alternative
        counter += 1


@router.post("/context-by-excel", response_model=ProtocolContextListOut)
async def contexts_by_excel(
    file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
    session: AsyncSession = Depends(get_db),
) -> ProtocolContextListOut:
    """Строит контексты протоколов на основе Excel.

    На входе Excel с шапкой; на выходе список элементов:
      - certificate, vri_id, filename
      - context (всё для шаблонов/генерации)
      - raw_details (сырой ответ /vri/{id})
    """
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")

    # 1) читаем строки как список словарей (ключи — из первой строки)
    rows = read_rows_as_dicts(data)
    if not rows:
        return ProtocolContextListOut(items=[])

    async def process_row(row: dict[str, Any]) -> ProtocolContextItem:
        cert = extract_certificate_number(row)
        filename = suggest_filename(row)

        if not cert:
            return ProtocolContextItem(
                certificate="",
                vri_id="",
                filename=filename,
                context={},
                raw_details={},
                error="certificate number is empty",
            )

        try:
            # 2) найти VRI по номеру свидетельства (ограничиваем параллельность)
            async with sem:
                search_resp = await client.get(f"{ARSHIN_BASE}/vri", params={"result_docnum": cert})
            search_resp.raise_for_status()
            found = (search_resp.json().get("result") or {}).get("items") or []
            if not found:
                return ProtocolContextItem(
                    certificate=cert,
                    vri_id="",
                    filename=filename,
                    context={},
                    raw_details={},
                    error="not found",
                )

            vri_id = found[0]["vri_id"]

            # 3) детали по VRI (ограничиваем параллельность)
            async with sem:
                details_resp = await client.get(f"{ARSHIN_BASE}/vri/{vri_id}")
            details_resp.raise_for_status()
            details = details_resp.json().get("result") or {}

            # 4) авто-поиск свидетельства эталона с учётом семафора
            et_cert = await find_etalon_certificate(client, details, sem=sem)
            if et_cert:
                row["_resolved_etalon_cert"] = et_cert  # билдер это подхватит

            # 5) собрать контекст
            ctx = await build_protocol_context(row, details, client, session=session)

            # 6) имя файла — по контексту или по исходной строке
            fname = suggest_filename(ctx) or filename

            return ProtocolContextItem(
                certificate=cert,
                vri_id=vri_id,
                filename=fname,
                context=ctx,
                raw_details=details,
                error=None,
            )
        except Exception as e:
            return ProtocolContextItem(
                certificate=cert,
                vri_id="",
                filename=filename,
                context={},
                raw_details={},
                error=str(e),
            )

    # Параллельная обработка строк Excel с общим семафором
    items: list[ProtocolContextItem] = await asyncio.gather(*(process_row(r) for r in rows))

    # Проставим номера протоколов последовательно по файлу: 1, 2, 3, ...
    for idx, it in enumerate(items, start=1):
        ctx = it.context or {}
        if ctx:
            pn = make_protocol_number(
                ctx.get("verifier_name"),
                ctx.get("verification_date"),
                idx,
            )
            ctx["protocol_number"] = pn
            it.context = ctx

    return ProtocolContextListOut(items=items)


@router.post("/html-by-excel", response_class=HTMLResponse)
async def html_by_excel(
    file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
    session: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Возвращает HTML-протокол по первой строке Excel.

    Принимает тот же формат Excel, что и /context-by-excel.
    """
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")

    rows = read_rows_as_dicts(data)
    if not rows:
        raise HTTPException(status_code=400, detail="no rows")

    row = rows[0]
    cert = extract_certificate_number(row)
    if not cert:
        raise HTTPException(status_code=400, detail="certificate number is empty")

    # 1) найти VRI по номеру свидетельства
    async with sem:
        search_resp = await client.get(f"{ARSHIN_BASE}/vri", params={"result_docnum": cert})
    search_resp.raise_for_status()
    found = (search_resp.json().get("result") or {}).get("items") or []
    if not found:
        raise HTTPException(status_code=404, detail="not found")

    vri_id = found[0]["vri_id"]

    # 2) детали по VRI
    async with sem:
        details_resp = await client.get(f"{ARSHIN_BASE}/vri/{vri_id}")
    details_resp.raise_for_status()
    details = details_resp.json().get("result") or {}

    # 3) авто-поиск свидетельства эталона
    et_cert = await find_etalon_certificate(client, details, sem=sem)
    if et_cert:
        row["_resolved_etalon_cert"] = et_cert

    # 4) собрать контекст
    ctx = await build_protocol_context(row, details, client, session=session)

    # Номер протокола: ИНИ/ДДММГГГГ/N (для одиночного запроса N=1)
    proto_num = make_protocol_number(
        ctx.get("verifier_name"),
        ctx.get("verification_date"),
        1,
    )
    ctx["protocol_number"] = proto_num

    # Рендерим HTML
    html = render_protocol_html(ctx)

    # Сохраняем файл в output/<filename>.html
    out_dir = get_output_dir()
    base_name = suggest_filename(ctx) or suggest_filename(row) or "protocol"
    if not base_name.lower().endswith(".html"):
        base_name = f"{base_name}.html"
    out_path = _unique_output_path(out_dir, base_name)
    out_path.write_text(html, encoding="utf-8")

    return HTMLResponse(content=html, media_type="text/html")


@router.post("/controllers/pdf-files")
async def controllers_pdf_files(
    controllers_file: UploadFile = File(...),
    db_file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
    session: AsyncSession = Depends(get_db),
):
    controllers_data = await controllers_file.read()
    db_data = await db_file.read()

    if not controllers_data:
        raise HTTPException(status_code=400, detail="empty controllers file")
    if not db_data:
        raise HTTPException(status_code=400, detail="empty db file")

    rows = read_rows_as_dicts(controllers_data)
    if not rows:
        return {"files": [], "count": 0}

    db_rows = read_rows_with_required_headers(
        db_data,
        header_row=5,
        data_start_row=6,
        required_headers=DB_SERIAL_KEYS,
    )
    if not db_rows:
        raise HTTPException(status_code=400, detail="db file has no serial entries")

    await ingest_registry_rows(
        session,
        source_file=db_file.filename or "registry.xlsx",
        rows=db_rows,
        source_sheet="controllers",
    )

    registry_repo = RegistryRepository(session)

    async def process_row(row: dict[str, Any]) -> ProtocolContextItem:
        serial = _extract_first_value(row, SERIAL_SOURCE_KEYS)
        normalized_serial = normalize_serial(serial)
        db_row: Mapping[str, Any] | None = None

        if normalized_serial:
            entries = await registry_repo.find_active_by_serial(normalized_serial)
            if entries:
                entry = entries[0]
                payload = dict(entry.payload or {})
                if entry.document_no and not payload.get("Документ"):
                    payload["Документ"] = entry.document_no
                if entry.protocol_no and not payload.get("номер_протокола"):
                    payload["номер_протокола"] = entry.protocol_no
                db_row = payload

        return await _build_context_from_db(
            row,
            db_row=db_row,
            client=client,
            sem=sem,
            session=session,
            strict_certificate_match=False,
        )

    items: list[ProtocolContextItem] = await asyncio.gather(*(process_row(r) for r in rows))

    exports_dir: Path | None = None
    pdf_unavailable = False
    saved: list[str] = []
    errors: list[dict[str, object]] = []

    for idx, (it, src_row) in enumerate(zip(items, rows), start=1):
        ctx = it.context or {}
        serial = _extract_first_value(src_row, SERIAL_SOURCE_KEYS)

        if it.error or not ctx:
            errors.append(
                {
                    "row": idx,
                    "serial": serial,
                    "certificate": it.certificate,
                    "reason": it.error or "empty context",
                }
            )
            continue

        if not ctx.get("protocol_number"):
            ctx["protocol_number"] = make_protocol_number(
                ctx.get("verifier_name"),
                ctx.get("verification_date"),
                len(saved) + 1,
            )

        html = render_protocol_html(ctx)
        pdf_bytes = await html_to_pdf_bytes(html)
        if not pdf_bytes:
            pdf_unavailable = True
            errors.append(
                {
                    "row": idx,
                    "serial": serial,
                    "certificate": it.certificate,
                    "reason": "pdf generation unavailable",
                }
            )
            continue

        if exports_dir is None:
            exports_dir = get_dated_exports_dir(date.today())

        base_name = _controller_filename(ctx)
        if not base_name.lower().endswith(".pdf"):
            base_name = f"{base_name}.pdf"
        path = _unique_output_path(exports_dir, base_name)
        path.write_bytes(pdf_bytes)
        saved.append(str(path))

    if not saved and pdf_unavailable:
        raise HTTPException(
            status_code=500, detail="PDF generation is unavailable (Playwright not installed)"
        )

    return {"files": saved, "count": len(saved), "errors": errors}


@router.post("/manometers/pdf-files")
async def manometers_pdf_files(
    manometers_file: UploadFile = File(...),
    db_file: UploadFile = File(...),
    client: httpx.AsyncClient = Depends(get_http_client),
    sem: asyncio.Semaphore = Depends(get_semaphore),
    session: AsyncSession = Depends(get_db),
):
    manometers_data = await manometers_file.read()
    db_data = await db_file.read()

    if not manometers_data:
        raise HTTPException(status_code=400, detail="empty manometers file")
    if not db_data:
        raise HTTPException(status_code=400, detail="empty db file")

    rows = read_rows_as_dicts(manometers_data)
    if not rows:
        return {"files": [], "count": 0, "errors": []}

    db_rows = read_rows_with_required_headers(
        db_data,
        header_row=5,
        data_start_row=6,
        required_headers=DB_SERIAL_KEYS,
    )
    if not db_rows:
        raise HTTPException(status_code=400, detail="db file has no serial entries")

    await ingest_registry_rows(
        session,
        source_file=db_file.filename or "registry.xlsx",
        rows=db_rows,
        source_sheet="manometers",
    )

    registry_repo = RegistryRepository(session)

    async def process_row(row: dict[str, Any]) -> ProtocolContextItem:
        serial = _extract_first_value(row, SERIAL_SOURCE_KEYS)
        normalized_serial = normalize_serial(serial)
        db_row: Mapping[str, Any] | None = None

        if normalized_serial:
            entries = await registry_repo.find_active_by_serial(normalized_serial)
            if entries:
                entry = entries[0]
                payload = dict(entry.payload or {})
                if entry.document_no and not payload.get("Документ"):
                    payload["Документ"] = entry.document_no
                if entry.protocol_no and not payload.get("номер_протокола"):
                    payload["номер_протокола"] = entry.protocol_no
                db_row = payload

        return await _build_context_from_db(
            row,
            db_row=db_row,
            client=client,
            sem=sem,
            session=session,
            strict_certificate_match=True,
        )

    items: list[ProtocolContextItem] = await asyncio.gather(*(process_row(r) for r in rows))

    exports_dir: Path | None = None
    pdf_unavailable = False
    saved: list[str] = []
    errors: list[dict[str, object]] = []

    for idx, (it, src_row) in enumerate(zip(items, rows), start=1):
        ctx = it.context or {}
        serial = _extract_first_value(src_row, SERIAL_SOURCE_KEYS)

        if it.error or not ctx:
            errors.append(
                {
                    "row": idx,
                    "serial": serial,
                    "certificate": it.certificate,
                    "reason": it.error or "empty context",
                }
            )
            continue

        if not ctx.get("protocol_number"):
            ctx["protocol_number"] = make_protocol_number(
                ctx.get("verifier_name"),
                ctx.get("verification_date"),
                len(saved) + 1,
            )

        html = render_protocol_html(ctx)
        pdf_bytes = await html_to_pdf_bytes(html)
        if not pdf_bytes:
            pdf_unavailable = True
            errors.append(
                {
                    "row": idx,
                    "serial": serial,
                    "certificate": it.certificate,
                    "reason": "pdf generation unavailable",
                }
            )
            continue

        if exports_dir is None:
            exports_dir = get_dated_exports_dir(date.today())

        base_name = _filename_from_protocol_number(ctx.get("protocol_number") or "", ".pdf")
        path = _unique_output_path(exports_dir, base_name)
        path.write_bytes(pdf_bytes)
        saved.append(str(path))

    if not saved and pdf_unavailable:
        raise HTTPException(
            status_code=500, detail="PDF generation is unavailable (Playwright not installed)"
        )

    return {"files": saved, "count": len(saved), "errors": errors}

```

### 16. `app/api/routes/registry.py`

```python
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.registry_ingest import (
    REGISTRY_SERIAL_KEYS,
    ingest_registry_rows,
)
from app.utils.excel import read_rows_with_required_headers

router = APIRouter(prefix="/api/v1/registry", tags=["registry"])


@router.post("/import")
async def import_registry_file(
    db_file: UploadFile = File(...),
    *,
    source_sheet: str | None = Query(
        None,
        description="Имя листа в Excel, если нужно жёстко указать",
    ),
    instrument_kind: str | None = Query(
        None,
        description="Тип средств измерений (например, controllers, manometers)",
    ),
    header_row: int = Query(5, ge=1, description="Номер строки с заголовками"),
    data_start_row: int = Query(6, ge=1, description="Первая строка с данными"),
    session: AsyncSession = Depends(get_db),
):
    payload = await db_file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="empty registry file")

    rows = read_rows_with_required_headers(
        payload,
        header_row=header_row,
        data_start_row=data_start_row,
        required_headers=REGISTRY_SERIAL_KEYS,
    )
    if not rows:
        raise HTTPException(status_code=400, detail="registry file has no serial entries")

    result = await ingest_registry_rows(
        session,
        source_file=db_file.filename or "registry.xlsx",
        rows=rows,
        source_sheet=source_sheet,
        instrument_kind=instrument_kind,
    )

    await session.commit()

    return {
        "processed": result["processed"],
        "deactivated": result["deactivated"],
        "instrument_kind": instrument_kind or source_sheet,
        "source_file": db_file.filename or "registry.xlsx",
    }

```

### 17. `app/cli.py`

```python
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from app.db.session import get_sessionmaker
from app.services.registry_ingest import (
    REGISTRY_SERIAL_KEYS,
    ingest_registry_rows,
)
from app.utils.excel import read_rows_with_required_headers


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="metrologenerator", description="Utility commands")
    sub = parser.add_subparsers(dest="command", required=True)

    import_parser = sub.add_parser(
        "import-registry",
        help="Импортирует Excel с реестром поверок в базу данных",
    )
    import_parser.add_argument("file", help="Путь к Excel-файлу реестра")
    import_parser.add_argument(
        "--source-sheet",
        dest="source_sheet",
        default=None,
        help="Имя листа (если нужен конкретный)",
    )
    import_parser.add_argument(
        "--instrument-kind",
        dest="instrument_kind",
        default=None,
        help="Тип средств измерений (controllers, manometers и т.д.)",
    )
    import_parser.add_argument(
        "--header-row",
        dest="header_row",
        type=int,
        default=5,
        help="Номер строки с заголовками (по умолчанию 5)",
    )
    import_parser.add_argument(
        "--data-start-row",
        dest="data_start_row",
        type=int,
        default=6,
        help="Номер строки с данными (по умолчанию 6)",
    )

    return parser


async def _run_import_registry(args: argparse.Namespace) -> None:
    path = Path(args.file)
    if not path.exists():
        raise FileNotFoundError(f"registry file not found: {path}")

    payload = path.read_bytes()
    rows = read_rows_with_required_headers(
        payload,
        header_row=args.header_row,
        data_start_row=args.data_start_row,
        required_headers=REGISTRY_SERIAL_KEYS,
    )
    if not rows:
        raise ValueError("registry file has no recognizable serial number columns")

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        result = await ingest_registry_rows(
            session,
            source_file=path.name,
            rows=rows,
            source_sheet=args.source_sheet,
            instrument_kind=args.instrument_kind,
        )
        await session.commit()

    print(
        "Imported",
        result["processed"],
        "rows (deactivated:",
        result["deactivated"],
        ")",
    )


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "import-registry":
        asyncio.run(_run_import_registry(args))
    else:  # pragma: no cover - defensive; argparse enforces known commands
        parser.error(f"unknown command: {args.command}")


if __name__ == "__main__":  # pragma: no cover - manual invocation helper
    main()

```

### 18. `app/core/__init__.py`

```python

```

### 19. `app/core/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Arshin helper API"
    ARSHIN_TIMEOUT: int = 30
    ARSHIN_CONCURRENCY: int = 8
    USER_AGENT: str = "arshin-fastapi/0.1"
    DATABASE_URL: str | None = None
    EXPORTS_DIR: str = "exports"  # base folder for saved files
    SIGNATURES_DIR: str = "signatures"  # base folder for signature images

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

```

### 20. `app/core/logging.py`

```python
import sys

from loguru import logger


def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
    )
    return logger

```

### 21. `app/data/__init__.py`

```python

```

### 22. `app/data/mappings.py`

```python
from __future__ import annotations

# Пункты методики для МИ 2124-90
METHODOLOGY_POINT_MAP = {
    "МИ 2124-90": {
        "title_full": (
            "МИ 2124-90 «ГСИ. Манометры, вакуумметры, мановакуумметры, напоромеры, "
            "тягомеры и тягонапоромеры показывающие и самопишущие. Методика поверки»"
        ),
        "points": {
            "p1": "5.1",
            "p2": "5.2.3",
            "p3": "5.3",
        },
        "preferred_unit": None,
        "allowable_variation_pct": 1.50,
    }
}

# ИНН для владельцев (можно расширять)
OWNER_INN_MAP = {
    'ООО "РИ-ИНВЕСТ"': "7705551779",
}

```

### 23. `app/data/methodologies.json`

```json
{
  "МИ 2124-90": {
    "title_full": "МИ 2124-90 «ГСИ. Манометры, вакуумметры, мановакуумметры, напоромеры, тягомеры и тягонапоромеры показывающие и самопишущие. Методика поверки»",
    "points": { "p1": "5.1", "p2": "5.2.3", "p3": "5.3" },
    "allowable_variation_pct": 1.5
  },
  "МП 20-221-2021": {
    "title_full": "ГСОЕИ. Системы газоаналитические многофункциональные серии  СГМ ЭРИС-100. МП 20-221-2021",
    "points": { "p1": "8", "p2": "9", "p3": "10", "p4": "11" },
    "allowable_variation_pct": 0.1
  }
}

```

### 24. `app/data/orgs.json`

```json
{
  "ООО \"РИ-ИНВЕСТ\"": { "inn": "7705551779" }
}

```

### 25. `app/db/base.py`

```python
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

```

### 26. `app/db/models.py`

```python
from __future__ import annotations

from datetime import date, datetime
from enum import Enum as PyEnum
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    supported_fields: Mapped[dict[str, Any] | list[str] | None] = mapped_column(
        JSONB, nullable=True
    )

    protocols: Mapped[list[Protocol]] = relationship(back_populates="template")


class Owner(Base):
    __tablename__ = "owners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    inn: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)

    protocols: Mapped[list[Protocol]] = relationship(back_populates="owner")
    aliases: Mapped[list[OwnerAlias]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    instruments: Mapped[list[MeasuringInstrument]] = relationship(back_populates="owner")


class OwnerAlias(Base):
    __tablename__ = "owner_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id", ondelete="CASCADE"))
    alias: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_alias: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    owner: Mapped[Owner] = relationship(back_populates="aliases")


class VerificationRegistryEntry(Base):
    __tablename__ = "verification_registry_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_file: Mapped[str] = mapped_column(String(512), nullable=False)
    source_sheet: Mapped[str | None] = mapped_column(String(255), nullable=True)
    loaded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("now()")
    )
    row_index: Mapped[int] = mapped_column(Integer, nullable=False)
    normalized_serial: Mapped[str | None] = mapped_column(String(128), index=True)
    document_no: Mapped[str | None] = mapped_column(String(128), index=True)
    protocol_no: Mapped[str | None] = mapped_column(String(128), index=True)
    owner_name_raw: Mapped[str | None] = mapped_column(String(255))
    methodology_raw: Mapped[str | None] = mapped_column(String(255))
    instrument_kind: Mapped[str | None] = mapped_column(String(64), index=True)
    verification_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )

    instruments: Mapped[list[MeasuringInstrument]] = relationship(back_populates="registry_entry")
    protocols: Mapped[list[Protocol]] = relationship(back_populates="registry_entry")


class Methodology(Base):
    __tablename__ = "methodologies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    document: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    allowable_variation_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    aliases: Mapped[list[MethodologyAlias]] = relationship(
        back_populates="methodology", cascade="all, delete-orphan"
    )
    points: Mapped[list[MethodologyPoint]] = relationship(
        back_populates="methodology", cascade="all, delete-orphan"
    )
    instruments: Mapped[list[MeasuringInstrument]] = relationship(back_populates="methodology")


class MethodologyAlias(Base):
    __tablename__ = "methodology_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    methodology_id: Mapped[int] = mapped_column(ForeignKey("methodologies.id", ondelete="CASCADE"))
    alias: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_alias: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    weight: Mapped[int] = mapped_column(
        Integer, nullable=False, default=100, server_default=text("100")
    )

    methodology: Mapped[Methodology] = relationship(back_populates="aliases")


class MethodologyPointType(str, PyEnum):
    BOOL = "bool"
    CLAUSE = "clause"
    CUSTOM = "custom"


class MethodologyPoint(Base):
    __tablename__ = "methodology_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    methodology_id: Mapped[int] = mapped_column(ForeignKey("methodologies.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(512), nullable=False)
    point_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=MethodologyPointType.BOOL.value,
        server_default=text("'bool'"),
    )
    default_text: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    methodology: Mapped[Methodology] = relationship(back_populates="points")


class EtalonDevice(Base):
    __tablename__ = "etalon_devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reg_number: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    mitype_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacture_num: Mapped[str | None] = mapped_column(String(128), nullable=True)
    manufacture_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rank_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rank_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    schema_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    certifications: Mapped[list[EtalonCertification]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )


class EtalonCertification(Base):
    __tablename__ = "etalon_certifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    etalon_device_id: Mapped[int] = mapped_column(
        ForeignKey("etalon_devices.id", ondelete="CASCADE")
    )
    certificate_no: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    verification_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    source: Mapped[str] = mapped_column(
        String(64), nullable=False, default="arshin", server_default=text("'arshin'")
    )
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    device: Mapped[EtalonDevice] = relationship(back_populates="certifications")
    protocols: Mapped[list[Protocol]] = relationship(back_populates="etalon_certification")


class MeasuringInstrument(Base):
    __tablename__ = "measuring_instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    normalized_serial: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    designation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacture_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("owners.id", ondelete="SET NULL"), nullable=True
    )
    methodology_id: Mapped[int | None] = mapped_column(
        ForeignKey("methodologies.id", ondelete="SET NULL"), nullable=True
    )
    registry_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("verification_registry_entries.id", ondelete="SET NULL"), nullable=True
    )
    certificate_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    certificate_valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    vri_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("now()"),
        server_onupdate=text("now()"),
    )

    owner: Mapped[Owner | None] = relationship(back_populates="instruments")
    methodology: Mapped[Methodology | None] = relationship(back_populates="instruments")
    registry_entry: Mapped[VerificationRegistryEntry | None] = relationship(
        back_populates="instruments"
    )
    protocols: Mapped[list[Protocol]] = relationship(back_populates="measuring_instrument")


class Etalon(Base):
    __tablename__ = "etalons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reg_number: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    certificate: Mapped[str | None] = mapped_column(String(128), nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    protocols: Mapped[list[Protocol]] = relationship(back_populates="etalon")


class Protocol(Base):
    __tablename__ = "protocols"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    methodology: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vri_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    owner_id: Mapped[int | None] = mapped_column(ForeignKey("owners.id"))
    template_id: Mapped[int | None] = mapped_column(ForeignKey("templates.id"))
    etalon_id: Mapped[int | None] = mapped_column(ForeignKey("etalons.id"))
    registry_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("verification_registry_entries.id", ondelete="SET NULL"), nullable=True
    )
    measuring_instrument_id: Mapped[int | None] = mapped_column(
        ForeignKey("measuring_instruments.id", ondelete="SET NULL"), nullable=True
    )
    etalon_certification_id: Mapped[int | None] = mapped_column(
        ForeignKey("etalon_certifications.id", ondelete="SET NULL"), nullable=True
    )

    context: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    owner: Mapped[Owner | None] = relationship(back_populates="protocols")
    template: Mapped[Template | None] = relationship(back_populates="protocols")
    etalon: Mapped[Etalon | None] = relationship(back_populates="protocols")
    registry_entry: Mapped[VerificationRegistryEntry | None] = relationship(
        back_populates="protocols"
    )
    measuring_instrument: Mapped[MeasuringInstrument | None] = relationship(
        back_populates="protocols"
    )
    etalon_certification: Mapped[EtalonCertification | None] = relationship(
        back_populates="protocols"
    )

```

### 27. `app/db/repositories/__init__.py`

```python
from __future__ import annotations

from . import utils

__all__ = ("utils",)

try:  # pragma: no cover - executed only when SQLAlchemy installed
    from .core import (
        BaseRepository,
        EtalonRepository,
        InstrumentRepository,
        MethodologyPointPayload,
        MethodologyRepository,
        OwnerRepository,
        RegistryRepository,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    if exc.name != "sqlalchemy":
        raise
else:  # pragma: no cover - skip when SQLAlchemy missing in tests
    __all__ += (
        "BaseRepository",
        "EtalonRepository",
        "InstrumentRepository",
        "MethodologyPointPayload",
        "MethodologyRepository",
        "OwnerRepository",
        "RegistryRepository",
    )

```

### 28. `app/db/repositories/core.py`

```python
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.db import models
from app.db.models import MethodologyPointType
from app.db.repositories.utils import (
    normalize_methodology_alias,
    normalize_owner_alias,
)

__all__ = (
    "BaseRepository",
    "OwnerRepository",
    "MethodologyRepository",
    "RegistryRepository",
    "InstrumentRepository",
    "EtalonRepository",
    "MethodologyPointPayload",
)


class BaseRepository:
    """Shared helper functionality for repository classes."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, instance: models.Base, *, flush: bool = True) -> Any:
        self.session.add(instance)
        if flush:
            await self.session.flush()
        return instance


class OwnerRepository(BaseRepository):
    async def get_by_name(self, name: str) -> models.Owner | None:
        if not name:
            return None
        stmt = select(models.Owner).where(models.Owner.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_inn(self, inn: str | None) -> models.Owner | None:
        if not inn:
            return None
        stmt = select(models.Owner).where(models.Owner.inn == inn)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_alias(self, alias: str) -> models.Owner | None:
        normalized = normalize_owner_alias(alias)
        if not normalized:
            return None
        stmt = (
            select(models.Owner)
            .join(models.OwnerAlias)
            .options(joinedload(models.Owner.aliases))
            .where(models.OwnerAlias.normalized_alias == normalized)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def upsert_owner(
        self,
        *,
        name: str,
        inn: str | None = None,
        aliases: Sequence[str] | None = None,
    ) -> models.Owner:
        owner = await self.get_by_name(name)
        if owner is None:
            owner = models.Owner(name=name, inn=inn)
            await self.add(owner)
        else:
            if inn and owner.inn != inn:
                owner.inn = inn

        if aliases:
            await self.ensure_aliases(owner, aliases)
        return owner

    async def ensure_aliases(
        self, owner: models.Owner, aliases: Iterable[str]
    ) -> list[models.OwnerAlias]:
        ensured: list[models.OwnerAlias] = []
        for alias in aliases:
            normalized = normalize_owner_alias(alias)
            if not normalized:
                continue
            existing = await self._fetch_alias(normalized)
            if existing is not None:
                ensured.append(existing)
                continue

            alias_row = models.OwnerAlias(
                owner_id=owner.id,
                alias=alias,
                normalized_alias=normalized,
            )
            await self.add(alias_row)
            ensured.append(alias_row)

        return ensured

    async def _fetch_alias(self, normalized_alias: str) -> models.OwnerAlias | None:
        stmt = select(models.OwnerAlias).where(
            models.OwnerAlias.normalized_alias == normalized_alias
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


@dataclass(slots=True)
class MethodologyPointPayload:
    position: int
    label: str
    point_type: MethodologyPointType = MethodologyPointType.BOOL
    default_text: str | None = None


class MethodologyRepository(BaseRepository):
    async def get_by_code(self, code: str) -> models.Methodology | None:
        stmt = (
            select(models.Methodology)
            .options(
                selectinload(models.Methodology.points), selectinload(models.Methodology.aliases)
            )
            .where(models.Methodology.code == code)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_alias(self, alias: str) -> models.Methodology | None:
        normalized = normalize_methodology_alias(alias)
        if not normalized:
            return None
        stmt = (
            select(models.Methodology)
            .join(models.MethodologyAlias)
            .options(
                joinedload(models.Methodology.aliases),
                selectinload(models.Methodology.points),
            )
            .where(models.MethodologyAlias.normalized_alias == normalized)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def upsert_methodology(
        self,
        *,
        code: str,
        title: str,
        document: str | None = None,
        notes: str | None = None,
        allowable_variation_pct: float | None = None,
    ) -> models.Methodology:
        methodology = await self.get_by_code(code)
        if methodology is None:
            methodology = models.Methodology(
                code=code,
                title=title,
                document=document,
                notes=notes,
                allowable_variation_pct=allowable_variation_pct,
            )
            await self.add(methodology)
            return methodology

        methodology.title = title
        methodology.document = document
        methodology.notes = notes
        methodology.allowable_variation_pct = allowable_variation_pct
        return methodology

    async def ensure_aliases(
        self,
        methodology: models.Methodology,
        aliases: Iterable[tuple[str, int] | str],
    ) -> list[models.MethodologyAlias]:
        ensured: list[models.MethodologyAlias] = []
        for alias_item in aliases:
            if isinstance(alias_item, tuple):
                alias, weight = alias_item
            else:
                alias, weight = alias_item, 100

            normalized = normalize_methodology_alias(alias)
            if not normalized:
                continue

            existing = await self._fetch_alias(normalized)
            if existing is not None:
                if existing.methodology_id == methodology.id and weight != existing.weight:
                    existing.weight = weight
                ensured.append(existing)
                continue

            alias_row = models.MethodologyAlias(
                methodology_id=methodology.id,
                alias=alias,
                normalized_alias=normalized,
                weight=weight,
            )
            await self.add(alias_row)
            ensured.append(alias_row)

        return ensured

    async def replace_points(
        self,
        methodology: models.Methodology,
        points: Sequence[MethodologyPointPayload],
    ) -> None:
        await self.session.execute(
            delete(models.MethodologyPoint).where(
                models.MethodologyPoint.methodology_id == methodology.id
            )
        )

        ordered = sorted(points, key=lambda item: item.position)
        for payload in ordered:
            point_type = (
                payload.point_type.value
                if isinstance(payload.point_type, MethodologyPointType)
                else payload.point_type
            )
            if isinstance(point_type, str):
                try:
                    point_type = MethodologyPointType(point_type.lower())
                except ValueError:
                    point_type = MethodologyPointType.BOOL
            elif not isinstance(point_type, MethodologyPointType):
                point_type = MethodologyPointType.BOOL

            point_type_value = (
                point_type.value
                if isinstance(point_type, MethodologyPointType)
                else str(point_type).lower()
            )
            point = models.MethodologyPoint(
                methodology_id=methodology.id,
                position=payload.position,
                label=payload.label,
                point_type=point_type_value,
                default_text=payload.default_text,
            )
            self.session.add(point)
        await self.session.flush()

    async def _fetch_alias(self, normalized_alias: str) -> models.MethodologyAlias | None:
        stmt = select(models.MethodologyAlias).where(
            models.MethodologyAlias.normalized_alias == normalized_alias
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class RegistryRepository(BaseRepository):
    async def upsert_entry(
        self,
        *,
        source_file: str,
        row_index: int,
        values: dict[str, Any],
    ) -> models.VerificationRegistryEntry:
        stmt = select(models.VerificationRegistryEntry).where(
            models.VerificationRegistryEntry.source_file == source_file,
            models.VerificationRegistryEntry.row_index == row_index,
        )
        result = await self.session.execute(stmt)
        entry = result.scalar_one_or_none()

        if entry is None:
            entry = models.VerificationRegistryEntry(
                source_file=source_file,
                row_index=row_index,
                **values,
            )
            await self.add(entry)
        else:
            for key, value in values.items():
                setattr(entry, key, value)

        return entry

    async def deactivate_for_source(self, source_file: str) -> int:
        stmt = select(models.VerificationRegistryEntry).where(
            models.VerificationRegistryEntry.source_file == source_file,
            models.VerificationRegistryEntry.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        entries = result.scalars().all()
        for entry in entries:
            entry.is_active = False
        if entries:
            await self.session.flush()
        return len(entries)

    async def find_active_by_serial(
        self, normalized_serial: str
    ) -> list[models.VerificationRegistryEntry]:
        stmt = select(models.VerificationRegistryEntry).where(
            models.VerificationRegistryEntry.normalized_serial == normalized_serial,
            models.VerificationRegistryEntry.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class InstrumentRepository(BaseRepository):
    async def find_by_serial(self, normalized_serial: str) -> list[models.MeasuringInstrument]:
        stmt = select(models.MeasuringInstrument).where(
            models.MeasuringInstrument.normalized_serial == normalized_serial
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_instrument(
        self,
        *,
        normalized_serial: str,
        certificate_no: str | None,
        values: dict[str, Any],
    ) -> models.MeasuringInstrument:
        stmt = select(models.MeasuringInstrument).where(
            models.MeasuringInstrument.normalized_serial == normalized_serial,
            models.MeasuringInstrument.certificate_no == certificate_no,
        )
        result = await self.session.execute(stmt)
        instrument = result.scalar_one_or_none()

        if instrument is None:
            instrument = models.MeasuringInstrument(
                normalized_serial=normalized_serial,
                certificate_no=certificate_no,
                **values,
            )
            await self.add(instrument)
        else:
            for key, value in values.items():
                setattr(instrument, key, value)

        return instrument


class EtalonRepository(BaseRepository):
    async def get_device(
        self, reg_number: str, manufacture_num: str | None
    ) -> models.EtalonDevice | None:
        stmt = select(models.EtalonDevice).where(
            models.EtalonDevice.reg_number == reg_number,
            models.EtalonDevice.manufacture_num == manufacture_num,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_device(
        self,
        *,
        reg_number: str,
        manufacture_num: str | None,
        values: dict[str, Any],
    ) -> models.EtalonDevice:
        device = await self.get_device(reg_number, manufacture_num)
        if device is None:
            device = models.EtalonDevice(
                reg_number=reg_number,
                manufacture_num=manufacture_num,
                **values,
            )
            await self.add(device)
        else:
            for key, value in values.items():
                setattr(device, key, value)
        return device

    async def upsert_certification(
        self,
        *,
        device: models.EtalonDevice,
        certificate_no: str,
        values: dict[str, Any],
    ) -> models.EtalonCertification:
        stmt = select(models.EtalonCertification).where(
            models.EtalonCertification.etalon_device_id == device.id,
            models.EtalonCertification.certificate_no == certificate_no,
        )
        result = await self.session.execute(stmt)
        certification = result.scalar_one_or_none()

        if certification is None:
            certification = models.EtalonCertification(
                etalon_device_id=device.id,
                certificate_no=certificate_no,
                **values,
            )
            await self.add(certification)
        else:
            for key, value in values.items():
                setattr(certification, key, value)

        return certification

```

### 29. `app/db/repositories/utils.py`

```python
from __future__ import annotations

import re

__all__ = (
    "normalize_owner_alias",
    "normalize_methodology_alias",
    "normalize_generic",
)

# NOTE: Кириллица часто приходит с "ё". Для поиска в базе нормализуем в "е".
_TRANSLATION_TABLE = str.maketrans({"ё": "е", "Ё": "Е"})
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

```

### 30. `app/db/seed.py`

```python
from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_sessionmaker
from app.services.mappings import _methodology_seed, _org_seed, ensure_methodology, ensure_owner


async def seed_owners(session: AsyncSession) -> int:
    count = 0
    for name, payload in _org_seed().items():
        owner = await ensure_owner(
            session,
            name,
            inn_hint=str(payload.get("inn") or "") or None,
            aliases=(payload.get("aliases") or [name]),
        )
        if owner is not None:
            count += 1
    return count


async def seed_methodologies(session: AsyncSession) -> int:
    count = 0
    for code in _methodology_seed().keys():
        methodology = await ensure_methodology(session, code)
        if methodology is not None:
            count += 1
    return count


async def seed_database(session: AsyncSession) -> dict[str, int]:
    """Populate the relational database with seed data from JSON files."""

    owners = await seed_owners(session)
    methodologies = await seed_methodologies(session)
    await session.commit()
    return {"owners": owners, "methodologies": methodologies}


async def seed_from_config() -> dict[str, int]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        return await seed_database(session)


def seed():
    asyncio.run(seed_from_config())


if __name__ == "__main__":
    seed()

```

### 31. `app/db/session.py`

```python
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def _get_database_url() -> str:
    url = getattr(settings, "DATABASE_URL", None)
    if not url:
        # default to local sqlite for development
        return "sqlite+aiosqlite:///./dev.db"
    return url


def get_engine() -> AsyncEngine:
    return create_async_engine(_get_database_url(), future=True)


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    engine = get_engine()
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yields AsyncSession."""
    async_session = get_sessionmaker()
    async with async_session() as session:
        yield session

```

### 32. `app/main.py`

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.arshin import router as arshin_router
from app.api.routes.methodologies import router as methodologies_router
from app.api.routes.protocols import router as protocols_router
from app.api.routes.registry import router as registry_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.seed import seed_from_config

logger = setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        await seed_from_config()
    except Exception as exc:  # pragma: no cover - logged for observability
        logger.exception("Database seeding failed: %s", exc)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
    app.include_router(arshin_router)
    app.include_router(protocols_router)
    app.include_router(methodologies_router)
    app.include_router(registry_router)
    return app


app = create_app()

```

### 33. `app/schemas/__init__.py`

```python

```

### 34. `app/schemas/arshin.py`

```python
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class VriIdOut(BaseModel):
    certificate: str
    vri_id: str | None = None
    year_used: int | None = None
    error: str | None = None


class VriIdListOut(BaseModel):
    items: list[VriIdOut]


class VriDetailOut(BaseModel):
    certificate: str | None = None
    vri_id: str | None = None
    organization: str | None = None
    vrfDate: str | None = None
    validDate: str | None = None
    applicable: bool | None = None
    protocol_url: str | None = None
    regNumber: str | None = None
    mitypeNumber: str | None = None
    mitypeTitle: str | None = None
    mitypeType: str | None = None
    mitypeType_short: str | None = None
    manufactureNum: str | None = None
    manufactureYear: int | None = None
    rankCode: str | None = None
    rankTitle: str | None = None
    etalon_line: str | None = None
    raw: dict[str, Any] | None = None
    error: str | None = None


class VriDetailListOut(BaseModel):
    items: list[VriDetailOut]

    # Дубликаты схем протоколов удалены. Используйте app.schemas.protocol.

```

### 35. `app/schemas/methodology.py`

```python
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.db.models import MethodologyPointType


class MethodologyPointIn(BaseModel):
    position: int = Field(..., ge=1)
    label: str = Field(..., min_length=1)
    point_type: MethodologyPointType | None = None


class MethodologyCreate(BaseModel):
    code: str = Field(..., min_length=1)
    title: str | None = None
    document: str | None = None
    notes: str | None = None
    allowable_variation_pct: float | None = Field(None, ge=0)
    aliases: list[str] = Field(default_factory=list)
    points: list[MethodologyPointIn] = Field(default_factory=list)


class MethodologyPointOut(BaseModel):
    position: int
    label: str
    point_type: MethodologyPointType


class MethodologyOut(BaseModel):
    code: str
    title: str
    document: str | None
    notes: str | None
    allowable_variation_pct: float | None
    points: list[MethodologyPointOut]

    @classmethod
    def from_orm_obj(cls, obj: Any) -> MethodologyOut:
        points = [
            MethodologyPointOut(
                position=point.position,
                label=point.label,
                point_type=MethodologyPointType(point.point_type),
            )
            for point in sorted(obj.points, key=lambda p: (p.position, p.id or 0))
        ]
        return cls(
            code=obj.code,
            title=obj.title,
            document=obj.document,
            notes=obj.notes,
            allowable_variation_pct=obj.allowable_variation_pct,
            points=points,
        )

```

### 36. `app/schemas/protocol.py`

```python
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ProtocolContextItem(BaseModel):
    certificate: str | None = None  # номер свидетельства из Excel
    vri_id: str | None = None  # найденный vri_id
    filename: str | None = None  # предлагаемое имя файла (без расширения)
    context: dict[str, Any] | None = None  # полный контекст для шаблона/рендера
    raw_details: dict[str, Any] | None = None  # сырой ответ /vri/{id} (для отладки)
    error: str | None = None


class ProtocolContextListOut(BaseModel):
    items: list[ProtocolContextItem]

```

### 37. `app/services/__init__.py`

```python

```

### 38. `app/services/arshin_client.py`

```python
# app/services/arshin_client.py
from __future__ import annotations

import asyncio
import re
from datetime import date, datetime
from typing import Any

import httpx

from app.services.cache import arshin_cache

# Важно: этот BASE дергается в тестах!
ARSHIN_BASE = "https://fgis.gost.ru/fundmetrology/eapi"


# ─────────────────────────── helpers ───────────────────────────


def _safe_get(d: dict[str, Any], path: list[str], default: Any = None) -> Any:
    cur = d
    for k in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def guess_year_from_cert(cert: str) -> int | None:
    """
    Извлекаем год из номера свидетельства:
    'С-ВЯ/15-01-2025/402123271' → 2025
    """
    m = re.search(r"/(\d{2})-(\d{2})-(\d{4})/", cert)
    if m:
        return int(m.group(3))
    return None


def _fmt_date_ddmmyyyy(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, datetime | date):
        return value.strftime("%d.%m.%Y")

    txt = str(value).strip()
    try:
        return datetime.fromisoformat(txt.replace("Z", "")).strftime("%d.%m.%Y")
    except Exception:
        pass

    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d.%m.%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(txt, fmt).strftime("%d.%m.%Y")
        except Exception:
            continue
    return txt


def _split_first_notation(s: str) -> str:
    """
    'ЭЛМЕТРО-Паскаль-04, Паскаль-04' → 'ЭЛМЕТРО-Паскаль-04'
    """
    if not s:
        return ""
    return s.split(",")[0].strip()


# ─────────────────────────── core fetchers ───────────────────────────


async def fetch_vri_id_by_certificate(
    client: httpx.AsyncClient,
    cert: str,
    year: int | None = None,
    sem: asyncio.Semaphore | None = None,
    use_cache: bool = True,
) -> str | None:
    """
    Возвращает vri_id по номеру свидетельства.
    Тесты мокают GET {ARSHIN_BASE}/vri (без учёта query),
    поэтому здесь не критично, какие параметры мы реально передадим.
    """
    params = {"result_docnum": cert}
    if year:
        params["year"] = str(year)

    cache_key = ("vri", tuple(sorted(params.items())))
    if use_cache:
        cached = arshin_cache.get(cache_key)
        if cached is not None:
            return cached

    if sem:
        async with sem:
            resp = await client.get(f"{ARSHIN_BASE}/vri", params=params)
    else:
        resp = await client.get(f"{ARSHIN_BASE}/vri", params=params)
    resp.raise_for_status()
    data = resp.json() or {}
    items = _safe_get(data, ["result", "items"], default=[])
    if not items:
        return None
    first = items[0] or {}
    vri_id = first.get("vri_id")
    if vri_id and use_cache:
        arshin_cache.set(cache_key, vri_id)
    return vri_id


async def fetch_vri_details(
    client: httpx.AsyncClient,
    vri_id: str,
    sem: asyncio.Semaphore | None = None,
) -> dict[str, Any]:
    """
    Возвращает payload с ключом 'result' по vri_id.
    """
    if sem:
        async with sem:
            resp = await client.get(f"{ARSHIN_BASE}/vri/{vri_id}")
    else:
        resp = await client.get(f"{ARSHIN_BASE}/vri/{vri_id}")
    resp.raise_for_status()
    data = resp.json() or {}
    return data.get("result") or {}


# ─────────────────────────── details utils ───────────────────────────


def compose_etalon_line_from_details(details: dict[str, Any]) -> str:
    """
    Строка эталона в коротком формате:
    'регномер; обозначение; наименование; первая_часть_обозначения_типа'

    Поддерживает 2 варианта источника:
      - details['miInfo']['etaMI']  (как в тестах)
      - details['means']['mieta'][0] (как в реальных ответах Аршина)
    """
    eta = _safe_get(details, ["miInfo", "etaMI"], {})
    reg = eta.get("regNumber")
    mitype_num = eta.get("mitypeNumber")
    mitype_title = eta.get("mitypeTitle")
    notation_src = eta.get("mitypeType")

    if not reg:
        mieta_list = _safe_get(details, ["means", "mieta"], [])
        if mieta_list:
            m = mieta_list[0] or {}
            reg = m.get("regNumber", reg)
            mitype_num = m.get("mitypeNumber", mitype_num)
            mitype_title = m.get("mitypeTitle", mitype_title)
            notation_src = m.get("notation", notation_src)

    notation_first = _split_first_notation(notation_src or "")
    parts = [p for p in [reg, mitype_num, mitype_title, notation_first] if p]
    return "; ".join(parts)


def extract_detail_fields(details: dict[str, Any]) -> dict[str, Any]:
    """
    Выжимка, на которую опираются проверки:
      - organization
      - vrfDate
      - validDate
      - applicable (bool по наличию certNum)
    """
    vri = details.get("vriInfo", {}) or {}
    org = vri.get("organization") or ""
    vrf_date = vri.get("vrfDate")
    valid_date = vri.get("validDate")
    applicable = bool(_safe_get(vri, ["applicable", "certNum"]))
    return {
        "organization": org,
        "vrfDate": vrf_date,
        "validDate": valid_date,
        "applicable": applicable,
    }


# ─────────────────────────── etalon certificate resolver ───────────────────────────


async def resolve_etalon_cert_from_details(
    client: httpx.AsyncClient,
    details: dict[str, Any],
    sem: asyncio.Semaphore | None = None,
) -> dict[str, str] | None:
    """
    Автопоиск свидетельства эталона:
    GET /vri?mit_number=...&mit_title=...&mi_modification=...&mi_number=...

    Возвращает:
      {
        "docnum": "...",
        "verification_date": "ДД.ММ.ГГГГ",
        "valid_date": "ДД.ММ.ГГГГ",
        "line": "свидетельство о поверке № <docnum>; действительно до <valid_date>;"
      }
    либо None, если не найдено/недостаточно данных.
    """
    # Берём эталон либо из miInfo.etaMI, либо из means.mieta[0]
    candidates: list[dict[str, Any]] = []
    primary = _safe_get(details, ["means", "mieta"], []) or []
    if primary:
        candidates.extend([(item or {}).copy() for item in primary])

    eta = _safe_get(details, ["miInfo", "etaMI"], {}) or {}
    if eta:
        candidates.append(eta.copy())

    if not candidates:
        return None

    async def _query(params: dict[str, str]) -> dict[str, str] | None:
        cache_key = ("eta_cert_v2", tuple(sorted((str(k), str(v)) for k, v in params.items())))
        cached = arshin_cache.get(cache_key)
        if cached is not None:
            return cached

        if sem:
            async with sem:
                resp = await client.get(f"{ARSHIN_BASE}/vri", params=params)
        else:
            resp = await client.get(f"{ARSHIN_BASE}/vri", params=params)
        resp.raise_for_status()
        data = resp.json() or {}
        items = _safe_get(data, ["result", "items"], default=[]) or []
        if not items:
            return None

        for it in items:
            if not isinstance(it, dict):
                continue
            cert = it.get("result_docnum")
            valid_date_raw = it.get("valid_date") or it.get("validDate")
            if not (cert and valid_date_raw):
                continue
            vrf_date_raw = it.get("verification_date") or it.get("verificationDate")
            vrf_date = _fmt_date_ddmmyyyy(vrf_date_raw)
            valid_date = _fmt_date_ddmmyyyy(valid_date_raw)

            base_line = f"свидетельство о поверке № {cert}"
            if vrf_date:
                base_line = f"{base_line} от {vrf_date}г."
            line = f"{base_line}; действительно до {valid_date}г."
            result = {
                "docnum": cert,
                "verification_date": vrf_date,
                "valid_date": valid_date,
                "line": line,
            }
            arshin_cache.set(cache_key, result)
            return result

        return None

    for entry in candidates:
        mit_number = str(entry.get("mitypeNumber") or "").strip()
        mi_number = str(entry.get("manufactureNum") or "").strip()
        if not (mit_number and mi_number):
            continue

        base_params: dict[str, str] = {
            "mit_number": mit_number,
            "mi_number": mi_number,
        }
        mit_title = str(entry.get("mitypeTitle") or "").strip()
        if mit_title:
            base_params["mit_title"] = mit_title
        mi_mod = str(entry.get("modification") or "").strip()
        if mi_mod:
            base_params["mi_modification"] = mi_mod
        notation = str(entry.get("notation") or "").strip()
        if notation:
            base_params["mit_notation"] = notation

        manufacture_year = entry.get("manufactureYear")
        candidate_params: list[dict[str, str]] = []
        if manufacture_year:
            candidate_params.append({**base_params, "year": str(manufacture_year)})
        candidate_params.append(dict(base_params))

        # Optionally try guessed year from device certificate if available
        cert_num = _safe_get(details, ["vriInfo", "applicable", "certNum"], "")
        guessed_year = guess_year_from_cert(cert_num)
        if guessed_year and guessed_year != manufacture_year:
            candidate_params.insert(0, {**base_params, "year": str(guessed_year)})

        seen_queries: set[tuple[tuple[str, str], ...]] = set()
        for params in candidate_params:
            key = tuple(sorted((str(k), str(v)) for k, v in params.items()))
            if key in seen_queries:
                continue
            seen_queries.add(key)
            result = await _query(params)
            if result:
                return result

    return None


# Алиас для совместимости со старым импортом в protocols.py
# (Теперь и старое имя, и новое работают одинаково.)
async def find_etalon_certificate(
    client: httpx.AsyncClient,
    details: dict[str, Any],
    sem: asyncio.Semaphore | None = None,
) -> dict[str, str] | None:
    return await resolve_etalon_cert_from_details(client, details, sem=sem)

```

### 39. `app/services/cache.py`

```python
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class _Entry:
    value: Any
    expires_at: float


class TTLCache:
    """Simple in-memory TTL cache suitable for process-local caching."""

    def __init__(self, ttl_seconds: float = 600.0, max_size: int = 2048) -> None:
        self.ttl = float(ttl_seconds)
        self.max_size = int(max_size)
        self._data: dict[Any, _Entry] = {}

    def _purge(self) -> None:
        now = time.time()
        keys = [k for k, v in self._data.items() if v.expires_at <= now]
        for k in keys:
            self._data.pop(k, None)
        # size-based purge (simple FIFO by dict order)
        if len(self._data) > self.max_size:
            overflow = len(self._data) - self.max_size
            for k in list(self._data.keys())[:overflow]:
                self._data.pop(k, None)

    def get(self, key: Any) -> Any | None:
        self._purge()
        ent = self._data.get(key)
        if not ent:
            return None
        if ent.expires_at <= time.time():
            self._data.pop(key, None)
            return None
        return ent.value

    def set(self, key: Any, value: Any) -> None:
        self._purge()
        self._data[key] = _Entry(value=value, expires_at=time.time() + self.ttl)


# shared instance for Arshin lookups
arshin_cache = TTLCache(ttl_seconds=900.0, max_size=4096)

```

### 40. `app/services/generators/base.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class Tolerance(Protocol):
    """Интерфейс допуска, возвращает допустимое значение (в процентах)."""

    def value(self, *, ref: float, fsv: float, ctx: dict[str, Any]) -> float: ...


@dataclass
class FixedPctTol:
    """Постоянный допуск, %."""

    pct: float

    def value(self, *, ref: float, fsv: float, ctx: dict[str, Any]) -> float:
        return float(self.pct)


@dataclass
class GenInput:
    """Вход генератора таблицы."""

    range_min: float
    range_max: float
    unit: str
    points: int
    allowable_error: Tolerance
    allowable_variation: Tolerance
    ctx: dict[str, Any]


class TableGenerator(Protocol):
    """Интерфейс любого генератора таблицы под конкретный «шаблон»."""

    def generate(self, gi: GenInput) -> dict[str, Any]: ...

```

### 41. `app/services/generators/controller_43790_12.py`

```python
from __future__ import annotations

from random import uniform

from .base import GenInput, TableGenerator

SET_VALUES_MA: tuple[float, ...] = (4.0, 8.0, 12.0, 16.0, 20.0)
SPAN_MA: float = max(SET_VALUES_MA) - min(SET_VALUES_MA)
DELTA_LIMIT_MA: float = 0.015  # keep error within ±0.1 % относительно диапазона 16 мА


def _fmt(value: float, digits: int) -> str:
    return f"{value:.{digits}f}"


class Controller43790(TableGenerator):
    """Генератор таблицы результатов для контроллеров 43790-12."""

    def generate(self, gi: GenInput) -> dict[str, object]:
        rows: list[dict[str, str]] = []

        for idx, set_ma in enumerate(SET_VALUES_MA):
            delta = uniform(-DELTA_LIMIT_MA, DELTA_LIMIT_MA)
            measured = set_ma + delta
            error_pct = ((measured - set_ma) / SPAN_MA) * 100.0

            rows.append(
                {
                    "channel": "1" if idx == 0 else "",
                    "set_value": _fmt(set_ma, 3),
                    "measured_value": _fmt(measured, 3),
                    "error_pct": _fmt(error_pct, 3),
                }
            )

        allowable_pct = gi.allowable_error.value(ref=gi.range_max, fsv=gi.range_max, ctx=gi.ctx)

        return {
            "rows": rows,
            "unit_label": "мА",
            "allowable_error": f"{allowable_pct:.2f}",
            "allowable_note": (
                "- ± 0,1 % (0,02 мА) - пределы допускаемой приведенной погрешности в "
                "рабочих условиях"
            ),
        }


GENERATOR = Controller43790()
TEMPLATE_ID = "controller_43790_12"

```

### 42. `app/services/generators/pressure_common.py`

```python
from __future__ import annotations

from random import uniform

from .base import GenInput, TableGenerator


def _fmt_fixed(x: float, digits: int) -> str:
    """Форматирование с устранением «-0.00» при очень малых значениях.

    Если |x| < 0.5*10^-digits — считаем это нулём.
    """
    try:
        x = float(x)
    except Exception:
        return ""  # на всякий случай
    threshold = 0.5 * (10 ** (-digits))
    if abs(x) < threshold:
        x = 0.0
    return f"{x:.{digits}f}"


def _round_si(x: float) -> str:  # показания СИ
    return _fmt_fixed(x, 2)


def _round_ref(x: float) -> str:  # показания эталона
    return _fmt_fixed(x, 3)


def _clamp_err(pct: float, limit_pct: float) -> float:
    """Ограничить случайную ошибку по модулю допустимым значением."""
    lim = abs(float(limit_pct))
    p = float(pct)
    if abs(p) <= lim:
        return p
    return (lim if p > 0 else -lim) * uniform(0.70, 0.95)


class PressureCommon(TableGenerator):
    """
    Общий генератор для манометров:
      - равномерные точки 0..ВПИ
      - прямой/обратный ход на одних опорных точках
      - ошибки и вариация «внутри» допусков (отображаем допуски отдельно)
    """

    def generate(self, gi: GenInput) -> dict[str, object]:
        fsv = float(gi.range_max or 0.0)
        if fsv <= 0:
            return {
                "rows": [],
                "unit_label": gi.unit,
                "allowable_error": "",
                "allowable_variation": "",
            }

        n = max(int(gi.points or 8), 2)

        def _nice_steps(fsv: float, desired_points: int) -> list[float]:
            """Подбор «красивых» опорных точек 0..FSV.

            Пытаемся найти шаг из ряда 1,2,5×10^k, чтобы FSV делился на шаг
            и число точек было близко к desired_points. Иначе — равномерно.
            """
            desired_intervals = max(desired_points - 1, 1)
            approx_step = fsv / desired_intervals

            candidates: list[float] = []
            for k in range(-4, 5):
                base = 10**k
                for b in (1.0, 2.0, 5.0):
                    candidates.append(b * base)

            best: tuple[float, int] | None = None
            best_score = float("inf")
            for s in candidates:
                if s <= 0:
                    continue
                m = fsv / s
                m_round = int(round(m))
                if m_round <= 0:
                    continue
                if abs(m - m_round) <= 1e-6:  # шаг кратен FSV
                    points = m_round + 1
                    score = abs(points - desired_points) + 0.1 * (
                        abs(s - approx_step) / max(approx_step, 1e-9)
                    )
                    if score < best_score:
                        best = (s, points)
                        best_score = score

            if best:
                step, points = best
                return [round(i * step, 6) for i in range(points)]

            # Фоллбэк: равномерные точки
            return [round((fsv * i) / desired_intervals, 6) for i in range(desired_points)]

        steps = _nice_steps(fsv, n)
        rows: list[dict[str, object]] = []

        for i, ref_fwd in enumerate(steps):
            # Обратный ход — на той же опорной точке, что и прямой,
            # чтобы пары значений стояли в одной строке
            ref_rev = ref_fwd

            err_limit = gi.allowable_error.value(ref=ref_fwd, fsv=fsv, ctx=gi.ctx)
            # var_limit = gi.allowable_variation.value(
            #     ref=ref_fwd, fsv=fsv, ctx=gi.ctx
            # )  # для будущего

            err_fwd_pct = _clamp_err(uniform(-err_limit * 0.6, err_limit * 0.6), err_limit)
            err_rev_pct = _clamp_err(uniform(-err_limit * 0.6, err_limit * 0.6), err_limit)

            # На нулевой точке не допускаем «-0.00»/случайных знаков — считаем ровно 0
            if abs(ref_fwd) < 1e-9:
                err_fwd_pct = 0.0
            if abs(ref_rev) < 1e-9:
                err_rev_pct = 0.0

            si_fwd = ref_fwd + (err_fwd_pct / 100.0) * fsv
            si_rev = ref_rev + (err_rev_pct / 100.0) * fsv
            var_pct = abs(si_fwd - si_rev) / fsv * 100.0

            rows.append(
                {
                    "si_fwd": _round_si(si_fwd),
                    "si_rev": _round_si(si_rev),
                    "ref_fwd": _round_ref(ref_fwd),
                    "ref_rev": _round_ref(ref_rev),
                    "err_fwd": _fmt_fixed(err_fwd_pct, 2),
                    "err_rev": _fmt_fixed(err_rev_pct, 2),
                    "var_pct": _fmt_fixed(var_pct, 2),
                }
            )

        unit_label = (gi.unit or "").replace("кгc", "кгс")
        disp_err = gi.allowable_error.value(ref=fsv, fsv=fsv, ctx=gi.ctx)
        disp_var = gi.allowable_variation.value(ref=fsv, fsv=fsv, ctx=gi.ctx)

        return {
            "rows": rows,
            "unit_label": unit_label,
            "allowable_error": f"{disp_err:.2f}",
            "allowable_variation": f"{disp_var:.2f}",
        }


GENERATOR = PressureCommon()
TEMPLATE_ID = "pressure_common"

```

### 43. `app/services/generators/registry.py`

```python
from __future__ import annotations

from .base import TableGenerator
from .controller_43790_12 import GENERATOR as _CTRL43790
from .controller_43790_12 import TEMPLATE_ID as _CTRL43790_ID
from .pressure_common import GENERATOR as _PRESSURE
from .pressure_common import TEMPLATE_ID as _PRESSURE_ID


class _DefaultGenerator(TableGenerator):
    def generate(self, gi):
        err_val = gi.allowable_error.value(ref=gi.range_max, fsv=gi.range_max, ctx=gi.ctx)
        var_val = gi.allowable_variation.value(ref=gi.range_max, fsv=gi.range_max, ctx=gi.ctx)
        return {
            "rows": [],
            "unit_label": gi.unit,
            "allowable_error": f"{err_val:.2f}",
            "allowable_variation": f"{var_val:.2f}",
        }


_REGISTRY: dict[str, TableGenerator] = {}
_DEFAULT = _DefaultGenerator()


def register_template(template_id: str, generator: TableGenerator) -> None:
    _REGISTRY[template_id.strip().lower()] = generator


def get_by_template(template_id: str | None) -> TableGenerator:
    if not template_id:
        return _DEFAULT
    return _REGISTRY.get(template_id.strip().lower(), _DEFAULT)


# регистрация встроенных
register_template(_PRESSURE_ID, _PRESSURE)
register_template(_CTRL43790_ID, _CTRL43790)

```

### 44. `app/services/html_renderer.py`

```python
from __future__ import annotations
# isort: skip_file

from pathlib import Path
from typing import Any

from starlette.templating import Jinja2Templates

from app.services.templates import resolve_template_id


_BASE_DIR = Path(__file__).resolve().parent.parent
_TPL_DIR = _BASE_DIR / "templates"


def _fmt2(value: Any) -> str:
    try:
        # format with 2 decimals, dot separator; template can replace if needed
        return f"{float(value):.2f}"
    except Exception:
        return str(value)


def _build_renderer() -> Jinja2Templates:
    templates = Jinja2Templates(directory=str(_TPL_DIR))
    # register filters
    templates.env.filters["fmt2"] = _fmt2
    return templates


_templates = _build_renderer()


def _template_name_from_context(ctx: dict[str, Any]) -> str:
    method_code = (ctx.get("methodology_full") or ctx.get("method_code") or "").strip()
    mitype_number = (ctx.get("mitypeNumber") or "").strip()
    mitype_title = (ctx.get("device_info") or "").strip()
    tpl_id = resolve_template_id(method_code, mitype_number, mitype_title)

    # simple mapping id -> file
    if tpl_id == "controller_43790_12":
        return "controller_43790_12.html"
    if tpl_id == "pressure_common":
        return "manometer.html"
    return "manometer.html"


def render_protocol_html(context: dict[str, Any]) -> str:
    """Render protocol HTML using Jinja2Templates.

    The template is chosen based on context via resolve_template_id.
    """
    name = _template_name_from_context(context)

    # Normalize commonly used fields for template compatibility
    ctx = dict(context)
    # expose aliases expected by template
    ctx.setdefault("unit_label", ctx.get("unit"))
    ctx.setdefault("allowable_error", ctx.get("allowable_error_fmt"))
    # plain numeric environment values (strings acceptable too)
    ctx.setdefault("temperature_plain", ctx.get("temperature"))
    ctx.setdefault("humidity_plain", ctx.get("humidity"))
    ctx.setdefault("allowable_note", "")

    template = _templates.get_template(name)
    return template.render(ctx)

```

### 45. `app/services/mappings.py`

```python
from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.repositories import (
    MethodologyPointPayload,
    MethodologyRepository,
    OwnerRepository,
)
from app.db.repositories.utils import normalize_methodology_alias

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass(slots=True)
class MethodologyInfo:
    code: str
    title: str
    allowable_variation_pct: float | None
    points: dict[str, str]


@lru_cache(maxsize=1)
def _methodology_seed() -> dict[str, Any]:
    path = DATA_DIR / "methodologies.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _org_seed() -> dict[str, Any]:
    path = DATA_DIR / "orgs.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _core_code(text: str) -> str:
    m = re.search(r"(\d{3,5}-\d{2})", text.replace(" ", ""))
    return m.group(1) if m else text


def _match_seed(code: str) -> tuple[str, dict[str, Any]] | tuple[None, None]:
    data = _methodology_seed()
    if code in data:
        return code, data[code]
    core = _core_code(code)
    for key, payload in data.items():
        if _core_code(key) == core:
            return key, payload
    lowered = code.lower()
    for key, payload in data.items():
        if key in code or key.lower() in lowered:
            return key, payload
    return None, None


async def ensure_owner(
    session: AsyncSession,
    name: str | None,
    *,
    inn_hint: str | None = None,
    aliases: Iterable[str] | None = None,
) -> models.Owner | None:
    if not name:
        return None

    repo = OwnerRepository(session)
    owner = await repo.get_by_alias(name)
    if owner is None:
        owner = await repo.get_by_name(name)

    if owner is None:
        fallback_inn = inn_hint or (_org_seed().get(name) or {}).get("inn")
        owner = models.Owner(name=name, inn=fallback_inn)
        await repo.add(owner)
    else:
        if inn_hint and owner.inn != inn_hint:
            owner.inn = inn_hint

    alias_values = list(aliases or [])
    if name not in alias_values:
        alias_values.append(name)
    if alias_values:
        await repo.ensure_aliases(owner, alias_values)
    return owner


async def resolve_owner_inn(session: AsyncSession, name: str | None) -> str | None:
    owner = await ensure_owner(session, name)
    return owner.inn if owner else None


async def ensure_methodology(
    session: AsyncSession,
    code: str | None,
) -> models.Methodology | None:
    if not code:
        return None

    repo = MethodologyRepository(session)
    methodology = await repo.get_by_code(code)
    if methodology:
        return methodology

    seed_key, seed_payload = _match_seed(code)
    title = seed_payload.get("title_full") if seed_payload else code
    allowable = seed_payload.get("allowable_variation_pct") if seed_payload else None
    document = seed_payload.get("document") if seed_payload else None
    notes = seed_payload.get("notes") if seed_payload else None

    methodology = await repo.upsert_methodology(
        code=code,
        title=title or code,
        document=document,
        notes=notes,
        allowable_variation_pct=allowable,
    )

    await repo.ensure_aliases(
        methodology,
        [
            (code, 100),
            *(
                [(seed_key, 90)]
                if seed_key
                and normalize_methodology_alias(seed_key) != normalize_methodology_alias(code)
                else []
            ),
        ],
    )

    if seed_payload and seed_payload.get("points"):
        has_points = (
            await session.execute(
                select(models.MethodologyPoint.id)
                .where(models.MethodologyPoint.methodology_id == methodology.id)
                .limit(1)
            )
        ).scalar_one_or_none()
        if has_points:
            return await repo.get_by_code(code)
        points_payload = [
            MethodologyPointPayload(position=index, label=value)
            for index, (_, value) in enumerate(sorted(seed_payload["points"].items()), start=1)
        ]
        await repo.replace_points(methodology, points_payload)

    return await repo.get_by_code(code)


async def resolve_methodology(
    session: AsyncSession,
    code: str | None,
) -> MethodologyInfo | None:
    if not code:
        return None

    methodology = await ensure_methodology(session, code)
    if methodology is None:
        return None

    # ensure relationships are loaded (selectinload in repository handles existing ones)
    points = {
        f"p{idx}": point.label
        for idx, point in enumerate(
            sorted(methodology.points, key=lambda p: (p.position, p.id or 0)), start=1
        )
    }

    return MethodologyInfo(
        code=methodology.code,
        title=methodology.title or methodology.code,
        allowable_variation_pct=methodology.allowable_variation_pct,
        points=points,
    )


async def resolve_owner_and_inn(
    session: AsyncSession,
    name: str | None,
    *,
    inn_hint: str | None = None,
) -> tuple[str | None, str | None]:
    owner = await ensure_owner(session, name, inn_hint=inn_hint)
    if owner is None:
        return name, inn_hint
    return owner.name, owner.inn

```

### 46. `app/services/pdf.py`

```python
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
        # Явно фиксируем формат A4 в книжной ориентации.
        # Указываем точные размеры страницы, чтобы исключить авто-поворот.
        pdf_bytes = await page.pdf(
            width="210mm",
            height="297mm",
            print_background=True,
            # Уменьшаем внешние поля страницы, чтобы увеличить ширину контента
            margin={"top": "10mm", "bottom": "10mm", "left": "8mm", "right": "8mm"},
            landscape=False,
        )
        await browser.close()
        return pdf_bytes

```

### 47. `app/services/protocol_builder.py`

```python
from __future__ import annotations

import math
import re
from datetime import date, datetime
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.arshin_client import resolve_etalon_cert_from_details
from app.services.generators.base import FixedPctTol, GenInput
from app.services.generators.registry import get_by_template
from app.services.mappings import resolve_methodology, resolve_owner_and_inn
from app.services.templates import TEMPLATES, resolve_template_id
from app.utils.signatures import get_signature_render


def _norm_unit(s: str | None) -> str | None:
    if not s:
        return s
    t = s
    t = t.replace("кгc", "кгс").replace("КГC", "КГС")
    t = t.replace("кг/см²", "кгс/см²").replace("кг / см²", "кгс/см²")
    t = t.replace("см2", "см²")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _parse_range_and_unit(
    additional_info: str | None,
) -> tuple[float | None, float | None, str | None]:
    if not additional_info:
        return None, None, None
    txt = additional_info.strip()
    m = re.search(r"(-?\d+(?:[.,]\d+)?)\s*[-–]\s*(-?\d+(?:[.,]\d+)?)\s*\)?\s*(.+)?", txt)
    if not m:
        return None, None, None
    lo = float(m.group(1).replace(",", "."))
    hi = float(m.group(2).replace(",", "."))
    unit = _norm_unit((m.group(3) or "").strip())
    return lo, hi, unit or None


def _fmt_date_ddmmyyyy(s: object) -> str:
    """Возвращает дату в формате ДД.ММ.ГГГГ.

    Поддерживает входные значения:
      - datetime/date объекты
      - строки вида "ДД.ММ.ГГГГ", "ГГГГ-ММ-ДД", "ГГГГ-ММ-ДД HH:MM:SS", "ГГГГ-ММ-ДДTHH:MM:SS",
        а также "MM/DD/YYYY".
    В противном случае возвращает исходную строку.
    """
    if isinstance(s, datetime):
        return s.strftime("%d.%m.%Y")
    if isinstance(s, date):
        return s.strftime("%d.%m.%Y")

    txt = str(s or "").strip()
    if re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", txt):
        return txt

    # Популярные форматы, включая ISO с временем
    fmts = (
        "%d.%m.%Y",
        "%m/%d/%Y",
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    )
    for fmt in fmts:
        try:
            return datetime.strptime(txt, fmt).strftime("%d.%m.%Y")
        except Exception:
            continue

    # Если строка похожа на ISO, отрежем время и попробуем снова
    if re.match(r"^\d{4}-\d{2}-\d{2} ", txt):
        try:
            return datetime.strptime(txt[:10], "%Y-%m-%d").strftime("%d.%m.%Y")
        except Exception:
            pass

    return txt


def _fmt_date_ddmmyy(s: str) -> str:
    s = _fmt_date_ddmmyyyy(s or "")
    try:
        return datetime.strptime(s, "%d.%m.%Y").strftime("%d%m%y")
    except Exception:
        return ""


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(_fmt_date_ddmmyyyy(value), "%d.%m.%Y")
    except Exception:
        return None


def _split_notation(notation: str) -> tuple[str, str]:
    if not notation:
        return "", ""
    parts = [p.strip() for p in notation.split(",")]
    first = parts[0] if parts else ""
    second = parts[1] if len(parts) > 1 else ""
    return first, second


async def build_context(
    *,
    excel_row: dict[str, Any],
    details: dict[str, Any],
    methodology_points: dict[str, str],
    owner_name: str,
    owner_inn: str | None,
    allowable_error: float,
    allowable_variation: float,
    protocol_number: str | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    methodology_points = dict(methodology_points or {})
    for key in ("p1", "p2", "p3", "p4"):
        methodology_points.setdefault(key, "")

    vri = details.get("vriInfo", {}) or {}
    mi_single = (details.get("miInfo", {}) or {}).get("singleMI") or {}
    means = details.get("means", {}) or {}
    mieta_list = means.get("mieta") or []

    # Даты
    vrf_date = vri.get("vrfDate")
    valid_date_arshin = vri.get("validDate")
    verification_date = _fmt_date_ddmmyyyy(excel_row.get("Дата поверки") or vrf_date or "")
    valid_to_date = _fmt_date_ddmmyyyy(excel_row.get("Действительно до") or valid_date_arshin or "")

    # Диапазон/единица
    range_min = range_max = None
    unit = None
    range_source = None

    rng_txt = (excel_row.get("Прочие сведения") or "").strip()
    if rng_txt:
        m = re.search(
            r"\(?\s*(-?\d+(?:[.,]\d+)?)\s*[-–]\s*(-?\d+(?:[.,]\d+)?)\s*\)?\s*(.+)$", rng_txt
        )
        if m:
            range_min = float(m.group(1).replace(",", "."))
            range_max = float(m.group(2).replace(",", "."))
            unit = _norm_unit(m.group(3))
            range_source = "excel"

    if range_min is None or range_max is None or not unit:
        lo, hi, u = _parse_range_and_unit((details.get("info") or {}).get("additional_info"))
        if lo is not None and hi is not None:
            range_min, range_max, unit = lo, hi, _norm_unit(u)
            range_source = range_source or "arshin"

    # Эталон (берём первый)
    et = mieta_list[0] if mieta_list else {}
    et_reg = et.get("regNumber") or ""
    et_mitype_num = et.get("mitypeNumber") or ""
    et_title = et.get("mitypeTitle") or ""
    notation_full = (et.get("notation") or "").strip()
    notation_first, notation_second = _split_notation(notation_full)
    et_mod = et.get("modification") or ""
    et_num = et.get("manufactureNum") or ""
    et_year = str(et.get("manufactureYear") or "")
    et_rank_code = et.get("rankCode") or ""
    et_rank_title = et.get("rankTitle") or ""
    et_schema = et.get("schemaTitle") or ""

    etalon_line = "; ".join(x for x in [et_reg, et_mitype_num, et_title, notation_full] if x)
    etalon_line_top = "; ".join(x for x in [et_reg, et_mitype_num, et_title, notation_first] if x)
    if notation_second:
        etalon_line_top = f"{etalon_line_top},"
    bottom_parts = [
        notation_second or "",
        et_mod,
        et_num,
        et_year,
        et_rank_code,
        et_rank_title,
        et_schema,
    ]
    etalon_line_bottom = "; ".join([x for x in bottom_parts if x])
    if etalon_line_bottom and not etalon_line_bottom.endswith(";"):
        etalon_line_bottom += ";"

    # Свидетельство эталона: из Excel кэш или авто-поиск
    et_cert = excel_row.get("_resolved_etalon_cert") or {}
    if not et_cert and http_client:
        try:
            et_cert = await resolve_etalon_cert_from_details(http_client, details)
        except Exception:
            et_cert = {}
    et_cert_line = (et_cert or {}).get("line")

    # Свидетельство поверяемого СИ
    device_cert_line = None
    if vri.get("applicable", {}).get("certNum") and valid_date_arshin:
        device_cert_line = (
            f"свидетельство о поверке № {vri['applicable']['certNum']}; "
            f"действительно до {valid_date_arshin};"
        )

    device_info = excel_row.get("Модификация") or mi_single.get("modification") or ""
    mitype_type = (mi_single.get("mitypeType") or "").strip()
    mitype_title = (mi_single.get("mitypeTitle") or "").strip()
    if mitype_title and mitype_type:
        device_info = f"{mitype_title} {mitype_type}"
    elif mitype_title and not device_info:
        device_info = mitype_title

    context: dict[str, Any] = {
        "device_info": device_info,
        "mitypeNumber": excel_row.get("Обозначение СИ") or mi_single.get("mitypeNumber") or "",
        "manufactureNum": excel_row.get("Заводской номер") or mi_single.get("manufactureNum") or "",
        "manufactureYear": str(
            excel_row.get("Год выпуска") or mi_single.get("manufactureYear") or ""
        ),
        "owner_name": owner_name,
        "owner_inn": owner_inn or "",
        "methodology_full": excel_row.get("_methodology_full") or vri.get("docTitle") or "",
        "methodology_points": methodology_points,
        "temperature": excel_row.get("Температура") or "",
        "pressure": excel_row.get("Давление") or "",
        "humidity": excel_row.get("Влажность") or "",
        "range_min": range_min,
        "range_max": range_max,
        "unit": unit,
        "range_source": range_source,
        "measurement_range": {"min": range_min, "max": range_max},
        "measurement_unit": unit,
        "etalon_line": etalon_line,
        "etalon_line_top": etalon_line_top,
        "etalon_line_bottom": etalon_line_bottom,
        "etalon_certificate": et_cert or None,
        "etalon_certificate_line": et_cert_line,
        "etalon_rank_code": et_rank_code or None,
        "etalon_rank_title": et_rank_title or None,
        "allowable_error_pct": allowable_error,
        "allowable_error_fmt": f"{allowable_error:.2f}",
        "allowable_variation_pct": allowable_variation,
        "verification_date": verification_date,
        "valid_to_date": valid_to_date,
        "verifier_name": excel_row.get("Поверитель") or "",
        "protocol_number": protocol_number,
        "device_certificate_line": device_cert_line,
    }

    # Выбор шаблона и генерация таблицы
    method_code = (excel_row.get("Методика поверки") or vri.get("docTitle") or "").strip()
    mitype_number = context["mitypeNumber"]
    mitype_title = (details.get("miInfo", {}) or {}).get("singleMI", {}).get("mitypeTitle") or ""

    template_id = resolve_template_id(method_code, mitype_number, mitype_title) or "pressure_common"
    tpl = TEMPLATES.get(template_id, {})
    context["template_id"] = template_id

    if template_id == "controller_43790_12":
        combined_device = " ".join(x for x in [mitype_title, mitype_type] if x).strip()
        if combined_device:
            context["device_info"] = combined_device
        cert_line_text = context.get("etalon_certificate_line") or ""
        base_line = str(context.get("etalon_line") or "").replace("\n", " ").strip(" ;")
        bottom_line = str(context.get("etalon_line_bottom") or "").replace("\n", " ").strip(" ;")

        parts: list[str] = []
        if base_line:
            parts.append(base_line)
        if bottom_line:
            parts.append(bottom_line)

        combined = "; ".join(parts)
        if cert_line_text:
            combined = f"{combined}; ({cert_line_text})" if combined else f"({cert_line_text})"

        context["etalon_line_combined"] = combined
        context["etalon_line_top"] = combined
        context["etalon_line_bottom"] = ""
        context["etalon_certificate_line"] = None

        method_full = (context.get("methodology_full") or "").strip()
        target_suffix = "МП 20-221-2021"
        if method_full and target_suffix in method_full:
            idx = method_full.find(target_suffix)
            core = method_full[:idx].strip()
            suffix = method_full[idx:].strip()
            if core and not core.startswith('"'):
                core = f'"{core}"'
            context["methodology_full"] = f"{core} {suffix}".strip()
        elif method_full and not method_full.startswith('"'):
            context["methodology_full"] = f'"{method_full}"'

    ver_dt = _parse_date(context.get("verification_date"))
    val_dt = _parse_date(context.get("valid_to_date"))
    mpi_years: int | None = None
    if ver_dt and val_dt and val_dt >= ver_dt:
        days = max((val_dt - ver_dt).days, 0)
        if days == 0:
            mpi_years = 1
        else:
            mpi_years = max(1, math.ceil(days / 365))
    context["mpi_years"] = mpi_years

    points = int(excel_row.get("_points") or tpl.get("points", 8))
    err_tol = FixedPctTol(float(allowable_error))
    var_tol = FixedPctTol(float(tpl.get("allowable_variation_pct", allowable_variation)))

    gen = get_by_template(template_id)
    if gen and range_min is not None and range_max is not None:
        gi = GenInput(
            range_min=float(range_min or 0.0),
            range_max=float(range_max or 0.0),
            unit=str(unit or ""),
            points=points,
            allowable_error=err_tol,
            allowable_variation=var_tol,
            ctx={
                "template_id": template_id,
                "method_code": method_code,
                "mitype_number": mitype_number,
                "mitype_title": mitype_title,
            },
        )
        gout = gen.generate(gi)
        context.update(
            {
                "table_rows": gout.get("rows", []),
                "unit": gout.get("unit_label") or context.get("unit") or "",
                "allowable_error_fmt": gout.get("allowable_error")
                or context["allowable_error_fmt"],
                "allowable_variation": gout.get("allowable_variation")
                or f"{float(context['allowable_variation_pct']):.2f}",
            }
        )
        if "allowable_note" in gout:
            context["allowable_note"] = gout["allowable_note"]

    signature = get_signature_render(context.get("verifier_name"))
    if signature:
        context["sign_src"] = signature.src
        context["sign_style"] = signature.style
    else:
        context["sign_src"] = None
        context["sign_style"] = "display: none;"

    return context


async def build_protocol_context(*args, **kwargs) -> dict[str, Any]:
    """
    Совместимо со старым вызовом: await build_protocol_context(row, details, client)
    и с новым: await build_protocol_context(excel_row=..., details=..., ...)
    """
    session: AsyncSession | None = kwargs.pop("session", None)

    if "excel_row" in kwargs:
        return await build_context(**kwargs)

    if len(args) >= 2 and not kwargs:
        excel_row: dict[str, Any] = dict(args[0] or {})
        details: dict[str, Any] = args[1] or {}
        http_client: httpx.AsyncClient | None = args[2] if len(args) >= 3 else None
        if session is None and len(args) >= 4:
            session = args[3]

        owner_name = (
            excel_row.get("Владелец СИ") or (details.get("vriInfo", {}) or {}).get("miOwner") or ""
        )
        owner_inn: str | None = None
        if session:
            resolved_name, resolved_inn = await resolve_owner_and_inn(session, owner_name)
            if resolved_name:
                owner_name = resolved_name
            owner_inn = resolved_inn

        method_short = (
            excel_row.get("Методика поверки")
            or (details.get("vriInfo", {}) or {}).get("docTitle")
            or ""
        ).strip()
        default_points = {"p1": "5.1", "p2": "5.2.3", "p3": "5.3", "p4": ""}
        methodology_points: dict[str, str] = default_points.copy()
        allowable_hint: float | None = None

        if session and method_short:
            method_info = await resolve_methodology(session, method_short)
        else:
            method_info = None

        if method_info:
            excel_row["_methodology_full"] = method_info.title
            if method_info.points:
                methodology_points.update(method_info.points)
            allowable_hint = method_info.allowable_variation_pct
        else:
            excel_row["_methodology_full"] = method_short
            methodology_points = default_points.copy()

        try:
            allowable = float(
                str(excel_row.get("Другие параметры") or allowable_hint or "1.5").replace(",", ".")
            )
        except Exception:
            allowable = float(allowable_hint or 1.5)

        return await build_context(
            excel_row=excel_row,
            details=details,
            methodology_points=methodology_points,
            owner_name=owner_name,
            owner_inn=owner_inn or "",
            allowable_error=allowable,
            allowable_variation=allowable,
            protocol_number=None,
            http_client=http_client,
        )

    raise TypeError(
        "build_protocol_context: expected (excel_row, details[, client]) or keyword arguments"
    )


def suggest_filename(row: dict) -> str:
    sn = str(row.get("Заводской номер") or row.get("manufactureNum") or "").strip()
    date_raw = (
        row.get("Дата поверки") or row.get("verification_date") or row.get("verificationDate") or ""
    )
    date_part = _fmt_date_ddmmyy(str(date_raw))
    return f"{sn}-б-{date_part}-1"


def _initials3(full_name: str | None) -> str:
    """Возвращает 3 буквы инициалов (Ф+И+О), например:
    "Большаков С Н" → "БСН", "Иванов И.И." → "ИИИ".
    Берём первую букву первой части (фамилии) и по одной букве из следующих частей.
    """
    if not full_name:
        return ""
    # Убираем точки/лишние пробелы
    cleaned = re.sub(r"[.]+", " ", str(full_name)).strip()
    parts = [p for p in re.split(r"\s+", cleaned) if p]
    if not parts:
        return ""
    letters: list[str] = []
    # Первая буква фамилии
    letters.append(parts[0][0])
    # Первая буква каждого из последующих компонентов
    for p in parts[1:]:
        if p:
            letters.append(p[0])
        if len(letters) >= 3:
            break
    # Если частей меньше трёх, просто вернём что есть
    return "".join(letters).upper()


def _fmt_date_ddmmyyyy_no_dots(s: str | None) -> str:
    """Дата формата ДДММГГГГ без разделителей.
    Принимает строки вида "15.01.2025", "2025-01-15" и т.п.
    """
    if not s:
        return ""
    human = _fmt_date_ddmmyyyy(str(s))  # ДД.ММ.ГГГГ
    try:
        dt = datetime.strptime(human, "%d.%m.%Y")
        return dt.strftime("%d%m%Y")
    except Exception:
        # Если не распарсилось — просто уберём точки
        return human.replace(".", "")


def make_protocol_number(verifier_name: str | None, verification_date: str | None, seq: int) -> str:
    """Строит номер протокола вида: ИНИ/ДДММГГ/N (дата без разделителей, 6 знаков).

    Пример: Большаков С Н, 15.01.2025, 1 → "БСН/150125/1".
    """
    ini = _initials3(verifier_name)
    d = _fmt_date_ddmmyy(verification_date or "")
    seq_part = max(int(seq or 1), 1)
    return f"{ini}/{d}/{seq_part}"

```

### 48. `app/services/registry_ingest.py`

```python
from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import RegistryRepository
from app.services.mappings import ensure_methodology, ensure_owner
from app.utils.normalization import normalize_serial

_OWNER_KEYS = (
    "Владелец СИ",
    "Владелец",
    "Организация",
    "owner_name",
)

_OWNER_INN_KEYS = (
    "ИНН",
    "ИНН владельца",
    "ИНН владельца СИ",
    "ИНН организации",
    "inn",
)

_METHODOLOGY_KEYS = (
    "Методика поверки",
    "Методика",
    "methodology",
)

_SERIAL_KEYS = (
    "Заводской №/ Буквенно-цифровое обозначение",
    "Заводской номер",
    "Заводской №",
    "Серийный номер",
    "serial",
)

# Public alias used by API layer for header validation
REGISTRY_SERIAL_KEYS = _SERIAL_KEYS

_VERIFICATION_DATE_KEYS = (
    "Дата поверки",
    "Дата поверки по реестру",
    "verification_date",
)

_VALID_TO_KEYS = (
    "Действительно до",
    "Дата окончания",
    "valid_to",
)


def _coerce_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _extract_first(row: Mapping[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
        lower_key = key.lower()
        for existing_key, existing_value in row.items():
            if not isinstance(existing_key, str):
                continue
            if existing_key.strip().lower() == lower_key and existing_value not in (None, ""):
                return existing_value
    return None


def _ensure_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = _coerce_str(value)
    if not text:
        return None

    candidates = (
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
    )
    for fmt in candidates:
        try:
            return datetime.strptime(text, fmt).date()
        except Exception:
            continue
    return None


def _sanitize_payload(row: Mapping[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            sanitized[key] = value.isoformat()
        elif isinstance(value, date):
            sanitized[key] = value.isoformat()
        else:
            sanitized[key] = value
    return sanitized


async def ingest_registry_rows(
    session: AsyncSession,
    *,
    source_file: str,
    rows: Iterable[Mapping[str, Any]],
    source_sheet: str | None = None,
    instrument_kind: str | None = None,
) -> dict[str, int]:
    """Persist registry-like rows into the database using repository helpers."""

    registry_repo = RegistryRepository(session)

    deactivated = await registry_repo.deactivate_for_source(source_file)

    processed = 0
    for processed, row in enumerate(rows, start=1):
        owner_name = _coerce_str(_extract_first(row, _OWNER_KEYS))
        owner_inn = _coerce_str(_extract_first(row, _OWNER_INN_KEYS))
        methodology_raw = _coerce_str(_extract_first(row, _METHODOLOGY_KEYS))
        verification_date = _ensure_date(_extract_first(row, _VERIFICATION_DATE_KEYS))
        valid_to = _ensure_date(_extract_first(row, _VALID_TO_KEYS))
        document_no = _coerce_str(row.get("Документ"))
        protocol_no = _coerce_str(row.get("номер_протокола"))
        serial_raw = _extract_first(row, _SERIAL_KEYS)
        normalized_serial = normalize_serial(serial_raw)

        await registry_repo.upsert_entry(
            source_file=source_file,
            row_index=processed,
            values={
                "source_sheet": source_sheet,
                "instrument_kind": instrument_kind,
                "normalized_serial": normalized_serial or None,
                "document_no": document_no,
                "protocol_no": protocol_no,
                "owner_name_raw": owner_name,
                "methodology_raw": methodology_raw,
                "verification_date": verification_date,
                "valid_to": valid_to,
                "payload": _sanitize_payload(dict(row)),
                "is_active": True,
            },
        )

        if owner_name:
            owner = await ensure_owner(
                session,
                owner_name,
                inn_hint=owner_inn,
                aliases=[owner_name],
            )
            if owner and owner.inn:
                owner_inn = owner.inn

        if methodology_raw:
            await ensure_methodology(session, methodology_raw)

    if processed or deactivated:
        await session.commit()

    return {"processed": processed, "deactivated": deactivated}

```

### 49. `app/services/templates.py`

```python
from __future__ import annotations

# базовые шаблоны
TEMPLATES: dict[str, dict] = {
    "pressure_common": {
        "title": "Манометры / датчики давления — общий",
        "points": 8,
        "allowable_variation_pct": 1.5,
        "path": "manometer.html",
        "fields": [
            "device_info",
            "mitypeNumber",
            "manufactureNum",
            "manufactureYear",
            "owner_name",
            "methodology_full",
            "methodology_points",
            "temperature",
            "humidity",
            "pressure",
            "etalon_line_top",
            "etalon_line_bottom",
            "table_rows",
            "unit",
            "allowable_error_fmt",
            "allowable_variation",
            "verification_date",
            "verifier_name",
        ],
    },
    "controller_43790_12": {
        "title": "Контроллеры 43790-12",
        "points": 5,
        "allowable_variation_pct": 0.1,
        "path": "controller_43790_12.html",
        "fields": [
            "device_info",
            "mitypeNumber",
            "manufactureNum",
            "manufactureYear",
            "owner_name",
            "methodology_full",
            "methodology_points",
            "temperature",
            "humidity",
            "pressure",
            "etalon_line_top",
            "etalon_line_bottom",
            "table_rows",
            "allowable_note",
            "verification_date",
            "verifier_name",
        ],
    },
    # добавляй новые шаблоны ниже
    # "thermometer_mercury": {...},
    # "rtp_tsp": {...},
}


def resolve_template_id(method_code: str, mitype_number: str, mitype_title: str) -> str:
    mt = (mitype_title or "").upper()
    mn = (mitype_number or "").upper()

    # простые эвристики выбора
    if mn == "43790-12" or "СГМ ЭРИС-100" in mt:
        return "controller_43790_12"
    if "МАНОМЕТР" in mt or mn == "13535-93":
        return "pressure_common"

    # по умолчанию
    return "pressure_common"

```

### 50. `app/templates/controller_43790_12.html`

```
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Форма контроллера</title>
  </head>
  <body>
    <p class="text-center">
      Общество с ограниченной ответственностью "Многоцелевая Компания.
      Автоматизация. Исследования. Разработки"
    </p>
    <p class="text-center" id="setValue_address">
      Ханты-Мансийский автономный округ - Югра, г.о. Нижневартовск, г
      Нижневартовск, ул Индустриальная, зд. 32, стр. 1, кабинет 14
    </p>
    <p class="text-center">
      Уникальный номер записи об аккредитации в реестре аккредитованных лиц
      №RA.RU.314356
    </p>
    <p class="vh-center bold spread-header">
      ПРОТОКОЛ ПЕРИОДИЧЕСКОЙ ПОВЕРКИ №
      <span id="setValue_protocolNumber">{{ protocol_number }}</span>
    </p>
    <div class="spread-bottom">
      <p class="line text-center" id="manual_deviceInfo">
        {{ device_info }}
      </p>
      <p class="undertext">
        наименование, тип (согласно Гос. реестра СИ РФ), если в состав средства
        измерений входят несколько автономных блоков, то привести их перечень
      </p>
    </div>
    <div class="spread-bottom">
      <div class="line">
        <p class="vh-center" id="setValue_deviceTypeNumber">{{ mitypeNumber }}</p>
      </div>
      <p class="undertext">номер по Государственному реестру СИ РФ</p>
    </div>
    <div class="split-20 spread-bottom">
      <div></div>
      <div>
        <div class="line">
          <p class="vh-center" id="setValue_deviceSerial">{{ manufactureNum }}</p>
        </div>
        <p class="undertext">
          заводской номер (все цифры и буквы заводского номера)
        </p>
      </div>
    </div>
    <div class="split-20 spread-bottom">
      <div>
        <p>Год выпуска:</p>
      </div>
      <div class="line">
        <p class="vh-center" id="setValue_manufactureYear">{{ manufactureYear }}</p>
      </div>
    </div>
    <div class="split-20 spread-bottom">
      <div>
        <p>Принадлежащее:</p>
      </div>
      <div>
        <div class="line">
          <p class="h-center" id="setValue_owner">{{ owner_name }}</p>
        </div>
        <p class="undertext">
          наименование юридического/ фамилия имя и отчество физического лица-
          владельца средства измерений
        </p>
      </div>
    </div>
    <div class="split-27 spread-bottom">
      <p>Документ на методику поверки:</p>
      <div>
        <p class="line" id="manual_verificationMethodMain">
          {{ methodology_full }}
        </p>
        <p class="undertext">наименование и номер документа</p>
      </div>
    </div>
    <div class="split-17 spread-bottom">
      <p>Средства поверки:</p>
      <div>
        <p class="line" id="manual_etalonsMain">
          {{ etalon_line_combined or etalon_line_top }}
        </p>
        <p class="undertext">
          Указываются эталоны единиц величин, обеспечивающие передачу размера
          единицы величины в соответствии с поверочной схемой,
        </p>
      </div>
    </div>
    {% set temp_display = temperature_plain or temperature %}
    {% set humidity_display = humidity_plain or humidity %}
    <div class="split-20 spread-bottom">
      <p>Условия поверки:</p>
      <div>
        <p class="line" style="display: flex; gap: 15px">
          <span>температура окружающего воздуха</span>
          <span>
            <span id="setValue_temperature" data-format="N1">{{ temp_display }}</span>
            {% if temp_display and '°' not in temp_display %}°С{% endif %}
          </span>
          <span>относительная влажность</span>
          <span id="setValue_humidity" data-format="0%">
            {{ humidity_display }}{% if humidity_display and '%' not in humidity_display %}%{% endif %}
          </span>
        </p>
        <p class="undertext">
          Указываются влияющие факторы, нормированные в НД на методику поверки,
          с указанием конкретных показателей (значений)
        </p>
      </div>
    </div>
    <div class="split-20 spread-bottom">
      <div></div>
      <div class="line">
        <p style="display: flex; gap: 15px">
          <span>атмосферное давление</span
          ><span id="setValue_pressure">{{ pressure }}</span>
        </p>
      </div>
    </div>
    <div class="spread-bottom" id="manual_checkups">
      <p class="manual_checkup">
        1. Результат внешнего осмотра:
        <span style="text-decoration-line: underline">соответствует</span>/не соответствует
        п. {{ methodology_points.p1 or '8' }} МП 20-221-2021
      </p>
      <p class="manual_checkup">
        2. Опробование СИ:
        <span style="text-decoration-line: underline">соответствует</span>/не соответствует
        п. {{ methodology_points.p2 or '9' }} МП 20-221-2021
      </p>
      <p class="manual_checkup">
        3. Проверка ПО:
        <span style="text-decoration-line: underline">соответствует</span>/не соответствует
        п. {{ methodology_points.p3 or '10' }} МП 20-221-2021
      </p>
      <p class="manual_checkup">
        4. Определение метрологических характеристик:
        <span style="text-decoration-line: underline">соответствует</span>/не соответствует
        п. {{ methodology_points.p4 or '11' }} МП 20-221-2021
      </p>
    </div>
    <table class="spread-bottom-large" id="valuesTable">
      <thead>
        <tr class="header-row">
          <th>№ канала</th>
          <th>Заданное значение, мА</th>
          <th>Измеренное значение, мА</th>
          <th>Погрешность, %</th>
        </tr>
      </thead>
      <tbody>
        {% for row in table_rows %}
        <tr>
          {% if loop.first %}
          <td class="channel-cell" rowspan="{{ table_rows|length }}">{{ row.channel or '1' }}</td>
          {% endif %}
          <td>{{ row.set_value }}</td>
          <td>{{ row.measured_value }}</td>
          <td>{{ row.error_pct }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    <p class="undertext spread-bottom">{{ allowable_note }}</p>
    <p class="spread-bottom-large conclusion-line">
      Заключение: на основании результатов поверки, СИ признано
      <span class="underline">пригодным</span> к применению
    </p>
    <div class="split-15">
      <p>Дата поверки:</p>
      <div>
        <p class="line h-center" id="setValue_verificationDate">{{ verification_date }}</p>
        <p class="undertext">Указывается дата поверки в формате ДД.ММ.ГГГГ.</p>
      </div>
    </div>
    <div class="split-15">
      <p class="h-left v-bottom" style="padding-bottom: 15px">Поверитель:</p>
      <div class="sign-wrapper">
        <div
          class="line"
          style="display: flex; justify-content: space-around; margin-top: 60px"
        >
          <div>
            <img
              alt="ПОДПИСЬ"
              id="sign"
              src="{{ sign_src or '' }}"
              style="position: absolute; width: auto; {{ sign_style or 'display: none;' }}"
            />
          </div>
          <p class="v-bottom" id="setValue_worker">{{ verifier_name }}</p>
        </div>
        <div
          class="undertext"
          style="display: flex; justify-content: space-around"
        >
          <p>(подпись)</p>
          <p>(фамилия, инициалы)</p>
        </div>
      </div>
    </div>
  </body>
  <style>
    @page {
      size: A4 portrait;
    }
    body {
      padding: 1rem 1.5rem;
    }
    p {
      padding: 0;
      margin: 0;
      font-family: "Times New Roman";
      font-size: 12px;
    }
    table {
      border-collapse: collapse;
      border-spacing: 0;
      width: 100%;
      margin: 0 auto;
      font-size: 12px;
    }
    #valuesTable,
    #valuesTable th,
    #valuesTable td {
      border: 0.5pt solid #555;
    }
    #valuesTable th,
    #valuesTable td {
      text-align: center;
    }
    .spread-header {
      margin-top: 1.4rem;
      margin-bottom: 1.4rem;
      text-align: center;
    }
    .spread-bottom {
      margin-bottom: 0.2rem;
    }
    .spread-bottom-large {
      margin-bottom: 0.7rem;
    }
    .split-15,
    .split-17,
    .split-20,
    .split-25,
    .split-27,
    .split-30,
    .split-35,
    .split-50,
    .split-60 {
      display: flex;
    }
    .split-15 > *:first-child { flex: 0 0 15%; }
    .split-15 > *:last-child { flex: 0 0 85%; }
    .split-17 > *:first-child { flex: 0 0 17%; }
    .split-17 > *:last-child { flex: 0 0 83%; }
    .split-20 > *:first-child { flex: 0 0 20%; }
    .split-20 > *:last-child { flex: 0 0 80%; }
    .split-25 > *:first-child { flex: 0 0 25%; }
    .split-25 > *:last-child { flex: 0 0 75%; }
    .split-27 > *:first-child { flex: 0 0 27%; }
    .split-27 > *:last-child { flex: 0 0 73%; }
    .split-30 > *:first-child { flex: 0 0 30%; }
    .split-30 > *:last-child { flex: 0 0 70%; }
    .split-35 > *:first-child { flex: 0 0 35%; }
    .split-35 > *:last-child { flex: 0 0 65%; }
    .split-50 { justify-content: space-between; }
    .split-50 > * { flex: 1; }
    .split-60 > *:first-child { flex: 0 0 60%; }
    .split-60 > *:last-child { flex: 0 0 40%; }
    .vh-center {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .h-center {
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .h-left {
      display: flex;
      justify-content: flex-start;
    }
    .v-bottom {
      display: flex;
      align-items: flex-end;
    }
    .undertext {
      display: flex;
      align-items: flex-start;
      justify-content: center;
      font-size: 0.5rem;
      line-height: 1.1rem;
    }
    .text-center {
      text-align: center;
    }
    .bold {
      font-weight: bold;
    }
    .line {
      border-bottom: 1px solid black;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
      min-height: 1.6rem;
      padding: 0 0.2rem;
      text-align: center;
      width: 100%;
    }
    .manual_checkup {
      margin-bottom: 0.3rem;
    }
    .sign-wrapper {
      position: relative;
    }
    .channel-cell {
      font-weight: bold;
      vertical-align: middle;
    }
    .underline {
      text-decoration: underline;
    }
    .conclusion-line {
      text-align: left;
    }
  </style>
</html>

```

### 51. `app/templates/manometer.html`

```
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Форма манометра</title>
  </head>
  <body>
    <p class="text-center">
      Общество с ограниченной ответственностью "Многоцелевая Компания.
      Автоматизация. Исследования. Разработки"
    </p>
    <p class="text-center" id="setValue_address">
      Ханты-Мансийский автономный округ - Югра, г.о. Нижневартовск, г
      Нижневартовск, ул Индустриальная, зд. 32, стр. 1, кабинет 14
    </p>
    <p class="text-center">
      Уникальный номер записи об аккредитации в реестре аккредитованных лиц
      №RA.RU.314356
    </p>
    <p class="vh-center bold spread-header">
      ПРОТОКОЛ ПЕРИОДИЧЕСКОЙ ПОВЕРКИ №
      <span id="setValue_protocolNumber">{{ protocol_number }}</span>
    </p>
    <div class="spread-bottom">
      <p class="line text-center" id="manual_deviceInfo">
        {{ device_info }}
      </p>
      <p class="undertext">
        наименование, тип (согласно Гос. реестра СИ РФ), если в состав средства
        измерений входят несколько автономных блоков, то привести их перечень
      </p>
    </div>
    <div class="spread-bottom">
      <div class="line">
        <p class="vh-center" id="setValue_deviceTypeNumber">{{ mitypeNumber }}</p>
      </div>
      <p class="undertext">номер по Государственному реестру СИ РФ</p>
    </div>
    <div class="split-20 spread-bottom">
      <div></div>
      <div>
        <div class="line">
          <p class="vh-center" id="setValue_deviceSerial">{{ manufactureNum }}</p>
        </div>
        <p class="undertext">
          заводской номер (все цифры и буквы заводского номера)
        </p>
      </div>
    </div>
    <div class="split-20 spread-bottom">
      <div>
        <p>Год выпуска:</p>
      </div>
      <div class="line">
        <p class="vh-center" id="setValue_manufactureYear">{{ manufactureYear }}</p>
      </div>
    </div>
    <div class="split-20 spread-bottom">
      <div>
        <p>Принадлежащее:</p>
      </div>
      <div>
        <div class="line">
          <p class="h-center" style="gap: 10px">
            <span>
              <span id="setValue_owner">{{ owner_name }}</span>
              <span>, ИНН</span>
            </span>
            <span id="setValue_ownerINN">{{ owner_inn }}</span>
          </p>
        </div>
        <p class="undertext">
          наименование юридического/ фамилия имя и отчество физического лица-
          владельца средства измерений, ИНН/КПП
        </p>
      </div>
    </div>
    <div class="split-27 spread-bottom">
      <p>Документ на методику поверки:</p>
      <div>
        <p class="line" id="manual_verificationMethodMain">
          {{ methodology_full }}
        </p>
        <p class="undertext">наименование и номер документа</p>
      </div>
    </div>
    <div class="split-17 spread-bottom">
      <p>Средства поверки:</p>
      <div>
        <p class="line" id="manual_etalonsMain">
          {{ etalon_line_top }}
        </p>
        <p class="undertext">
          Указываются эталоны единиц величин, обеспечивающие передачу размера
          единицы величины в соответствии с поверочной схемой,
        </p>
      </div>
    </div>
    <div class="spread-bottom">
      <p class="line" id="manual_etalonsAdditional">{{ etalon_line_bottom }}</p>
      <p class="undertext spread-bottom">
        номер (все цифры и буквы регистрационного номера)
      </p>
      {% if etalon_certificate_line %}
      <p class="line" id="manual_etalonsCertificate">{{ etalon_certificate_line }}</p>
      {% endif %}
    </div>
    <div class="split-20 spread-bottom">
      <p>Условия поверки:</p>
      <div>
        <p class="line" style="display: flex; gap: 15px">
          <span>температура окружающего воздуха</span>
          <span
            ><span id="setValue_temperature" data-format="N1">{{ temperature_plain }}</span
            >°С</span
          >
          <span>относительная влажность</span>
          <span id="setValue_humidity" data-format="0%">{{ humidity_plain }}</span>
        </p>
        <p class="undertext">
          Указываются влияющие факторы, нормированные в НД на методику поверки,
          с указанием конкретных показателей (значений)
        </p>
      </div>
    </div>
    <div class="split-20 spread-bottom">
      <div></div>
      <div class="line">
        <p style="display: flex; gap: 15px">
          <span>атмосферное давление</span
          ><span id="setValue_pressure">{{ pressure }}</span>
        </p>
      </div>
    </div>
    <div class="spread-bottom" id="manual_checkups">
      <p class="manual_checkup">
        1. Результат внешнего осмотра: <span style="text-decoration-line: underline">соответствует</span>/не соответствует
        п. <span class="manual_checkupValue">{{ methodology_points.p1 }}</span> методики поверки
      </p>
      <p class="manual_checkup">
        2. Результат опробования: <span style="text-decoration-line: underline">соответствует</span>/не соответствует
        п. <span class="manual_checkupValue">{{ methodology_points.p2 }}</span> методики поверки
      </p>
      <p class="manual_checkup">
        3. Определение основной погрешности в соответствии с п. <span class="manual_checkupValue">{{ methodology_points.p3 }}</span>
        методики поверки
      </p>
    </div>
    <table class="spread-bottom-large" id="valuesTable">
      <thead>
        <tr>
          <th colspan="2">Показания поверяемого СИ</th>
          <th colspan="2">Показания эталона</th>
          <th colspan="2" rowspan="2">Приведенная погрешность, %</th>
          <th rowspan="3">Допустимая приведенная погрешность, %</th>
          <th rowspan="3">Вариация показаний, %</th>
          <th rowspan="3">Допустимая вариация, %</th>
        </tr>
        <tr class="units-row">
          <th colspan="2" id="measurementUnit1">{{ unit_label }}</th>
          <th colspan="2" id="measurementUnit2">{{ unit_label }}</th>
        </tr>
        <tr class="header-row">
          <th>прямой ход</th>
          <th>обратный ход</th>
          <th>прямой ход</th>
          <th>обратный ход</th>
          <th>прямой ход</th>
          <th>обратный ход</th>
        </tr>
      </thead>
      <tbody>
        {% for row in table_rows %}
        <tr>
          <td>{{ row.si_fwd }}</td>
          <td>{{ row.si_rev }}</td>
          <td>{{ row.ref_fwd }}</td>
          <td>{{ row.ref_rev }}</td>
          <td>{{ row.err_fwd }}</td>
          <td>{{ row.err_rev }}</td>
          <td>{{ allowable_error }}</td>
          <td>{{ row.var_pct }}</td>
          <td>{{ allowable_variation }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    <p class="spread-bottom-large">
      Заключение: на основании результатов поверки, СИ признано
      <span class="line">пригодным</span>/<span>непригодным</span>
      к применению
    </p>
    <div class="split-15">
      <p>Дата поверки:</p>
      <div>
        <p class="line h-center" id="setValue_verificationDate">{{ verification_date }}</p>
        <p class="undertext">Указывается дата поверки в формате ДД.ММ.ГГГГ.</p>
      </div>
    </div>
    <div class="split-15">
      <p class="h-left v-bottom" style="padding-bottom: 15px">Поверитель:</p>
      <div class="sign-wrapper">
        <div
          class="line"
          style="display: flex; justify-content: space-around; margin-top: 60px"
        >
          <div>
            <img
              alt="ПОДПИСЬ"
              id="sign"
              src="{{ sign_src or '' }}"
              style="position: absolute; width: auto; {{ sign_style or 'display: none;' }}"
            />
          </div>
          <p class="v-bottom" id="setValue_worker">{{ verifier_name }}</p>
        </div>
        <div
          class="undertext"
          style="display: flex; justify-content: space-around"
        >
          <p>(подпись)</p>
          <p>(фамилия, инициалы)</p>
        </div>
      </div>
    </div>
  </body>
  <style>
    /* Фиксируем формат и ориентацию страницы при печати/PDF */
    @page {
      size: A4 portrait;
      /* Отступы задаются также на уровне генератора PDF; здесь оставим по умолчанию */
    }
    body {
      /* Уменьшаем внутренние поля, чтобы увеличить полезную ширину */
      padding: 1rem 1.5rem;
    }
    p {
      padding: 0;
      margin: 0;
      font-family: "Times New Roman";
      font-size: 12px;
    }
    table {
      border-collapse: collapse;
      border-spacing: 0;
      width: 100%;
      margin: 0 auto;
      font-size: 12px;
    }
    /* Единообразные тонкие границы только для таблицы значений */
    #valuesTable,
    #valuesTable th,
    #valuesTable td {
      border: 0.5pt solid #555;
    }
    #valuesTable th,
    #valuesTable td {
      text-align: center;
    }
    #valuesTable .units-row th,
    #valuesTable .header-row th {
      border-width: 0.5pt;
    }
    .spread-header {
      margin-top: 1.4rem;
      margin-bottom: 1.4rem;
      text-align: center;
    }
    .spread-bottom {
      margin-bottom: 0.2rem;
    }
    .spread-bottom-large {
      margin-bottom: 0.7rem;
    }
    .split-15 {
      display: flex;
    }
    .split-15 > *:first-child {
      flex: 0 0 15%;
    }
    .split-15 > *:last-child {
      flex: 0 0 85%;
    }
    .split-17 {
      display: flex;
    }
    .split-17 > *:first-child {
      flex: 0 0 17%;
    }
    .split-17 > *:last-child {
      flex: 0 0 83%;
    }
    .split-20 {
      display: flex;
    }
    .split-20 > *:first-child {
      flex: 0 0 20%;
    }
    .split-20 > *:last-child {
      flex: 0 0 80%;
    }
    .split-25 {
      display: flex;
    }
    .split-25 > *:first-child {
      flex: 0 0 25%;
    }
    .split-25 > *:last-child {
      flex: 0 0 75%;
    }
    .split-27 {
      display: flex;
    }
    .split-27 > *:first-child {
      flex: 0 0 27%;
    }
    .split-27 > *:last-child {
      flex: 0 0 73%;
    }
    .split-30 {
      display: flex;
    }
    .split-30 > *:first-child {
      flex: 0 0 30%;
    }
    .split-30 > *:last-child {
      flex: 0 0 70%;
    }
    .split-35 {
      display: flex;
    }
    .split-35 > *:first-child {
      flex: 0 0 35%;
    }
    .split-35 > *:last-child {
      flex: 0 0 65%;
    }
    .split-50 {
      display: flex;
      justify-content: space-between;
    }
    .split-50 > * {
      flex: 1;
    }
    .split-60 {
      display: flex;
    }
    .split-60 > *:first-child {
      flex: 0 0 60%;
    }
    .split-60 > *:last-child {
      flex: 0 0 40%;
    }
    .v-center {
      display: flex;
      align-items: center;
    }
    .v-bottom {
      display: flex;
      align-items: flex-end;
    }
    .h-center {
      display: flex;
      justify-content: center;
    }
    .h-bottom {
      display: flex;
      align-items: flex-end;
      justify-content: center;
    }
    .vh-center {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .undertext {
      display: flex;
      align-items: flex-start;
      justify-content: center;
      font-size: 0.5rem;
    }
    .text-stretch {
      text-align: justify;
    }
    .text-center {
      text-align: center;
    }
    .bold {
      font-weight: bold;
    }
    .line {
      border-bottom: 1px solid black;
    }
    .sign-wrapper {
      position: relative;
    }
    #sign {
      position: absolute;
      width: auto;
    }
  </style>
</html>

```

### 52. `app/utils/__init__.py`

```python

```

### 53. `app/utils/excel.py`

```python
from __future__ import annotations

from collections.abc import Iterable, Mapping
from io import BytesIO
from typing import Any

from openpyxl import load_workbook

# Excel headers we accept for certificate numbers; include common typo + correct spelling.
CERTIFICATE_HEADER_KEYS: tuple[str, ...] = (
    "Номер свидетельтсва",
    "Номер свидетельства",
    "Свидетельство о поверке",
)


def read_column_as_list(
    file_bytes: bytes, column_letter: str = "P", start_row: int = 2
) -> list[str]:
    """
    Читает колонку (по умолчанию P) со start_row, убирает пустые и дубликаты (сохраняя порядок).
    """
    wb = load_workbook(filename=BytesIO(file_bytes), data_only=True)
    ws = wb.active
    items = []
    col = column_letter.upper()

    for row in range(start_row, ws.max_row + 1):
        val = ws[f"{col}{row}"].value
        if val is None:
            continue
        s = str(val).strip()
        if s:
            items.append(s)

    seen = set()
    uniq = []
    for x in items:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def _normalized_header(values: Iterable[str]) -> set[str]:
    return {str(value).strip().lower() for value in values if value}


def _extract_header(ws, header_row: int) -> list[str]:
    header_row = max(int(header_row or 1), 1)
    if header_row > ws.max_row:
        return []

    header: list[str] = []
    for cell in ws[header_row]:
        val = cell.value
        header.append(str(val).strip() if val is not None else "")
    return header


def _sheet_rows(ws, header: list[str], start_row: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for r in ws.iter_rows(min_row=start_row, values_only=True):
        if all(v is None or str(v).strip() == "" for v in r):
            continue
        item: dict[str, object] = {}
        for i, key in enumerate(header):
            if not key:
                continue
            if i < len(r):
                item[key] = r[i]
        rows.append(item)
    return rows


def read_rows_as_dicts(
    file_bytes: bytes,
    *,
    header_row: int = 1,
    data_start_row: int | None = None,
    sheet: str | None = None,
) -> list[dict[str, object]]:
    """
    Читает указанный лист (по умолчанию активный) как список словарей.

    :param header_row: Номер строки (1-based), содержащей заголовки.
    :param data_start_row: Первая строка с данными; по умолчанию header_row + 1.
    :param sheet: Имя листа. Если None — используется активный лист.
    Пустые строки пропускаются.
    """
    wb = load_workbook(filename=BytesIO(file_bytes), data_only=True)
    try:
        ws = wb[sheet] if sheet else wb.active
        header = _extract_header(ws, header_row)
        start_row = int(data_start_row) if data_start_row else header_row + 1
        return _sheet_rows(ws, header, start_row)
    finally:
        wb.close()


def read_rows_with_required_headers(
    file_bytes: bytes,
    *,
    header_row: int = 1,
    data_start_row: int | None = None,
    required_headers: tuple[str, ...] | None = None,
) -> list[dict[str, object]]:
    """
    Перебирает все листы файла и возвращает строки первого листа,
    содержащего любой из required_headers (без учёта регистра/пробелов).
    Если подходящий лист не найден — возвращает пустой список.
    """

    wb = load_workbook(filename=BytesIO(file_bytes), data_only=True)
    try:
        wanted = _normalized_header(required_headers or [])
        for ws in wb.worksheets:
            header = _extract_header(ws, header_row)
            if wanted:
                normalized = _normalized_header(header)
                if not (normalized & wanted):
                    continue
            start_row = int(data_start_row) if data_start_row else header_row + 1
            rows = _sheet_rows(ws, header, start_row)
            if rows:
                return rows
        return []
    finally:
        wb.close()


def extract_certificate_number(row: Mapping[str, Any]) -> str:
    """Return trimmed certificate number from supported header variants."""

    normalized = {str(key).strip().lower(): value for key, value in row.items() if key}
    for header in CERTIFICATE_HEADER_KEYS:
        value = row.get(header)
        if value is None:
            value = normalized.get(header.lower())
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""

```

### 54. `app/utils/normalization.py`

```python
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

```

### 55. `app/utils/paths.py`

```python
from __future__ import annotations

from datetime import date
from pathlib import Path

from app.core.config import settings


def get_project_root() -> Path:
    # app/utils/paths.py -> utils -> app -> project root
    return Path(__file__).resolve().parents[2]


def get_exports_base() -> Path:
    root = get_project_root()
    base = root / settings.EXPORTS_DIR
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_dated_exports_dir(today: date | None = None) -> Path:
    d = today or date.today()
    base = get_exports_base()
    target = base / d.isoformat()
    target.mkdir(parents=True, exist_ok=True)
    return target


def get_output_dir() -> Path:
    """Папка для временного сохранения HTML/сырого вывода до внедрения БД.

    По требованию — корень проекта /output.
    """
    root = get_project_root()
    out = root / "output"
    out.mkdir(parents=True, exist_ok=True)
    return out

```

### 56. `app/utils/signatures.py`

```python
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

# Базовая геометрия и небольшая вариация, чтобы подпись всегда помещалась внутри строки.
_TOP_BASE = 38.0
_TOP_JITTER = 2.0  # ±px

_LEFT_BASE = 48.0
_LEFT_JITTER = 8.0

_HEIGHT_BASE = 26.0
_HEIGHT_JITTER = 2.0

_ROTATION_BASE = 0.0
_ROTATION_JITTER = 2.5


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

    top = _with_jitter(_TOP_BASE, _TOP_JITTER)
    left = _with_jitter(_LEFT_BASE, _LEFT_JITTER)
    height = max(10.0, _with_jitter(_HEIGHT_BASE, _HEIGHT_JITTER))
    rotation = _with_jitter(_ROTATION_BASE, _ROTATION_JITTER)

    style = (
        "display: block; "
        f"top: {top:.1f}px; "
        f"left: {left:.1f}px; "
        f"height: {height:.1f}px; "
        f"transform: rotate({rotation:.1f}deg);"
    )

    return SignatureRender(src=src, style=style)


def _clear_caches_for_tests() -> None:
    _signature_entries.cache_clear()
    _data_uri_for.cache_clear()

```

### 57. `data/attachments/Davlenie.html`

```
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Форма датчик давления</title>
  </head>
  <body>
    <p class="vh-center">
      Общество с ограниченной ответственностью "Многоцелевая Компания.
      Автоматизация. Исследования. Разработки"
    </p>
    <p class="vh-center" id="setValue_address">
      Ханты-Мансийский автономный округ - Югра, г.о. Нижневартовск, г
      Нижневартовск, ул Индустриальная, зд. 32, стр. 1, кабинет 14
    </p>
    <p class="vh-center">
      Уникальный номер записи об аккредитации в реестре аккредитованных лиц
      №RA.RU.314356
    </p>
    <p class="vh-center bold spread-header">
      ПРОТОКОЛ ПЕРИОДИЧЕСКОЙ ПОВЕРКИ №
      <span id="setValue_protocolNumber">25/012/22</span>
    </p>
    <div class="spread-bottom">
      <p class="line text-center" id="manual_deviceInfo">
        Манометры деформационные с трубчатой пружиной 2 Манометры деформационные
        с трубчатой пружиной 2 Ман
      </p>
      <p class="undertext">
        наименование, тип (согласно Гос. реестра СИ РФ), если в состав средства
        измерений входят несколько автономных блоков, то привести их перечень
      </p>
    </div>
    <div class="spread-bottom">
      <div class="line">
        <p class="vh-center" id="setValue_deviceTypeNumber">55984-13</p>
      </div>
      <p class="undertext">номер по Государственному реестру СИ РФ</p>
    </div>
    <div class="split-20 spread-bottom">
      <div>
        <p>Заводской номер:</p>
      </div>
      <div>
        <div class="line">
          <p class="vh-center" id="setValue_deviceSerial">05322</p>
        </div>
        <p class="undertext">
          заводской номер (все цифры и буквы заводского номера)
        </p>
      </div>
    </div>
    <div class="split-20 spread-bottom">
      <div>
        <p>Год выпуска:</p>
      </div>
      <div class="line">
        <p class="vh-center" id="setValue_manufactureYear">2015</p>
      </div>
    </div>
    <div class="split-20 spread-bottom">
      <div>
        <p>Принадлежащее:</p>
      </div>
      <div>
        <div class="line">
          <p class="h-center" style="gap: 10px">
            <span>
              <span id="setValue_owner">ООО "РИ-ИНВЕСТ"</span>
              <span>, ИНН</span>
            </span>
            <span id="setValue_ownerINN">7705551779</span>
          </p>
        </div>
        <p class="undertext">
          наименование юридического/ фамилия имя и отчество физического лица-
          владельца средства измерений, ИНН/КПП
        </p>
      </div>
    </div>
    <div class="split-27 spread-bottom">
      <p>Документ на методику поверки:</p>
      <div>
        <p class="line" id="manual_verificationMethodMain">
          МИ 2124-90 ГСИ. Манометры, вакуумметры, мановакуумметры, тягомеры и
        </p>
        <p class="undertext">наименование и номер документа</p>
      </div>
    </div>
    <div class="spread-bottom">
      <p class="line" id="manual_verificationMethodAdditional">
        тягомеры и тягонапоромеры показывающие и самопишущие. Методика поверки
        документа напоромеры, тягомеры
      </p>
    </div>
    <div class="split-17 spread-bottom">
      <p>Средства поверки:</p>
      <div>
        <p class="line" id="manual_etalonsMain">
          77090.19.2Р.00761950; 77090-19; Преобразователи давления эталонные;
        </p>
        <p class="undertext">
          Указываются эталоны единиц величин, обеспечивающие передачу размера
          единицы величины в соответствии с поверочной схемой,
        </p>
      </div>
    </div>
    <div class="spread-bottom-large">
      <p class="line" id="manual_etalonsAdditional">
        ЭЛМЕТРО-Паскаль-04, Паскаль-04; 2022 г. 7М-0,02-Т35; 3110; 2020; 2Р;
        Эталон 2-го разряда; Приказ Росстандарта
      </p>
      <p class="undertext spread-bottom">
        их наименование, регистрационный номер (все цифры и буквы
        регистрационного номера)
      </p>
    </div>
    <div class="spread-bottom">
      <p>Условия поверки:</p>
    </div>
    <div class="split-45 spread-bottom">
      <p>Температура окружающей среды</p>
      <p><span id="setValue_temperature" data-format="N1">25</span>°С</p>
    </div>
    <div class="split-45 spread-bottom">
      <p>Относительная влажность окружающей среды</p>
      <p id="setValue_humidity" data-format="0%">25</p>
    </div>
    <div class="split-45 spread-bottom-large">
      <p>Атмосферное давление</p>
      <p id="setValue_pressure">25 кПа</p>
    </div>
    <div class="spread-bottom">
      <p class="text-stretch" id="manual_checkup">
        <span id="manual_checkupNum">1. </span>
        <span id="manual_checkupTitle"
          >Определение основной приведенной погрешности и вариации</span
        >: <span style="text-decoration-line: underline">соответствует</span>/не
        соответствует п. <span id="manual_checkupValue">5.1</span> методики
        поверки
        <span id="manual_checkupVerification"
          >ГСИ. Преобразователи давления измерительные EJX. Методика
          поверки</span
        >
      </p>
    </div>
    <div class="spread-bottom-large"></div>
    <table class="spread-bottom-large" id="valuesTable">
      <thead>
        <tr>
          <th rowspan="2">№ измерения</th>
          <th colspan="2">Задаваемое давление</th>
          <th colspan="2">Измеренное значение сигнала, мА</th>
          <th colspan="2">Приведенная погрешность, %</th>
          <th rowspan="2">Допустимая приведенная погрешность, %</th>
          <th rowspan="2">Вариация выходного сигнала γ, %</th>
        </tr>
        <tr class="header-row">
          <th id="measurementUnit">bar</th>
          <th>мА</th>
          <th>пр. ход</th>
          <th>обр. ход</th>
          <th>пр. ход</th>
          <th>обр. ход</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>1</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td rowspan="5">0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>2</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td style="display: none">0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>3</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td style="display: none">0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>4</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td style="display: none">0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>5</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td style="display: none">0</td>
          <td>0</td>
        </tr>
      </tbody>
    </table>
    <p class="spread-bottom-large">
      Заключение: на основании результатов поверки, СИ признано
      <span class="line">пригодным</span>/<span>непригодным</span>
      к применению
    </p>
    <p>
      Дата поверки: <span id="setValue_verificationDate">28.03.2024</span>г.
    </p>
    <div class="split-15">
      <p class="h-left v-bottom" style="padding-bottom: 15px">Поверитель:</p>
      <div class="sign-wrapper">
        <div
          class="line"
          style="display: flex; justify-content: space-around; margin-top: 60px"
        >
          <div>
            <img alt="ПОДПИСЬ" id="sign" src="test большаков с.н. 1.png" />
            <!-- <img alt="ПОДПИСЬ" id="sign" src="test запевахин т.е. 1.png" />
            <img alt="ПОДПИСЬ" id="sign" src="test кадыков п.ю. 1.png" />
            <img alt="ПОДПИСЬ" id="sign" src="test манджеев а.а. 1.png" />
            <img alt="ПОДПИСЬ" id="sign" src="test тиора в.а. 1.png" />
            <img alt="ПОДПИСЬ" id="sign" src="test чупин а.а. 1.png" /> -->
          </div>
          <p class="v-bottom" id="setValue_worker">Иванов Иван Иванович</p>
        </div>
        <div
          class="undertext"
          style="display: flex; justify-content: space-around"
        >
          <p>(подпись)</p>
          <p>(фамилия, инициалы)</p>
        </div>
      </div>
    </div>
  </body>
  <style>
    body {
      padding: 2rem 5rem;
    }
    p {
      padding: 0;
      margin: 0;
      font-family: "Times New Roman";
      font-size: 12px;
    }
    table {
      border-collapse: collapse;
      width: 100%;
      margin: 0 auto;
      font-size: 12px;
    }
    th,
    td {
      border: 1px solid black;
      text-align: center;
    }
    .spread-header {
      margin-top: 1.4rem;
      margin-bottom: 1.4rem;
    }
    .spread-bottom {
      margin-bottom: 0.2rem;
    }
    .spread-bottom-large {
      margin-bottom: 0.7rem;
    }
    .split-15 {
      display: flex;
    }
    .split-15 > *:first-child {
      flex: 0 0 15%;
    }
    .split-15 > *:last-child {
      flex: 0 0 85%;
    }
    .split-17 {
      display: flex;
    }
    .split-17 > *:first-child {
      flex: 0 0 17%;
    }
    .split-17 > *:last-child {
      flex: 0 0 83%;
    }
    .split-20 {
      display: flex;
    }
    .split-20 > *:first-child {
      flex: 0 0 20%;
    }
    .split-20 > *:last-child {
      flex: 0 0 80%;
    }
    .split-25 {
      display: flex;
    }
    .split-25 > *:first-child {
      flex: 0 0 25%;
    }
    .split-25 > *:last-child {
      flex: 0 0 75%;
    }
    .split-27 {
      display: flex;
    }
    .split-27 > *:first-child {
      flex: 0 0 27%;
    }
    .split-27 > *:last-child {
      flex: 0 0 73%;
    }
    .split-30 {
      display: flex;
    }
    .split-30 > *:first-child {
      flex: 0 0 30%;
    }
    .split-30 > *:last-child {
      flex: 0 0 70%;
    }
    .split-35 {
      display: flex;
    }
    .split-35 > *:first-child {
      flex: 0 0 35%;
    }
    .split-35 > *:last-child {
      flex: 0 0 65%;
    }
    .split-37 {
      display: flex;
    }
    .split-37 > *:first-child {
      flex: 0 0 37%;
    }
    .split-37 > *:last-child {
      flex: 0 0 63%;
    }
    .split-40 {
      display: flex;
    }
    .split-40 > *:first-child {
      flex: 0 0 40%;
    }
    .split-40 > *:last-child {
      flex: 0 0 60%;
    }
    .split-45 {
      display: flex;
    }
    .split-45 > *:first-child {
      flex: 0 0 45%;
    }
    .split-45 > *:last-child {
      flex: 0 0 55%;
    }
    .split-50 {
      display: flex;
      justify-content: space-between;
    }
    .split-50 > * {
      flex: 1;
    }
    .split-60 {
      display: flex;
    }
    .split-60 > *:first-child {
      flex: 0 0 60%;
    }
    .split-60 > *:last-child {
      flex: 0 0 40%;
    }
    .v-center {
      display: flex;
      align-items: center;
    }
    .v-bottom {
      display: flex;
      align-items: flex-end;
    }
    .h-center {
      display: flex;
      justify-content: center;
    }
    .h-bottom {
      display: flex;
      align-items: flex-end;
      justify-content: center;
    }
    .vh-center {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .undertext {
      display: flex;
      align-items: flex-start;
      justify-content: center;
      font-size: 0.5rem;
    }
    .text-stretch {
      text-align: justify;
    }
    .text-center {
      text-align: center;
    }
    .bold {
      font-weight: bold;
    }
    .line {
      border-bottom: 1px solid black;
    }
    .sign-wrapper {
      position: relative;
    }
    #sign {
      position: absolute;
      top: 30px; /* 20 - 30 */
      left: 150px; /* 30 - 150 */
      height: 33px; /* 31 - 33 */
      width: auto;
    }
  </style>
</html>

```

### 58. `data/attachments/DavlenieSuccessDocumentCreator.cs`

```csharp
using System.Reflection;
using Infrastructure.DocumentProcessor.Forms;
using ProjApp.ProtocolForms;
using PuppeteerSharp;

namespace Infrastructure.DocumentProcessor.Creator;

internal class DavlenieSuccessDocumentCreator : DocumentCreatorBase<DavlenieForm>
{
    protected override IReadOnlyList<PropertyInfo> TypeProps { get; init; } = typeof(DavlenieForm).GetProperties();

    public DavlenieSuccessDocumentCreator(
        Browser browser,
        Dictionary<string, string> signsCache,
        string signsDirPath)
            : base(browser,
                   signsCache,
                   signsDirPath,
                   HTMLForms.Davlenie)
    { }

    protected override async Task<string?> SetSpecificAsync(IPage page, DavlenieForm data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name == "MeasurementUnit");
        if (prop == null) return "MeasurementUnit prop not found";

        var measurementElement = await page.QuerySelectorAsync("#measurementUnit");
        if (measurementElement == null) return "measurementUnit not found";
        await measurementElement.SetElementValueAsync(prop.GetValue(data)!.ToString()!);

        var table = await page.QuerySelectorAsync("#valuesTable");
        if (table == null) return "Таблица не найдена";

        var tbody = await table.QuerySelectorAsync("tbody");
        if (tbody == null) return "Таблица не содержит строк";

        var columnFormats = new Dictionary<int, string>
    {
        { 1, "N1" }, // Давление
        { 2, "N3" }, // Показания эталона
        { 3, "N3" }, // Показания устройства (прямой ход)
        { 4, "N3" }, // Показания устройства (обратный ход)
        { 5, "N3" }, // Приведенная погрешность (прямой ход)
        { 6, "N3" }, // Приведенная погрешность (обратный ход)
        { 7, "N3" }, // Допустимая приведенная погрешность
        { 8, "N3" }  // Вариация показаний
    };

        for (int rowIndex = 0; rowIndex < 5; rowIndex++)
        {
            var rows = await tbody.QuerySelectorAllAsync("tr");
            if (rowIndex >= rows.Length) continue;

            var row = rows[rowIndex];
            if (row == null) continue;

            for (int colIndex = 1; colIndex < 9; colIndex++)
            {
                var cell = await row.QuerySelectorAsync($"td:nth-child({colIndex + 1})");
                if (cell == null) return "Ячейка таблицы не найдена";

                var innerHtml = await cell.EvaluateFunctionAsync<string>("el => el.innerHTML");
                if (innerHtml.Trim() == "-") continue;

                double value = colIndex switch
                {
                    1 => data.PressureInputs[rowIndex],
                    2 => data.EtalonValues[rowIndex],
                    3 => data.DeviceValues[0][rowIndex],
                    4 => data.DeviceValues[1][rowIndex],
                    5 => data.ActualError[0][rowIndex],
                    6 => data.ActualError[1][rowIndex],
                    7 => data.ValidError,
                    8 => data.Variations[rowIndex],
                    _ => throw new Exception("Некорректный индекс столбца")
                };

                await cell.SetElementValueAsync(value.ToString(), columnFormats[colIndex]);
            }
        }

        return null;
    }
}

```

### 59. `data/attachments/DocumentCreatorBase.cs`

```csharp
using System.Reflection;
using ProjApp.Database.Entities;
using PuppeteerSharp;

namespace Infrastructure.DocumentProcessor.Creator;

// TODO: Replace reflection with the source generator
internal abstract class DocumentCreatorBase<T>
{
    private readonly Browser _browser;
    private readonly string _htmlForm;
    private readonly Dictionary<string, string> _signsCache;
    private readonly string _signsDirPath;
    protected abstract IReadOnlyList<PropertyInfo> TypeProps { get; init; }

    public DocumentCreatorBase(Browser browser, Dictionary<string, string> signsCache, string signsDirPath, string formPath)
    {
        _browser = browser;
        _signsCache = signsCache;
        _signsDirPath = signsDirPath;
        _htmlForm = File.ReadAllText(formPath);
    }

    public async Task<HTMLCreationResult> CreateAsync(T data)
    {
        var page = await _browser.CreatePageAsync();
        await page.SetContentAsync(_htmlForm);

        var result = await SetDeviceAsync(page, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        result = await SetAutoElementsAsync(page, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        result = await SetVerificationAsync(page, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        result = await SetEtalonsAsync(page, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        result = await SetCheckupsAsync(page, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        result = await SetSignAsync(page, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        result = await SetSpecificAsync(page, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        return HTMLCreationResult.Success(page);
    }

    protected abstract Task<string?> SetSpecificAsync(IPage page, T data);

    private async Task<string?> SetDeviceAsync(IPage page, T data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name.Equals("deviceInfo", StringComparison.OrdinalIgnoreCase));
        if (prop == null) return "Data property deviceInfo not found";
        var deviceInfo = prop.GetValue(data)!.ToString()!;

        var result = await page.SetElementTextAsync("#manual_deviceInfo", deviceInfo);
        if (!result) return "Cannot set text in manual_deviceInfo";

        return null;
    }

    private async Task<string?> SetAutoElementsAsync(IPage page, T data)
    {
        var elements = await page.QuerySelectorAllAsync("[id]");
        foreach (var element in elements)
        {
            var id = await element.EvaluateFunctionAsync<string>("el => el.id");
            if (id.StartsWith("setValue_"))
            {
                var propName = id["setValue_".Length..].ToLower();
                var prop = TypeProps.FirstOrDefault(t => t.Name.Equals(propName, StringComparison.OrdinalIgnoreCase));
                if (prop == null)
                {
                    return $"Data property {propName} not found";
                }

                var value = prop.GetValue(data)?.ToString() ?? string.Empty;
                await element.SetElementValueAsync(value);
            }
        }

        return null;
    }

    private async Task<string?> SetVerificationAsync(IPage page, T data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name.Equals("verificationsinfo", StringComparison.OrdinalIgnoreCase));
        if (prop == null) return "Data property verificationsinfo not found";
        var verificationsText = prop.GetValue(data)!.ToString()!;

        var (success, remainingText) = await page.SetElementTextExactAsync("#manual_verificationMethodMain", verificationsText);
        if (!success) return "Verifications text cannot be set";
        if (remainingText.Length == 0)
        {
            var removeResult = await page.RemoveElementAsync("#manual_verificationMethodAdditional");
            if (removeResult != null) return removeResult;
            return null;
        }

        var result = await page.SetElementTextAsync("#manual_verificationMethodAdditional", remainingText);
        if (!result) return "Verifications text cannot be set";

        return null;
    }

    private async Task<string?> SetEtalonsAsync(IPage page, T data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name.Equals("EtalonsInfo", StringComparison.OrdinalIgnoreCase));
        if (prop == null) return "Data property EtalonsInfo not found";
        var etalonsText = prop.GetValue(data)!.ToString()!;

        var (success, remainingText) = await page.SetElementTextExactAsync("#manual_etalonsMain", etalonsText);
        if (!success) return "Etalons text cannot be set";
        if (remainingText.Length == 0) return null;

        var result = await page.SetElementTextAsync("#manual_etalonsAdditional", remainingText);
        if (!result) return "Etalons text cannot be set";

        return null;
    }

    private async Task<string?> SetCheckupsAsync(IPage page, T data)
    {
        try
        {
            var verificationInfoProp = TypeProps.FirstOrDefault(p => p.Name.Equals("VerificationsInfo", StringComparison.OrdinalIgnoreCase));
            if (verificationInfoProp == null) return "Data property VerificationsInfo not found";
            var verificationsInfo = verificationInfoProp.GetValue(data)!.ToString()!;

            var checkupsProp = TypeProps.FirstOrDefault(p => p.Name.Equals("Checkups", StringComparison.OrdinalIgnoreCase));
            if (checkupsProp == null) return "Data property Checkups not found";
            var checkups = (Dictionary<string, CheckupType>)checkupsProp.GetValue(data)!;

            return await page.EvaluateFunctionAsync<string?>(@"(checkupsData, verificationsInfo) => {
            const template = document.getElementById('manual_checkup');
            if (!template) return 'Template element not found';
            
            const container = template.parentElement;
            if (!container) return 'Container not found';
            
            // Clear container but keep template structure
            container.innerHTML = '';
            container.appendChild(template);

            const hasVerifCheckup = template.querySelector('#manual_checkupVerification') !== null
                
            let index = 0;
            for (const [key, checkup] of Object.entries(checkupsData)) {
                const element = index === 0 ? template : template.cloneNode(true);
                
                const numE = `<span id=""manual_checkupNum"">${index + 1}. </span>`;
                const titleE = `<span id=""manual_checkupTitle"">${key}</span>`;

                const valueE = checkup.type === 'Fact' 
                    ? ' в соответствии с п. <span id=""manual_checkupValue"">' + checkup.value + '</span> методики поверки'
                    : ': <span style=""text-decoration-line: underline"">соответствует</span>/не соответствует п. <span id=""manual_checkupValue"">' + checkup.value + '</span> методики поверки';

                const verInfo = hasVerifCheckup ? ' ' + verificationsInfo : '';
                element.innerHTML = numE + titleE + valueE + verInfo;

                if (index > 0) {
                    container.appendChild(element);
                }
                index++;
            }

            return null;
        }", checkups, verificationsInfo);
        }
        catch (Exception ex)
        {
            return $"Error setting checkups: {ex.Message}";
        }
    }

    private async Task<string?> SetSignAsync(IPage page, T data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name == "Worker");
        if (prop == null) return "Data property Worker not found";
        var worker = (string)prop.GetValue(data)!;
        worker = worker.ToLower();

        var strictSignsCount = 12;
        var randomSignIndex = Random.Shared.Next(1, strictSignsCount);
        var key = $"{worker} {randomSignIndex}";

        if (!_signsCache.TryGetValue(key, out var sign))
        {
            var filePath = Path.Combine(_signsDirPath, $"{key}.png");
            if (!File.Exists(filePath)) return $"Подпись сотрудника {worker} не найдена. Или вариантов меньше 12";
            var bytes = await File.ReadAllBytesAsync(filePath);
            var base64 = Convert.ToBase64String(bytes);
            var signBase64 = $"data:image/png;base64,{base64}";
            sign = _signsCache[key] = signBase64;
        }

        try
        {
            var randomTop = Random.Shared.Next(20, 30);
            var randomLeft = Random.Shared.Next(30, 150);
            var randomHeight = Random.Shared.Next(31, 33);

            await page.EvaluateFunctionAsync(@"(signSrc, top, left, height) => {
                const imgElement = document.querySelector('#sign');
                if (imgElement) {
                    imgElement.style.cssText = `top: ${top}px; left: ${left}px; height: ${height}px;`;
                    imgElement.src = signSrc;
                }
            }", sign, randomTop, randomLeft, randomHeight);
        }
        catch (Exception ex)
        {
            return $"Error setting signature image: {ex.Message}";
        }

        return null;
    }
}

```

### 60. `data/attachments/Forms.cs`

```csharp
namespace Infrastructure.DocumentProcessor.Forms;

internal static class HTMLForms
{
    public static string Manometr { get; } = "Manometr.html".GetFormPath();
    public static string Davlenie { get; } = "Davlenie.html".GetFormPath();
}



```

### 61. `data/attachments/HTMLCreationResult.cs`

```csharp
using PuppeteerSharp;

namespace Infrastructure.DocumentProcessor.Creator;

internal class HTMLCreationResult
{
    public IPage? HTMLPage { get; init; }
    public string? Error { get; init; }

    private HTMLCreationResult() { }

    public static HTMLCreationResult Success(IPage htmlPage) => new() { HTMLPage = htmlPage };
    public static HTMLCreationResult Failure(string error) => new() { Error = error };
}

```

### 62. `data/attachments/Manometr.html`

```
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Форма манометра</title>
  </head>
  <body>
    <p class="vh-center">
      Общество с ограниченной ответственностью "Многоцелевая Компания.
      Автоматизация. Исследования. Разработки"
    </p>
    <p class="vh-center" id="setValue_address">
      Ханты-Мансийский автономный округ - Югра, г.о. Нижневартовск, г
      Нижневартовск, ул Индустриальная, зд. 32, стр. 1, кабинет 14
    </p>
    <p class="vh-center">
      Уникальный номер записи об аккредитации в реестре аккредитованных лиц
      №RA.RU.314356
    </p>
    <p class="vh-center bold spread-header">
      ПРОТОКОЛ ПЕРИОДИЧЕСКОЙ ПОВЕРКИ №
      <span id="setValue_protocolNumber">25/012/22</span>
    </p>
    <div class="spread-bottom">
      <p class="line text-center" id="manual_deviceInfo">
        Манометры деформационные с трубчатой пружиной 2 Манометры деформационные
        с трубчатой пружиной 2 Ман
      </p>
      <p class="undertext">
        наименование, тип (согласно Гос. реестра СИ РФ), если в состав средства
        измерений входят несколько автономных блоков, то привести их перечень
      </p>
    </div>
    <div class="spread-bottom">
      <div class="line">
        <p class="vh-center" id="setValue_deviceTypeNumber">55984-13</p>
      </div>
      <p class="undertext">номер по Государственному реестру СИ РФ</p>
    </div>
    <div class="split-20 spread-bottom">
      <div></div>
      <div>
        <div class="line">
          <p class="vh-center" id="setValue_deviceSerial">05322</p>
        </div>
        <p class="undertext">
          заводской номер (все цифры и буквы заводского номера)
        </p>
      </div>
    </div>
    <div class="split-20 spread-bottom">
      <div>
        <p>Год выпуска:</p>
      </div>
      <div class="line">
        <p class="vh-center" id="setValue_manufactureYear">2015</p>
      </div>
    </div>
    <div class="split-20 spread-bottom">
      <div>
        <p>Принадлежащее:</p>
      </div>
      <div>
        <div class="line">
          <p class="h-center" style="gap: 10px">
            <span>
              <span id="setValue_owner">ООО "РИ-ИНВЕСТ"</span>
              <span>, ИНН</span>
            </span>
            <span id="setValue_ownerINN">7705551779</span>
          </p>
        </div>
        <p class="undertext">
          наименование юридического/ фамилия имя и отчество физического лица-
          владельца средства измерений, ИНН/КПП
        </p>
      </div>
    </div>
    <div class="split-27 spread-bottom">
      <p>Документ на методику поверки:</p>
      <div>
        <p class="line" id="manual_verificationMethodMain">
          МИ 2124-90 ГСИ. Манометры, вакуумметры, мановакуумметры, тягомеры и
        </p>
        <p class="undertext">наименование и номер документа</p>
      </div>
    </div>
    <div class="spread-bottom">
      <p class="line" id="manual_verificationMethodAdditional">
        документа напоромеры, тягомеры и тягонапоромеры показывающие и
        самопишущие.
      </p>
    </div>
    <div class="split-17 spread-bottom">
      <p>Средства поверки:</p>
      <div>
        <p class="line" id="manual_etalonsMain">
          77090.19.2Р.00761950; 77090-19; Преобразователи давления эталонные;
        </p>
        <p class="undertext">
          Указываются эталоны единиц величин, обеспечивающие передачу размера
          единицы величины в соответствии с поверочной схемой,
        </p>
      </div>
    </div>
    <div class="spread-bottom">
      <p class="line" id="manual_etalonsAdditional">
        ЭЛМЕТРО-Паскаль-04, Паскаль-04; 2022 г. 7М-0,02-Т35; 3110; 2020; 2Р;
        Эталон 2-го разряда; Приказ Росстандарта
      </p>
      <p class="undertext spread-bottom">
        номер (все цифры и буквы регистрационного номера)
      </p>
    </div>
    <div class="split-20 spread-bottom">
      <p>Условия поверки:</p>
      <div>
        <p class="line" style="display: flex; gap: 15px">
          <span>температура окружающего воздуха</span>
          <span
            ><span id="setValue_temperature" data-format="N1">22,9</span
            >°С</span
          >
          <span>относительная влажность</span>
          <span id="setValue_humidity" data-format="0%">42</span>
        </p>
        <p class="undertext">
          Указываются влияющие факторы, нормированные в НД на методику поверки,
          с указанием конкретных показателей (значений)
        </p>
      </div>
    </div>
    <div class="split-20 spread-bottom">
      <div></div>
      <div class="line">
        <p style="display: flex; gap: 15px">
          <span>атмосферное давление</span
          ><span id="setValue_pressure">101,2 кПа</span>
        </p>
      </div>
    </div>
    <div class="spread-bottom">
      <p id="manual_checkup">
        <span id="manual_checkupNum">1. </span>
        <span id="manual_checkupTitle"
          >Определение основной приведенной погрешности и вариации</span
        >: <span style="text-decoration-line: underline">соответствует</span>/не
        соответствует п. <span id="manual_checkupValue">5.1</span> методики
        поверки
      </p>
    </div>
    <table class="spread-bottom-large" id="valuesTable">
      <thead>
        <tr>
          <th colspan="2">Показания поверяемого СИ</th>
          <th colspan="2">Показания эталона</th>
          <th colspan="2" rowspan="2">Приведенная погрешность, %</th>
          <th rowspan="3">Допустимая приведенная погрешность, %</th>
          <th rowspan="3">Вариация показаний, %</th>
          <th rowspan="3">Допустимая вариация, %</th>
        </tr>
        <tr class="units-row">
          <th colspan="2" id="measurementUnit1">bar</th>
          <th colspan="2" id="measurementUnit2">bar</th>
        </tr>
        <tr class="header-row">
          <th>прямой ход</th>
          <th>обратный ход</th>
          <th>прямой ход</th>
          <th>обратный ход</th>
          <th>прямой ход</th>
          <th>обратный ход</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>-</td>
          <td>-</td>
        </tr>
        <tr>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>-</td>
          <td>-</td>
        </tr>
      </tbody>
    </table>
    <p class="spread-bottom-large">
      Заключение: на основании результатов поверки, СИ признано
      <span class="line">пригодным</span>/<span>непригодным</span>
      к применению
    </p>
    <div class="split-15">
      <p>Дата поверки:</p>
      <div>
        <p class="line h-center" id="setValue_verificationDate">28.03.2024</p>
        <p class="undertext">Указывается дата поверки в формате ЧЧ.ММ.ГГГГ.</p>
      </div>
    </div>
    <div class="split-15">
      <p class="h-left v-bottom" style="padding-bottom: 15px">Поверитель:</p>
      <div class="sign-wrapper">
        <div
          class="line"
          style="display: flex; justify-content: space-around; margin-top: 60px"
        >
          <div>
            <img alt="ПОДПИСЬ" id="sign" src="test большаков с.н. 1.png" />
            <!-- <img alt="ПОДПИСЬ" id="sign" src="test запевахин т.е. 1.png" />
            <img alt="ПОДПИСЬ" id="sign" src="test кадыков п.ю. 1.png" />
            <img alt="ПОДПИСЬ" id="sign" src="test манджеев а.а. 1.png" />
            <img alt="ПОДПИСЬ" id="sign" src="test тиора в.а. 1.png" />
            <img alt="ПОДПИСЬ" id="sign" src="test чупин а.а. 1.png" /> -->
          </div>
          <p class="v-bottom" id="setValue_worker">Иванов Иван Иванович</p>
        </div>
        <div
          class="undertext"
          style="display: flex; justify-content: space-around"
        >
          <p>(подпись)</p>
          <p>(фамилия, инициалы)</p>
        </div>
      </div>
    </div>
  </body>
  <style>
    body {
      padding: 2rem 5rem;
    }
    p {
      padding: 0;
      margin: 0;
      font-family: "Times New Roman";
      font-size: 12px;
    }
    table {
      border-collapse: collapse;
      width: 100%;
      margin: 0 auto;
      font-size: 12px;
    }
    th,
    td {
      border: 1px solid black;
      text-align: center;
    }
    .spread-header {
      margin-top: 1.4rem;
      margin-bottom: 1.4rem;
    }
    .spread-bottom {
      margin-bottom: 0.2rem;
    }
    .spread-bottom-large {
      margin-bottom: 0.7rem;
    }
    .split-15 {
      display: flex;
    }
    .split-15 > *:first-child {
      flex: 0 0 15%;
    }
    .split-15 > *:last-child {
      flex: 0 0 85%;
    }
    .split-17 {
      display: flex;
    }
    .split-17 > *:first-child {
      flex: 0 0 17%;
    }
    .split-17 > *:last-child {
      flex: 0 0 83%;
    }
    .split-20 {
      display: flex;
    }
    .split-20 > *:first-child {
      flex: 0 0 20%;
    }
    .split-20 > *:last-child {
      flex: 0 0 80%;
    }
    .split-25 {
      display: flex;
    }
    .split-25 > *:first-child {
      flex: 0 0 25%;
    }
    .split-25 > *:last-child {
      flex: 0 0 75%;
    }
    .split-27 {
      display: flex;
    }
    .split-27 > *:first-child {
      flex: 0 0 27%;
    }
    .split-27 > *:last-child {
      flex: 0 0 73%;
    }
    .split-30 {
      display: flex;
    }
    .split-30 > *:first-child {
      flex: 0 0 30%;
    }
    .split-30 > *:last-child {
      flex: 0 0 70%;
    }
    .split-35 {
      display: flex;
    }
    .split-35 > *:first-child {
      flex: 0 0 35%;
    }
    .split-35 > *:last-child {
      flex: 0 0 65%;
    }
    .split-50 {
      display: flex;
      justify-content: space-between;
    }
    .split-50 > * {
      flex: 1;
    }
    .split-60 {
      display: flex;
    }
    .split-60 > *:first-child {
      flex: 0 0 60%;
    }
    .split-60 > *:last-child {
      flex: 0 0 40%;
    }
    .v-center {
      display: flex;
      align-items: center;
    }
    .v-bottom {
      display: flex;
      align-items: flex-end;
    }
    .h-center {
      display: flex;
      justify-content: center;
    }
    .h-bottom {
      display: flex;
      align-items: flex-end;
      justify-content: center;
    }
    .vh-center {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .undertext {
      display: flex;
      align-items: flex-start;
      justify-content: center;
      font-size: 0.5rem;
    }
    .text-stretch {
      text-align: justify;
    }
    .text-center {
      text-align: center;
    }
    .bold {
      font-weight: bold;
    }
    .line {
      border-bottom: 1px solid black;
    }
    .sign-wrapper {
      position: relative;
    }
    #sign {
      position: absolute;
      top: 30px; /* 20 - 30 */
      left: 150px; /* 30 - 150 */
      height: 33px; /* 31 - 33 */
      width: auto;
    }
  </style>
</html>

```

### 63. `data/attachments/ManometrDocumentCreator.cs`

```csharp
using System.Reflection;
using Infrastructure.DocumentProcessor.Forms;
using ProjApp.ProtocolForms;
using PuppeteerSharp;

namespace Infrastructure.DocumentProcessor.Creator;

internal class ManometrSuccessDocumentCreator : DocumentCreatorBase<ManometrForm>
{
    protected override IReadOnlyList<PropertyInfo> TypeProps { get; init; } = typeof(ManometrForm).GetProperties();

    public ManometrSuccessDocumentCreator(
        Browser browser,
        Dictionary<string, string> signsCache,
        string signsDirPath)
            : base(browser,
                   signsCache,
                   signsDirPath,
                   HTMLForms.Manometr)
    { }

    protected override async Task<string?> SetSpecificAsync(IPage page, ManometrForm data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name == "MeasurementUnit");
        if (prop == null) return "MeasurementUnit prop not found";

        var measurement1Element = await page.QuerySelectorAsync("#measurementUnit1");
        if (measurement1Element == null) return "measurementUnit1 not found";
        await measurement1Element.SetElementValueAsync(prop.GetValue(data)!.ToString()!);

        var measurement2Element = await page.QuerySelectorAsync("#measurementUnit2");
        if (measurement2Element == null) return "measurementUnit2 not found";
        await measurement2Element.SetElementValueAsync(prop.GetValue(data)!.ToString()!);

        var table = await page.QuerySelectorAsync("#valuesTable");
        if (table == null)
        {
            return "Table not found";
        }

        var tbody = await table.QuerySelectorAsync("tbody");
        if (tbody == null)
        {
            return "Table body not found";
        }

        var columnFormats = new Dictionary<int, string>
        {
            { 0, "N2" }, // Показания поверяемого СИ (прямой ход)
            { 1, "N2" }, // Показания поверяемого СИ (обратный ход)
            { 2, "N3" }, // Показания эталона (прямой ход)
            { 3, "N3" }, // Показания эталона (обратный ход)
            { 4, "N2" }, // Приведенная погрешность (прямой ход)
            { 5, "N2" }, // Приведенная погрешность (обратный ход)
            { 6, "N2" }, // Допустимая приведенная погрешность
            { 7, "N2" }, // Вариация показаний
            { 8, "N2" }  // Допустимая вариация
        };

        for (int rowIndex = 0; rowIndex < 8; rowIndex++)
        {
            var rows = await tbody.QuerySelectorAllAsync("tr");
            if (rowIndex >= rows.Length) continue;

            var row = rows[rowIndex];
            if (row == null) continue;

            for (int colIndex = 0; colIndex < 9; colIndex++)
            {
                var cell = await row.QuerySelectorAsync($"td:nth-child({colIndex + 1})");
                if (cell == null) continue;

                var innerHtml = await cell.EvaluateFunctionAsync<string>("el => el.innerHTML");
                if (innerHtml.Trim() == "-") continue;

                var value = colIndex switch
                {
                    0 => data.DeviceValues[0][rowIndex],
                    1 => data.DeviceValues[1][rowIndex],
                    2 => data.EtalonValues[0][rowIndex],
                    3 => data.EtalonValues[1][rowIndex],
                    4 => data.ActualError[0][rowIndex],
                    5 => data.ActualError[1][rowIndex],
                    6 => data.ValidError,
                    7 => data.ActualVariation[rowIndex],
                    8 => data.ValidError,
                    _ => throw new Exception("Некорректный индекс столбца")
                };

                await cell.SetElementValueAsync(value.ToString(), columnFormats[colIndex]);
            }
        }

        return null;
    }
}

```

### 64. `data/attachments/PageManipulationExtensions.cs`

```csharp
using PuppeteerSharp;

namespace Infrastructure.DocumentProcessor.Creator;

internal static class PageManipulationExtensions
{
    public static async Task<(bool Success, string RemainingText)> SetElementTextExactAsync(this IPage page, string selector, string text)
    {
        try
        {
            var result = await page.EvaluateFunctionAsync<TextFitResult>(@"(selector, fullText) => {
            const element = document.querySelector(selector);
            if (!element) return { success: false, fittedText: '', remainingText: fullText };

            // Save original styles for measurement
            const style = window.getComputedStyle(element);
            const maxWidth = element.clientWidth;
            const maxHeight = element.clientHeight;
            
            // Create measurement element with identical styling
            const measurer = element.cloneNode(true);
            measurer.style.position = 'absolute';
            measurer.style.visibility = 'hidden';
            document.body.appendChild(measurer);

            // Find last space position where text fits
            let lastValidSpace = -1;
            let currentPosition = 0;
            let remainingText = fullText;
            let fittedText = '';

            // Check whole text first
            measurer.textContent = fullText;
            if (measurer.scrollWidth <= maxWidth && measurer.scrollHeight <= maxHeight) {
                element.textContent = fullText;
                document.body.removeChild(measurer);
                return { 
                    success: true, 
                    fittedText: fullText, 
                    remainingText: '' 
                };
            }

            // Find the optimal split point at a space boundary
            while (currentPosition < fullText.length) {
                const nextSpace = fullText.indexOf(' ', currentPosition);
                if (nextSpace === -1) break;
                
                const testText = fullText.substring(0, nextSpace);
                measurer.textContent = testText;
                
                if (measurer.scrollWidth <= maxWidth && measurer.scrollHeight <= maxHeight) {
                    lastValidSpace = nextSpace;
                    currentPosition = nextSpace + 1;
                } else {
                    break;
                }
            }

            // Prepare results
            if (lastValidSpace > 0) {
                fittedText = fullText.substring(0, lastValidSpace);
                remainingText = fullText.substring(lastValidSpace + 1);
                element.textContent = fittedText;
            } else {
                // No space found - return failure
                remainingText = fullText;
            }

            // Clean up
            document.body.removeChild(measurer);
            
            return { 
                success: lastValidSpace > 0,
                fittedText: fittedText,
                remainingText: remainingText
            };
        }", selector, text);

            return (result.Success, result.RemainingText);
        }
        catch
        {
            return (false, text);
        }
    }

    public static async Task<bool> SetElementTextAsync(this IPage page, string selector, string text)
    {
        try
        {
            return await page.EvaluateFunctionAsync<bool>(@"(selector, text) => {
            const originalElement = document.querySelector(selector);
            if (!originalElement) return false;

            // Cache DOM references
            const parent = originalElement.parentNode;
            const staticTextElement = originalElement.nextElementSibling;
            const originalClass = originalElement.className;
            const originalStyle = originalElement.getAttribute('style');
            
            // Get dimensions once
            const rect = originalElement.getBoundingClientRect();
            const maxWidth = rect.width;
            
            // Create canvas for faster measurement
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const style = window.getComputedStyle(originalElement);
            ctx.font = style.font;
            
            // Pre-process text into words and spaces
            const tokens = [];
            let buffer = '';
            let isWord = false;
            
            for (let i = 0; i < text.length; i++) {
                const char = text[i];
                const charIsSpace = char.trim() === '';
                
                if (charIsSpace !== isWord) {
                    if (buffer) tokens.push(buffer);
                    buffer = char;
                    isWord = !charIsSpace;
                } else {
                    buffer += char;
                }
            }
            if (buffer) tokens.push(buffer);

            // Process tokens
            let currentElement = originalElement;
            originalElement.textContent = '';
            let currentLine = [];
            let currentWidth = 0;
            let hasPassedStaticText = false;

            const createElement = () => {
                const el = document.createElement(originalElement.tagName);
                el.className = originalClass;
                if (originalStyle) el.setAttribute('style', originalStyle);
                
                if (!hasPassedStaticText && staticTextElement) {
                    parent.insertBefore(el, staticTextElement.nextSibling);
                    hasPassedStaticText = true;
                } else {
                    parent.insertBefore(el, currentElement.nextSibling);
                }
                return el;
            };

            for (const token of tokens) {
                const tokenWidth = ctx.measureText(token).width;
                
                if (currentWidth + tokenWidth <= maxWidth) {
                    currentLine.push(token);
                    currentWidth += tokenWidth;
                } else {
                    // Commit current line
                    currentElement.textContent = currentLine.join('');
                    
                    // Handle overflow
                    if (tokenWidth > maxWidth) {
                        // For tokens wider than container (preserve whole token)
                        currentElement = createElement();
                        currentElement.textContent = token;
                        currentElement = createElement();
                    } else {
                        // Normal overflow
                        currentElement = createElement();
                        currentLine = [token];
                        currentWidth = tokenWidth;
                    }
                }
            }

            // Flush remaining content
            if (currentLine.length > 0) {
                currentElement.textContent = currentLine.join('');
            }

            return true;
        }", selector, text);
        }
        catch
        {
            return false;
        }
    }

    public static async Task SetElementValueAsync(this IElementHandle element, string value, string? format = null)
    {
        format ??= await element.EvaluateFunctionAsync<string>("el => el.getAttribute('data-format')");

        if (format != null)
        {
            if (format.StartsWith('N'))
            {
                var formattedValue = double.Parse(value).ToString(format);
                await element.EvaluateFunctionAsync("(el, val) => { el.innerHTML = val; }", formattedValue);
            }
            else if (format == "0%")
            {
                var formattedValue = double.Parse(value).ToString(format);
                await element.EvaluateFunctionAsync("(el, val) => { el.innerHTML = val; }", formattedValue);
            }
            else
            {
                throw new Exception($"Unsupported format: {format}");
            }
        }
        else
        {
            await element.EvaluateFunctionAsync("(el, val) => { el.innerHTML = val; }", value);
        }
    }

    public static async Task<string?> RemoveElementAsync(this IPage page, string selector)
    {
        try
        {
            await page.EvaluateFunctionAsync(@"(selector) => {
            const element = document.querySelector(selector);
            if (element && element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }", selector);
            return null;
        }
        catch (Exception ex)
        {
            return ex.Message;
        }
    }

    public class TextFitResult
    {
        public required bool Success { get; set; }
        public required string FittedText { get; set; }
        public required string RemainingText { get; set; }
    }
}

/*
    public async Task<HTMLCreationResult> CreateAsync(T data, CancellationToken? cancellationToken = null)
    {
        var config = Configuration.Default.WithDefaultLoader();
        using var context = BrowsingContext.New(config);
        using var document = await context.OpenAsync(r => r.Content(_htmlForm), cancellationToken ?? CancellationToken.None);

        var deviceInfoResult = SetDeviceInfo(document, data);
        if (deviceInfoResult != null) return HTMLCreationResult.Failure(deviceInfoResult);

        foreach (var idValueElement in document.QuerySelectorAll("[id]").Where(e => e.Id!.StartsWith("setValue_")))
        {
            var id = idValueElement.Id!["setValue_".Length..].ToLower();
            var prop = TypeProps.FirstOrDefault(t => t.Name.Equals(id, StringComparison.OrdinalIgnoreCase));
            if (prop == null) return HTMLCreationResult.Failure($"Data property {id} not found");
            SetElementValue(idValueElement, prop.GetValue(data)!.ToString()!);
        }

        var result = SetVerification(document, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        result = SetEtalons(document, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        result = SetCheckups(document, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        if (cancellationToken.HasValue &&
        cancellationToken.Value.IsCancellationRequested)
        {
            return HTMLCreationResult.Failure("Отмена");
        }

        result = await SetSignAsync(document, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        var specifiResult = SetSpecific(document, data);
        if (specifiResult != null) return HTMLCreationResult.Failure(specifiResult);

        // return HTMLCreationResult.Success(document.DocumentElement.OuterHtml);
        return null!;
    }

    protected static void SetElementValue(IElement element, string value, string? format = null)
    {
        format ??= element.GetAttribute("data-format");
        if (format != null)
        {
            if (format.StartsWith('N'))
            {
                element.InnerHtml = double.Parse(value).ToString(format);
            }
            else if (format == "0%")
            {
                element.InnerHtml = double.Parse(value).ToString(format);
            }
            else
            {
                throw new Exception($"Неподдерживаемый формат: {format}");
            }
        }
        else
        {
            element.InnerHtml = value;
        }
    }

    protected string? SetLine(IHtmlParagraphElement element, int lineLength, ref string text)
    {
        if (text.Length <= lineLength)
        {
            // Text fits entirely
            element.InnerHtml = text;
            text = string.Empty;
            return null;
        }

        // Find the last space within maxLength+1 characters
        int splitPos = text.Substring(0, lineLength + 1).LastIndexOf(' ');

        if (splitPos > 0)
        {
            // Split at the found space
            element.InnerHtml = text.Substring(0, splitPos);
            text = text.Substring(splitPos + 1);
            return null;
        }

        return "Нет возможности разделить текст. Пробелы отсутствуют.";
    }

    private string? SetDeviceInfo(IDocument document, T data)
    {
        var deviceTypeNameElement = document.QuerySelector<IHtmlParagraphElement>("#manual_deviceInfo");
        if (deviceTypeNameElement == null) return "manual_deviceInfo not found";
        var insertAfterDeviceNameElement = deviceTypeNameElement.NextSibling;
        if (insertAfterDeviceNameElement == null) return "manual_deviceInfo sibling not found";
        var prop = TypeProps.FirstOrDefault(p => p.Name.Equals("deviceInfo", StringComparison.OrdinalIgnoreCase));
        if (prop == null) return "Data property deviceInfo not found";
        var deviceInfo = prop.GetValue(data)!.ToString()!;
        var deviceNameError = SetLine(deviceTypeNameElement, FullLineLength, ref deviceInfo);
        if (deviceNameError != null) return deviceNameError;

        while (deviceInfo.Length > 0)
        {
            var newDeviceNameLineElement = (IHtmlParagraphElement)deviceTypeNameElement.Clone(false);
            deviceNameError = SetLine(newDeviceNameLineElement, FullLineLength, ref deviceInfo);
            if (deviceNameError != null) return deviceNameError;
            insertAfterDeviceNameElement.InsertAfter(newDeviceNameLineElement);
            insertAfterDeviceNameElement = newDeviceNameLineElement;
        }

        return null;
    }

    private string? SetVerification(IDocument document, T data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name.Equals("verificationsinfo", StringComparison.OrdinalIgnoreCase));
        if (prop == null) return "Data property verificationsinfo not found";
        var verificationsText = prop.GetValue(data)!.ToString()!;
        var mainLine = document.QuerySelector<IHtmlParagraphElement>("#manual_verificationMethodMain")!;
        var result = SetLine(mainLine, VerificationLineLength, ref verificationsText);
        if (result != null) return result;
        if (verificationsText.Length == 0) return null;

        var vmAdditionalContainer = document.QuerySelector<IHtmlDivElement>("#manual_verificationMethodAdditional")!;

        while (verificationsText.Length > 0)
        {
            var element = document.CreateElement<IHtmlParagraphElement>();
            element.ClassName = "line";
            vmAdditionalContainer.AppendChild(element);
            SetLine(element, FullLineLength, ref verificationsText);
        }

        return null;
    }

    private string? SetEtalons(IDocument document, T data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name.Equals("EtalonsInfo", StringComparison.OrdinalIgnoreCase));
        if (prop == null) return "Data property EtalonsInfo not found";
        var etalonsText = prop.GetValue(data)!.ToString()!;

        var mainLine = document.QuerySelector<IHtmlParagraphElement>("#mainLine_etalons")!;
        var result = SetLine(mainLine, EtalonLineLength, ref etalonsText);
        if (result != null) return result;
        if (etalonsText.Length == 0) return null;

        var additionalLine = document.QuerySelector<IHtmlParagraphElement>("#additionalLine_etalons")!;
        result = SetLine(additionalLine, FullLineLength, ref etalonsText);
        if (result != null) return result;
        if (etalonsText.Length == 0) return null;

        var addAfterElement = document.QuerySelector("#addAfter_etalons")!;

        while (etalonsText.Length > 0)
        {
            var newLine = (IHtmlParagraphElement)additionalLine.Clone(false);
            result = SetLine(newLine, FullLineLength, ref etalonsText);
            if (result != null) return result;
            addAfterElement.InsertAfter(newLine);
            addAfterElement = newLine;
        }

        return null;
    }

    private string? SetCheckups(IDocument document, T data)
    {
        var verificationInfoProp = TypeProps.FirstOrDefault(p => p.Name.Equals("VerificationsInfo", StringComparison.OrdinalIgnoreCase));
        if (verificationInfoProp == null) return "Data property VerificationsInfo not found";
        var verificationInfo = verificationInfoProp.GetValue(data)!.ToString()!;

        var checkupsProp = TypeProps.FirstOrDefault(p => p.Name.Equals("Checkups", StringComparison.OrdinalIgnoreCase));
        if (checkupsProp == null) return "Data property Checkups not found";
        var checkups = (Dictionary<string, string>)checkupsProp.GetValue(data)!;

        var checkupElement = document.QuerySelector<IHtmlParagraphElement>("#manual_checkup");
        if (checkupElement == null) return "manual_checkup not found";

        var checkupNum = 1;

        foreach (var (key, value) in checkups)
        {
            var checkupNumElement = checkupElement.QuerySelector("#manual_checkupNum");
            if (checkupNumElement == null) return "manual_checkupNum not found";
            checkupNumElement.TextContent = $"{checkupNum++}. ";

            var checkupTitleElement = checkupElement.QuerySelector("#manual_checkupTitle");
            if (checkupTitleElement == null) return "manual_checkupTitle not found";
            checkupTitleElement.TextContent = key;

            var checkupValueElement = checkupElement.QuerySelector("#manual_checkupValue");
            if (checkupValueElement == null) return "manual_checkupValue not found";
            checkupValueElement.TextContent = value;

            var checkupVerificationElement = checkupElement.QuerySelector("#manual_checkupVerification");
            if (checkupVerificationElement != null)
            {
                checkupVerificationElement.TextContent = verificationInfo;
            }

            var newCheckupElement = (IHtmlParagraphElement)checkupElement.Clone(true);
            checkupElement.After(newCheckupElement);
            checkupElement = newCheckupElement;
        }

        checkupElement.Remove();

        return null;
    }

    private async Task<string?> SetSignAsync(IDocument document, T data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name == "Worker");
        if (prop == null) return "Data property Worker not found";
        var worker = (string)prop.GetValue(data)!;
        worker = worker.ToLower();

        if (!_signsCache.TryGetValue(worker, out var _))
        {
            var signFilesPaths = Directory.GetFiles(_signsDirPath, $"{worker}*.png");

            if (signFilesPaths.Length < 12) return $"Подпись сотрудника {worker} не найдена. Или вариантов меньше 12";

            foreach (var filePath in signFilesPaths)
            {
                var bytes = await File.ReadAllBytesAsync(filePath);
                var base64 = Convert.ToBase64String(bytes);
                var signBase64 = $"data:image/png;base64,{base64}";
                var cacheKey = Path.GetFileNameWithoutExtension(filePath);
                _signsCache[cacheKey] = signBase64;
            }
        }

        var signsCount = _signsCache.Where(s => s.Key.StartsWith(worker)).Count();
        var randomSignIndex = Random.Shared.Next(1, signsCount);
        var key = $"{worker} {randomSignIndex}";
        var _ = _signsCache.TryGetValue(key, out var sign);

        var imgElement = document.QuerySelector<IHtmlImageElement>("#sign")!;
        var randomTop = Random.Shared.Next(20, 30);
        var randomLeft = Random.Shared.Next(30, 150);
        var randomHeight = Random.Shared.Next(31, 33);
        imgElement.SetAttribute("style", $"top: {randomTop}px; left: {randomLeft}px;height: {randomHeight}px;");
        imgElement.Source = sign;

        return null;
    }

*/
```

### 65. `data/input/.~lock.Поверка манометры 06.2025 (copy 1).xlsm#`

```
,mflkee,archlinux-laptop,01.10.2025 11:18,file:///home/mflkee/.config/libreoffice/4;
```

### 66. `data/input/.~lock.Поверка манометры 06.2025.xlsm#`

```
,mflkee,archlinux-laptop,01.10.2025 11:11,file:///home/mflkee/.config/libreoffice/4;
```

### 67. `migrations/env.py`

```python
from __future__ import annotations
# isort: skip_file

import os
import sys
import asyncio
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.base import Base  # noqa: E402
from app.db import models as _models  # noqa: E402,F401  # register models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def get_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        # fallback for local runs
        return "sqlite:///dev.db"
    return url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()
    if url.startswith("postgresql+asyncpg"):

        async def async_run() -> None:
            connectable: AsyncEngine = create_async_engine(url, poolclass=pool.NullPool)
            async with connectable.connect() as connection:
                await connection.run_sync(_run_migrations)
            await connectable.dispose()

        asyncio.run(async_run())
        return

    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        _run_migrations(connection)


def _run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

```

### 68. `migrations/versions/20250906_000001_init.py`

```python
"""init schema

Revision ID: 20250906_000001_init
Revises:
Create Date: 2025-09-06 00:00:01

"""

from __future__ import annotations
# isort: skip_file

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20250906_000001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("supported_fields", sa.JSON(), nullable=True),
    )

    op.create_table(
        "owners",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("inn", sa.String(length=32), nullable=True),
    )
    op.create_index("ix_owners_inn", "owners", ["inn"], unique=False)

    op.create_table(
        "etalons",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("reg_number", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("certificate", sa.String(length=128), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
    )
    op.create_index("ix_etalons_reg_number", "etalons", ["reg_number"], unique=False)

    op.create_table(
        "protocols",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("number", sa.String(length=64), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("methodology", sa.String(length=255), nullable=True),
        sa.Column("vri_id", sa.String(length=64), nullable=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("owners.id")),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("templates.id")),
        sa.Column("etalon_id", sa.Integer(), sa.ForeignKey("etalons.id")),
        sa.Column("context", sa.JSON(), nullable=True),
    )
    op.create_index("ix_protocols_number", "protocols", ["number"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_protocols_number", table_name="protocols")
    op.drop_table("protocols")
    op.drop_index("ix_etalons_reg_number", table_name="etalons")
    op.drop_table("etalons")
    op.drop_index("ix_owners_inn", table_name="owners")
    op.drop_table("owners")
    op.drop_table("templates")

```

### 69. `migrations/versions/20251001_000002_data_model.py`

```python
"""Expand data model with registry, instruments, etalons, methodologies

Revision ID: 20251001_000002_data_model
Revises: 20250906_000001_init
Create Date: 2025-10-01 06:20:00.000000
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "20251001_000002_data_model"
down_revision = "20250906_000001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    methodology_point_type = postgresql.ENUM(
        "bool",
        "clause",
        "custom",
        name="methodology_point_type",
        create_type=False,
    )
    methodology_point_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "verification_registry_entries",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("source_file", String(512), nullable=False),
        Column("source_sheet", String(255), nullable=True),
        Column("loaded_at", DateTime, nullable=False, server_default=text("now()")),
        Column("row_index", Integer, nullable=False),
        Column("normalized_serial", String(128), nullable=True),
        Column("document_no", String(128), nullable=True),
        Column("protocol_no", String(128), nullable=True),
        Column("owner_name_raw", String(255), nullable=True),
        Column("methodology_raw", String(255), nullable=True),
        Column("verification_date", Date, nullable=True),
        Column("valid_to", Date, nullable=True),
        Column("payload", JSONB, nullable=True),
        Column("is_active", Boolean, nullable=False, server_default=text("true")),
        UniqueConstraint("source_file", "row_index", name="uq_registry_source_row"),
    )
    op.create_index(
        "ix_registry_serial",
        "verification_registry_entries",
        ["normalized_serial"],
    )
    op.create_index(
        "ix_registry_document",
        "verification_registry_entries",
        ["document_no"],
    )
    op.create_index(
        "ix_registry_protocol",
        "verification_registry_entries",
        ["protocol_no"],
    )

    op.create_table(
        "methodologies",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("code", String(128), nullable=False, unique=True),
        Column("title", String(255), nullable=False),
        Column("document", String(255), nullable=True),
        Column("notes", String(1024), nullable=True),
    )

    op.create_table(
        "methodology_aliases",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column(
            "methodology_id",
            Integer,
            ForeignKey("methodologies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("alias", String(255), nullable=False),
        Column("normalized_alias", String(255), nullable=False),
        Column("weight", Integer, nullable=False, server_default=text("100")),
        UniqueConstraint("normalized_alias", name="uq_methodology_alias_normalized"),
    )
    op.create_index(
        "ix_methodology_alias_methodology",
        "methodology_aliases",
        ["methodology_id"],
    )

    op.create_table(
        "methodology_points",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column(
            "methodology_id",
            Integer,
            ForeignKey("methodologies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("position", Integer, nullable=False),
        Column("label", String(512), nullable=False),
        Column("point_type", methodology_point_type, nullable=False, server_default="bool"),
        Column("default_text", String(1024), nullable=True),
        UniqueConstraint("methodology_id", "position", name="uq_methodology_points_order"),
    )
    op.create_index(
        "ix_methodology_points_methodology",
        "methodology_points",
        ["methodology_id"],
    )

    op.create_table(
        "owner_aliases",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("owner_id", Integer, ForeignKey("owners.id", ondelete="CASCADE"), nullable=False),
        Column("alias", String(255), nullable=False),
        Column("normalized_alias", String(255), nullable=False),
        UniqueConstraint("normalized_alias", name="uq_owner_alias_normalized"),
    )
    op.create_index(
        "ix_owner_alias_owner",
        "owner_aliases",
        ["owner_id"],
    )

    op.create_table(
        "etalon_devices",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("reg_number", String(128), nullable=False),
        Column("mitype_number", String(128), nullable=True),
        Column("title", String(255), nullable=True),
        Column("notation", String(255), nullable=True),
        Column("modification", String(255), nullable=True),
        Column("manufacture_num", String(128), nullable=True),
        Column("manufacture_year", Integer, nullable=True),
        Column("rank_code", String(64), nullable=True),
        Column("rank_title", String(255), nullable=True),
        Column("schema_title", String(255), nullable=True),
        Column("payload", JSONB, nullable=True),
        UniqueConstraint(
            "reg_number",
            "manufacture_num",
            name="uq_etalon_device_reg_manufacture",
        ),
    )
    op.create_index(
        "ix_etalon_devices_reg_number",
        "etalon_devices",
        ["reg_number"],
    )

    op.create_table(
        "etalon_certifications",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column(
            "etalon_device_id",
            Integer,
            ForeignKey("etalon_devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("certificate_no", String(128), nullable=False),
        Column("verification_date", Date, nullable=True),
        Column("valid_to", Date, nullable=True),
        Column("source", String(64), nullable=False, server_default=text("'arshin'")),
        Column("payload", JSONB, nullable=True),
        UniqueConstraint(
            "etalon_device_id",
            "certificate_no",
            name="uq_etalon_certificates_unique",
        ),
    )
    op.create_index(
        "ix_etalon_cert_certificate",
        "etalon_certifications",
        ["certificate_no"],
    )
    op.create_index(
        "ix_etalon_cert_valid_to",
        "etalon_certifications",
        ["valid_to"],
    )

    op.create_table(
        "measuring_instruments",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("normalized_serial", String(128), nullable=False),
        Column("designation", String(255), nullable=True),
        Column("modification", String(255), nullable=True),
        Column("manufacture_year", Integer, nullable=True),
        Column("owner_id", Integer, ForeignKey("owners.id", ondelete="SET NULL"), nullable=True),
        Column(
            "methodology_id",
            Integer,
            ForeignKey("methodologies.id", ondelete="SET NULL"),
            nullable=True,
        ),
        Column(
            "registry_entry_id",
            Integer,
            ForeignKey("verification_registry_entries.id", ondelete="SET NULL"),
            nullable=True,
        ),
        Column("certificate_no", String(128), nullable=True),
        Column("certificate_valid_to", Date, nullable=True),
        Column("vri_id", String(64), nullable=True),
        Column("payload", JSONB, nullable=True),
        Column("created_at", DateTime, nullable=False, server_default=text("now()")),
        Column(
            "updated_at",
            DateTime,
            nullable=False,
            server_default=text("now()"),
            server_onupdate=text("now()"),
        ),
        UniqueConstraint("normalized_serial", "certificate_no", name="uq_instruments_serial_cert"),
    )
    op.create_index(
        "ix_instruments_serial",
        "measuring_instruments",
        ["normalized_serial"],
    )
    op.create_index(
        "ix_instruments_owner",
        "measuring_instruments",
        ["owner_id"],
    )
    op.create_index(
        "ix_instruments_methodology",
        "measuring_instruments",
        ["methodology_id"],
    )

    op.add_column(
        "protocols",
        Column(
            "registry_entry_id",
            Integer,
            ForeignKey("verification_registry_entries.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "protocols",
        Column(
            "measuring_instrument_id",
            Integer,
            ForeignKey("measuring_instruments.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "protocols",
        Column(
            "etalon_certification_id",
            Integer,
            ForeignKey("etalon_certifications.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_protocols_registry_entry",
        "protocols",
        ["registry_entry_id"],
    )
    op.create_index(
        "ix_protocols_measuring_instrument",
        "protocols",
        ["measuring_instrument_id"],
    )
    op.create_index(
        "ix_protocols_etalon_certification",
        "protocols",
        ["etalon_certification_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_protocols_etalon_certification", table_name="protocols")
    op.drop_index("ix_protocols_measuring_instrument", table_name="protocols")
    op.drop_index("ix_protocols_registry_entry", table_name="protocols")
    op.drop_column("protocols", "etalon_certification_id")
    op.drop_column("protocols", "measuring_instrument_id")
    op.drop_column("protocols", "registry_entry_id")

    op.drop_index("ix_instruments_methodology", table_name="measuring_instruments")
    op.drop_index("ix_instruments_owner", table_name="measuring_instruments")
    op.drop_index("ix_instruments_serial", table_name="measuring_instruments")
    op.drop_table("measuring_instruments")

    op.drop_index("ix_etalon_cert_valid_to", table_name="etalon_certifications")
    op.drop_index("ix_etalon_cert_certificate", table_name="etalon_certifications")
    op.drop_table("etalon_certifications")

    op.drop_index("ix_etalon_devices_reg_number", table_name="etalon_devices")
    op.drop_table("etalon_devices")

    op.drop_index("ix_owner_alias_owner", table_name="owner_aliases")
    op.drop_table("owner_aliases")

    op.drop_index("ix_methodology_points_methodology", table_name="methodology_points")
    op.drop_table("methodology_points")

    op.drop_index("ix_methodology_alias_methodology", table_name="methodology_aliases")
    op.drop_table("methodology_aliases")

    op.drop_table("methodologies")

    op.drop_index("ix_registry_protocol", table_name="verification_registry_entries")
    op.drop_index("ix_registry_document", table_name="verification_registry_entries")
    op.drop_index("ix_registry_serial", table_name="verification_registry_entries")
    op.drop_table("verification_registry_entries")

    op.execute("DROP TYPE IF EXISTS methodology_point_type")

```

### 70. `migrations/versions/20251001_000003_methodology.py`

```python
"""Add allowable variation column to methodologies

Revision ID: 20251001_000003_methodology
Revises: 20251001_000002_data_model
Create Date: 2025-10-01 07:45:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20251001_000003_methodology"
down_revision = "20251001_000002_data_model"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "methodologies",
        sa.Column("allowable_variation_pct", sa.Float(), nullable=True),
    )
    op.alter_column(
        "methodology_points",
        "point_type",
        type_=sa.String(length=32),
        existing_type=postgresql.ENUM("bool", "clause", "custom", name="methodology_point_type"),
        postgresql_using="point_type::text",
        server_default=sa.text("'bool'"),
    )
    op.execute("DROP TYPE IF EXISTS methodology_point_type")


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS methodology_point_type")
    enum_type = postgresql.ENUM("bool", "clause", "custom", name="methodology_point_type")
    enum_type.create(op.get_bind(), checkfirst=False)
    op.alter_column(
        "methodology_points",
        "point_type",
        type_=enum_type,
        existing_type=sa.String(length=32),
        postgresql_using="point_type::methodology_point_type",
        server_default=sa.text("'bool'"),
    )
    op.drop_column("methodologies", "allowable_variation_pct")

```

### 71. `migrations/versions/20251010_000004_add_instrument_kind.py`

```python
"""Add instrument_kind to verification registry entries

Revision ID: 20251010_000004_add_instrument_kind
Revises: 20251001_000003_methodology
Create Date: 2025-10-10 08:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251010_000004_add_instrument_kind"
down_revision = "20251001_000003_methodology"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(64)")
    op.add_column(
        "verification_registry_entries",
        sa.Column("instrument_kind", sa.String(length=64), nullable=True),
    )
    op.create_index(
        op.f("ix_verification_registry_entries_instrument_kind"),
        "verification_registry_entries",
        ["instrument_kind"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_verification_registry_entries_instrument_kind"),
        table_name="verification_registry_entries",
    )
    op.drop_column("verification_registry_entries", "instrument_kind")

```

### 72. `pyproject.toml`

```toml
[project]
name = "metrologenerator"
version = "0.1.0"
description = "Protocol generator for mkair"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
  "fastapi",
  "uvicorn[standard]",
  "httpx",
  "openpyxl",
  "python-dateutil",
  "pydantic-settings",
  "loguru",
  "python-multipart",
  "Jinja2",
  "playwright",
  "python-slugify",
  "ruff>=0.12.12",
  "SQLAlchemy>=2.0",
  "alembic>=1.13",
  "asyncpg",
]

# dev-зависимости как optional extras (стандарт PEP 621)
[project.optional-dependencies]
dev = [
  "pytest",
  "pytest-asyncio",
  "respx",
  "pytest-cov",
  "ruff",
  "black"
]

[tool.ruff]
# Общие настройки Ruff (линтер + форматтер)
target-version = "py313"
line-length = 100

[tool.ruff.lint]
# Набор правил: базовая чистота + импорт-упорядочивание + обновления синтаксиса
select = [
  "E",   # pycodestyle
  "F",   # pyflakes
  "I",   # isort (упорядочивание импортов)
  "UP",  # pyupgrade
]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false

```

### 73. `pytest.ini`

```ini
# pytest.ini
[pytest]
asyncio_mode = auto

```

### 74. `scripts/run_quality_checks.py`

```python
from __future__ import annotations

import argparse
import asyncio
import os
import shlex
import subprocess
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DEFAULT_SQLITE = "sqlite+aiosqlite:///./dev.db"
ENV_FILE = Path(".env")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _can_connect(url: str) -> bool:
    async def _check() -> bool:
        engine = create_async_engine(url)
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
        finally:
            await engine.dispose()

    try:
        return asyncio.run(_check())
    except Exception:
        return False


def ensure_database_url() -> None:
    url = os.environ.get("DATABASE_URL")
    if url and url.startswith("postgresql"):
        if _can_connect(url):
            return
        print("[warn] PostgreSQL URL set but unreachable; falling back to sqlite dev.db")
    elif url:
        return
    else:
        print("[warn] DATABASE_URL not set; using sqlite dev.db")

    os.environ["DATABASE_URL"] = DEFAULT_SQLITE


def run_command(
    command: Sequence[str],
    *,
    description: str,
    allow_failure: bool = False,
) -> tuple[bool, str]:
    print(f"\n==> {description}")
    print("   $", " ".join(shlex.quote(c) for c in command))
    result = subprocess.run(command, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    success = result.returncode == 0
    if not success and not allow_failure:
        print(f"[!] step failed (exit code {result.returncode})")
    return success, description


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Ruff checks, apply fixes (unless --no-fix), and execute pytest",
    )
    parser.add_argument(
        "--no-fix",
        action="store_true",
        help="Do not run Ruff auto-fix commands",
    )
    parser.add_argument(
        "--pytest-args",
        nargs=argparse.REMAINDER,
        help="Additional pytest arguments (everything after this flag)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    load_env_file(ENV_FILE)
    ensure_database_url()

    summary: list[tuple[str, bool]] = []
    failure = False

    success, desc = run_command(
        ["ruff", "format", "--check", "."],
        description="Ruff format check",
        allow_failure=True,
    )
    summary.append((desc, success))
    if not success and not args.no_fix:
        run_command(
            ["ruff", "format", "."],
            description="Ruff format auto-fix",
            allow_failure=True,
        )
        success, desc = run_command(
            ["ruff", "format", "--check", "."],
            description="Ruff format re-check",
            allow_failure=False,
        )
        summary.append((desc, success))
    failure = failure or not success

    success, desc = run_command(
        ["ruff", "check", "."],
        description="Ruff lint check",
        allow_failure=True,
    )
    summary.append((desc, success))
    if not success and not args.no_fix:
        run_command(
            ["ruff", "check", "--fix", "."],
            description="Ruff lint auto-fix",
            allow_failure=True,
        )
        success, desc = run_command(
            ["ruff", "check", "."],
            description="Ruff lint re-check",
            allow_failure=False,
        )
        summary.append((desc, success))
    failure = failure or not success

    pytest_cmd = ["pytest", "-q"]
    if args.pytest_args:
        pytest_cmd.extend(args.pytest_args)
    success, desc = run_command(pytest_cmd, description="Pytest suite")
    summary.append((desc, success))
    failure = failure or not success

    print("\nSummary:")
    for step, ok in summary:
        status = "OK" if ok else "FAIL"
        print(f" - {step}: {status}")

    return 1 if failure else 0


if __name__ == "__main__":
    raise SystemExit(main())

```

### 75. `tests/conftest.py`

```python
import io
import os
import sys

import httpx
import pytest
from fastapi import FastAPI
from openpyxl import Workbook

# 1) добавляем корень репозитория в sys.path ДО импортов app.*
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# 2) теперь можно импортировать код приложения
from app.main import app as fastapi_app  # noqa: E402
from app.utils.excel import CERTIFICATE_HEADER_KEYS  # noqa: E402


@pytest.fixture(scope="session")
def app() -> FastAPI:
    return fastapi_app


@pytest.fixture
async def async_client(app: FastAPI):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def make_excel():
    """Фабрика: создаёт XLSX в памяти с данными в указанной колонке/строке."""

    def _make(
        values,
        column_letter="P",
        header: str = CERTIFICATE_HEADER_KEYS[-1],
        start_row=2,
    ):
        wb = Workbook()
        ws = wb.active
        ws[f"{column_letter}1"] = header
        r = start_row
        for v in values:
            ws[f"{column_letter}{r}"] = v
            r += 1
        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    return _make

```

### 76. `tests/test_arshin_routes.py`

```python
import httpx
import pytest
import respx

from app.services.arshin_client import ARSHIN_BASE


@pytest.mark.anyio
@respx.mock
async def test_get_vri_id_endpoint(async_client):
    cert = "С-ВЯ/15-01-2025/402123271"
    vri_id = "1-402123271"
    respx.get(f"{ARSHIN_BASE}/vri").mock(
        return_value=httpx.Response(200, json={"result": {"items": [{"vri_id": vri_id}]}})
    )
    r = await async_client.get("/api/v1/resolve/vri-id", params={"cert": cert})
    assert r.status_code == 200
    body = r.json()
    assert body["vri_id"] == vri_id


@pytest.mark.anyio
@respx.mock
async def test_post_vri_ids_by_excel(async_client, make_excel):
    certs = [
        "С-ЕЖБ/05-06-2025/440144576",
        "С-ЕЖБ/05-06-2025/440144575",
    ]
    xlsx = make_excel(certs)  # колонка P, со 2 строки

    # моки: /vri → vri_id и /vri/{id} → детали (пустые достаточно)
    for i, cert in enumerate(certs, start=1):
        vid = f"1-40212327{i}"
        respx.get(f"{ARSHIN_BASE}/vri").mock(
            return_value=httpx.Response(200, json={"result": {"items": [{"vri_id": vid}]}})
        )
        respx.get(f"{ARSHIN_BASE}/vri/{vid}").mock(
            return_value=httpx.Response(200, json={"result": {}})
        )

    files = {
        "file": (
            "input.xlsx",
            xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    r = await async_client.post("/api/v1/resolve/vri-details-by-excel", files=files)
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == len(certs)
    assert {item["certificate"] for item in body["items"]} == set(certs)


@pytest.mark.anyio
@respx.mock
async def test_get_details_by_vri_id(async_client):
    vri_id = "1-402123271"
    respx.get(f"{ARSHIN_BASE}/vri/{vri_id}").mock(
        return_value=httpx.Response(
            200,
            json={
                "result": {
                    "miInfo": {
                        "etaMI": {
                            "regNumber": "77090.19.1Р.00761951",
                            "mitypeNumber": "77090-19",
                            "mitypeTitle": "Преобразователи давления эталонные",
                            "mitypeType": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                        }
                    },
                    "vriInfo": {"organization": "ФБУ", "applicable": {"certNum": "X"}},
                    "info": {"protocol_url": f"{ARSHIN_BASE}/vri/{vri_id}/protocol"},
                }
            },
        )
    )
    r = await async_client.get(f"/api/v1/resolve/vri/{vri_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["vri_id"] == vri_id
    assert body["etalon_line"].startswith("77090.19.1Р.00761951; 77090-19")


@pytest.mark.anyio
@respx.mock
async def test_post_vri_details_by_excel(async_client, make_excel):
    certs = [
        "С-ЕЖБ/05-06-2025/440144576",
        "С-ЕЖБ/05-06-2025/440144575",
    ]
    xlsx = make_excel(certs)

    # 1) мок /vri: два последовательных ответа для двух вызовов
    respx.get(f"{ARSHIN_BASE}/vri").mock(
        side_effect=[
            httpx.Response(200, json={"result": {"items": [{"vri_id": "1-AAA"}]}}),
            httpx.Response(200, json={"result": {"items": [{"vri_id": "1-BBB"}]}}),
        ]
    )
    # 2) мок /vri/{id} → детали
    respx.get(f"{ARSHIN_BASE}/vri/1-AAA").mock(
        return_value=httpx.Response(
            200,
            json={
                "result": {
                    "miInfo": {
                        "etaMI": {
                            "regNumber": "77090.19.1Р.00761951",
                            "mitypeNumber": "77090-19",
                            "mitypeTitle": "Преобразователи давления эталонные",
                            "mitypeType": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                        }
                    },
                    "vriInfo": {
                        "vrfDate": "15.01.2025",
                        "validDate": "14.01.2026",
                        "applicable": {"certNum": "X"},
                    },
                    "info": {"protocol_url": f"{ARSHIN_BASE}/vri/1-AAA/protocol"},
                }
            },
        )
    )
    respx.get(f"{ARSHIN_BASE}/vri/1-BBB").mock(
        return_value=httpx.Response(
            200,
            json={
                "result": {
                    "miInfo": {
                        "etaMI": {
                            "regNumber": "52506.16.РЭ.00353712",
                            "mitypeNumber": "52506-16",
                            "mitypeTitle": "Манометры газовые грузопоршневые",
                            "mitypeType": "МГП-10",
                        }
                    },
                    "vriInfo": {
                        "vrfDate": "01.02.2025",
                        "validDate": "31.01.2026",
                        "applicable": {"certNum": "Y"},
                    },
                    "info": {"protocol_url": f"{ARSHIN_BASE}/vri/1-BBB/protocol"},
                }
            },
        )
    )

    files = {
        "file": (
            "input.xlsx",
            xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    r = await async_client.post("/api/v1/resolve/vri-details-by-excel", files=files)
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 2
    ids = {it["vri_id"] for it in body["items"]}
    assert ids == {"1-AAA", "1-BBB"}
    # проверим готовую строку для одного из них
    # в текущей реализации Excel-ручка не возвращает etalon_line —
    # он доступен в /resolve/vri/{vri_id}. Достаточно проверить состав ids.

```

### 77. `tests/test_arshin_service.py`

```python
import httpx
import respx

from app.services.arshin_client import (
    ARSHIN_BASE,
    compose_etalon_line_from_details,
    extract_detail_fields,
    fetch_vri_details,
    fetch_vri_id_by_certificate,
)

CERT = "С-ВЯ/15-01-2025/402123271"
VRI_ID = "1-402123271"

LIST_PAYLOAD = {
    "result": {
        "count": 1,
        "start": 0,
        "rows": 10,
        "items": [
            {
                "vri_id": VRI_ID,
                "org_title": 'ФБУ "ТЮМЕНСКИЙ ЦСМ"',
                "mit_number": "77090-19",
                "mit_title": "Преобразователи давления эталонные",
                "mit_notation": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                "mi_modification": "1М-0,01-Т35",
                "mi_number": "3127",
                "verification_date": "15.01.2025",
                "valid_date": "14.01.2026",
                "result_docnum": CERT,
                "applicability": True,
            }
        ],
    }
}

DETAILS_PAYLOAD = {
    "result": {
        "miInfo": {
            "etaMI": {
                "regNumber": "77090.19.1Р.00761951",
                "mitypeNumber": "77090-19",
                "mitypeTitle": "Преобразователи давления эталонные",
                "mitypeType": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                "manufactureNum": "3127",
                "manufactureYear": 2020,
                "rankCode": "1Р",
                "rankTitle": "Эталон 1-го разряда",
            }
        },
        "vriInfo": {
            "organization": 'ФБУ "ТЮМЕНСКИЙ ЦСМ"',
            "vrfDate": "15.01.2025",
            "validDate": "14.01.2026",
            "applicable": {"certNum": CERT},
        },
        "info": {"protocol_url": f"{ARSHIN_BASE}/vri/{VRI_ID}/protocol"},
    }
}


@respx.mock
async def test_fetch_vri_and_details():
    async with httpx.AsyncClient() as client:
        # мок: список по сертификату
        respx.get(f"{ARSHIN_BASE}/vri").mock(return_value=httpx.Response(200, json=LIST_PAYLOAD))
        # мок: детали по vri_id
        respx.get(f"{ARSHIN_BASE}/vri/{VRI_ID}").mock(
            return_value=httpx.Response(200, json=DETAILS_PAYLOAD)
        )

        data = await fetch_vri_id_by_certificate(client, CERT, year=2025)
        assert data == VRI_ID

        details = await fetch_vri_details(client, VRI_ID)
        line = compose_etalon_line_from_details(details)
        fields = extract_detail_fields(details)

        assert line == (
            "77090.19.1Р.00761951; 77090-19; Преобразователи давления эталонные; ЭЛМЕТРО-Паскаль-04"
        )
        assert fields["organization"].startswith("ФБУ")
        assert fields["vrfDate"] == "15.01.2025"
        assert fields["applicable"] is True

```

### 78. `tests/test_excel_utils.py`

```python
import io

import pytest
from openpyxl import Workbook

from app.utils.excel import (
    CERTIFICATE_HEADER_KEYS,
    extract_certificate_number,
    read_column_as_list,
)


def test_read_column_as_list_default():
    wb = Workbook()
    ws = wb.active
    ws["P1"] = CERTIFICATE_HEADER_KEYS[-1]
    ws["P2"] = "С-ЕЖБ/05-06-2025/440144576"
    ws["P3"] = "С-ЕЖБ/05-06-2025/440144575"
    ws["P4"] = "С-ЕЖБ/05-06-2025/440144575"  # дубликат
    buf = io.BytesIO()
    wb.save(buf)

    items = read_column_as_list(buf.getvalue(), column_letter="P", start_row=2)
    assert items == [
        "С-ЕЖБ/05-06-2025/440144576",
        "С-ЕЖБ/05-06-2025/440144575",
    ]


@pytest.mark.parametrize("header", CERTIFICATE_HEADER_KEYS)
def test_extract_certificate_number(header):
    row = {header: " С-ВЯ/15-01-2025/402123271 "}
    assert extract_certificate_number(row) == "С-ВЯ/15-01-2025/402123271"


def test_extract_certificate_number_missing():
    assert extract_certificate_number({}) == ""

```

### 79. `tests/test_methodologies_routes.py`

```python
import pytest
from sqlalchemy import delete, select

from app.db import models
from app.db.session import get_sessionmaker


@pytest.mark.anyio
async def test_create_methodology_endpoint(async_client):
    payload = {
        "code": "МИ 9999-99",
        "title": "Методика поверки датчиков давления",
        "aliases": ["9999-99 МИ"],
        "points": [
            {"position": 1, "label": "Соответствует/не соответствует"},
            {"position": 2, "label": "Температура ____ °C"},
        ],
    }

    response = await async_client.post("/api/v1/methodologies", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == payload["code"]
    assert body["title"] == payload["title"]
    assert len(body["points"]) == 2
    assert body["points"][0]["point_type"] == "bool"
    assert body["points"][1]["point_type"] == "custom"

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        methodology = (
            await session.execute(
                select(models.Methodology).where(models.Methodology.code == payload["code"])
            )
        ).scalar_one()
        assert methodology.title == payload["title"]
        stored_points = (
            (
                await session.execute(
                    select(models.MethodologyPoint)
                    .where(models.MethodologyPoint.methodology_id == methodology.id)
                    .order_by(models.MethodologyPoint.position)
                )
            )
            .scalars()
            .all()
        )
        assert len(stored_points) == 2
        assert stored_points[0].point_type == "bool"
        assert stored_points[1].point_type == "custom"

        await session.execute(
            delete(models.MethodologyPoint).where(
                models.MethodologyPoint.methodology_id == methodology.id
            )
        )
        await session.execute(
            delete(models.Methodology).where(models.Methodology.id == methodology.id)
        )
        await session.commit()


@pytest.mark.anyio
async def test_create_methodology_variant_with_extra_point(async_client):
    long_title = (
        "МИ 2124-90 «ГСИ. Манометры, вакуумметры, мановакуумметры, "
        "напоромеры, тягомеры и тягонапоромеры показывающие и "
        "самопишущие. Методика поверки»"
    )
    payload = {
        "code": "МИ 2124-91",
        "title": long_title,
        "aliases": ["2124-91 МИ"],
        "allowable_variation_pct": 1.5,
        "points": [
            {"position": 1, "label": "5.1"},
            {"position": 2, "label": "5.2.3"},
            {"position": 3, "label": "5.3"},
            {"position": 4, "label": "Проведение очистки _____"},
        ],
    }

    response = await async_client.post("/api/v1/methodologies", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == payload["code"]
    assert body["points"][3]["point_type"] == "custom"

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        methodology = (
            await session.execute(
                select(models.Methodology).where(models.Methodology.code == payload["code"])
            )
        ).scalar_one()
        aliases = (
            (
                await session.execute(
                    select(models.MethodologyAlias.alias).where(
                        models.MethodologyAlias.methodology_id == methodology.id
                    )
                )
            )
            .scalars()
            .all()
        )
        assert "2124-91 МИ" in aliases

        await session.execute(
            delete(models.MethodologyPoint).where(
                models.MethodologyPoint.methodology_id == methodology.id
            )
        )
        await session.execute(
            delete(models.MethodologyAlias).where(
                models.MethodologyAlias.methodology_id == methodology.id
            )
        )
        await session.execute(
            delete(models.Methodology).where(models.Methodology.id == methodology.id)
        )
        await session.commit()


@pytest.mark.anyio
async def test_create_methodology_with_explicit_point_types(async_client):
    payload = {
        "code": "МИ 8888-88",
        "title": "Методика с явным типом",
        "points": [
            {"position": 1, "label": "Проверка параметров", "point_type": "clause"},
            {"position": 2, "label": "Соответствует", "point_type": "bool"},
        ],
    }

    response = await async_client.post("/api/v1/methodologies", json=payload)
    assert response.status_code == 201

```

### 80. `tests/test_protocols_html.py`

```python
import io

import httpx
import pytest
import respx
from openpyxl import Workbook

from app.services.arshin_client import ARSHIN_BASE
from app.utils.excel import CERTIFICATE_HEADER_KEYS


def _make_excel_row(
    certificate: str,
    sn: str = "ABC123",
    date: str = "15.01.2025",
    header: str = CERTIFICATE_HEADER_KEYS[-1],
) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws["A1"] = header
    ws["B1"] = "Заводской номер"
    ws["C1"] = "Дата поверки"

    ws["A2"] = certificate
    ws["B2"] = sn
    ws["C2"] = date

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.mark.anyio
@respx.mock
@pytest.mark.parametrize("header", CERTIFICATE_HEADER_KEYS)
async def test_html_by_excel_returns_html(async_client, header):
    cert = "С-ВЯ/15-01-2025/402123271"
    vri_id = "1-XYZ"

    # 1) /vri (по номеру свидетельства)
    respx.get(f"{ARSHIN_BASE}/vri").mock(
        side_effect=[
            httpx.Response(200, json={"result": {"items": [{"vri_id": vri_id}]}}),
            httpx.Response(
                200,
                json={
                    "result": {
                        "items": [
                            {
                                "result_docnum": "ET-123",
                                "verification_date": "01.01.2025",
                                "valid_date": "31.12.2025",
                            }
                        ]
                    }
                },
            ),
        ]
    )

    # 2) /vri/{id}
    respx.get(f"{ARSHIN_BASE}/vri/{vri_id}").mock(
        return_value=httpx.Response(
            200,
            json={
                "result": {
                    "means": {
                        "mieta": [
                            {
                                "regNumber": "77090.19.1Р.00761951",
                                "mitypeNumber": "77090-19",
                                "mitypeTitle": "Преобразователи давления эталонные",
                                "notation": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                                "manufactureNum": "3127",
                                "manufactureYear": 2020,
                                "rankCode": "1Р",
                                "rankTitle": "Эталон 1-го разряда",
                            }
                        ]
                    },
                    "vriInfo": {
                        "docTitle": "МИ 123-45",
                        "vrfDate": "15.01.2025",
                        "validDate": "14.01.2026",
                        "applicable": {"certNum": cert},
                    },
                }
            },
        )
    )

    xlsx = _make_excel_row(cert, header=header)
    files = {
        "file": (
            "input.xlsx",
            xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    r = await async_client.post("/api/v1/protocols/html-by-excel", files=files)

    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    html = r.text
    assert "ПРОТОКОЛ ПЕРИОДИЧЕСКОЙ ПОВЕРКИ" in html
    assert "ABC123" in html  # serial number appears
    assert "МИ 123-45" in html  # methodology
    assert "77090-19" in html  # etalon line

```

### 81. `tests/test_protocols_routes.py`

```python
import io
from pathlib import Path

import httpx
import pytest
import respx
from openpyxl import Workbook

from app.services.arshin_client import ARSHIN_BASE
from app.utils.excel import CERTIFICATE_HEADER_KEYS


def _make_protocols_excel_row(
    certificate: str,
    sn: str = "ABC123",
    date: str = "15.01.2025",
    header: str = CERTIFICATE_HEADER_KEYS[-1],
) -> bytes:
    """Готовит XLSX с минимально нужной шапкой для /protocols/context-by-excel."""
    wb = Workbook()
    ws = wb.active
    ws["A1"] = header
    ws["B1"] = "Заводской номер"
    ws["C1"] = "Дата поверки"

    ws["A2"] = certificate
    ws["B2"] = sn
    ws["C2"] = date

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _make_manometers_excel_row(
    *,
    certificate: str,
    serial: str,
    verifier: str = "Большаков С.Н.",
    date: str = "15.06.2025",
    pressure: str = "101,5 кПа",
    owner: str = 'ООО "РИ-ИНВЕСТ"',
) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws["A1"] = "Обозначение СИ"
    ws["B1"] = "Заводской номер"
    ws["E1"] = "Владелец СИ"
    ws["F1"] = "Дата поверки"
    ws["H1"] = "Методика поверки"
    ws["J1"] = "Прочие сведения"
    ws["K1"] = "Поверитель"
    ws["M1"] = "Давление"
    ws["P1"] = "Свидетельство о поверке"

    ws["A2"] = "13535-93"
    ws["B2"] = serial
    ws["E2"] = owner
    ws["F2"] = date
    ws["H2"] = "МИ 2124-90"
    ws["J2"] = "(0 - 4) кгс/см²"
    ws["K2"] = verifier
    ws["M2"] = pressure
    ws["P2"] = certificate

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _make_manometers_db_excel(
    *,
    serial: str,
    certificate: str,
    protocol_number: str,
) -> bytes:
    wb = Workbook()
    ws = wb.active

    ws["H5"] = "Заводской №/ Буквенно-цифровое обозначение"
    ws["L5"] = "Документ"
    ws["P5"] = "номер_протокола"

    ws["H6"] = serial
    ws["L6"] = certificate
    ws["P6"] = protocol_number

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.mark.anyio
@respx.mock
@pytest.mark.parametrize("header", CERTIFICATE_HEADER_KEYS)
async def test_contexts_by_excel_happy_path(async_client, header):
    cert = "С-ВЯ/15-01-2025/402123271"
    vri_id = "1-XYZ"

    # 1) /vri (по номеру свидетельства) → vri_id
    # 2) /vri (по данным эталона)      → свидетельство эталона (второй вызов того же URL)
    respx.get(f"{ARSHIN_BASE}/vri").mock(
        side_effect=[
            httpx.Response(200, json={"result": {"items": [{"vri_id": vri_id}]}}),
            httpx.Response(
                200,
                json={
                    "result": {
                        "items": [
                            {
                                "result_docnum": "ET-123",
                                "verification_date": "01.01.2025",
                                "valid_date": "31.12.2025",
                            }
                        ]
                    }
                },
            ),
        ]
    )

    # 3) /vri/{id} → детали для билдера
    respx.get(f"{ARSHIN_BASE}/vri/{vri_id}").mock(
        return_value=httpx.Response(
            200,
            json={
                "result": {
                    "means": {
                        "mieta": [
                            {
                                "regNumber": "77090.19.1Р.00761951",
                                "mitypeNumber": "77090-19",
                                "mitypeTitle": "Преобразователи давления эталонные",
                                "notation": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                                "manufactureNum": "3127",
                                "manufactureYear": 2020,
                                "rankCode": "1Р",
                                "rankTitle": "Эталон 1-го разряда",
                            }
                        ]
                    },
                    "vriInfo": {
                        "docTitle": "МИ 123-45",
                        "vrfDate": "15.01.2025",
                        "validDate": "14.01.2026",
                        "applicable": {"certNum": cert},
                    },
                }
            },
        )
    )

    xlsx = _make_protocols_excel_row(cert, header=header)
    files = {
        "file": (
            "input.xlsx",
            xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    r = await async_client.post("/api/v1/protocols/context-by-excel", files=files)

    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 1
    item = body["items"][0]

    # Проверяем основные поля
    assert item["certificate"] == cert
    assert item["vri_id"] == vri_id
    assert item["filename"] == "ABC123-б-150125-1"
    # В контексте должна появиться строка эталона
    assert "77090-19" in (item["context"] or {}).get("etalon_line", "")


@pytest.mark.anyio
@respx.mock
async def test_contexts_by_excel_empty_certificate(async_client):
    # Пустой номер → элемент с ошибкой
    xlsx = _make_protocols_excel_row("")
    files = {
        "file": (
            "input.xlsx",
            xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    r = await async_client.post("/api/v1/protocols/context-by-excel", files=files)

    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["error"] == "certificate number is empty"
    assert item["vri_id"] == ""


@pytest.mark.anyio
@respx.mock
async def test_contexts_by_excel_not_found(async_client):
    cert = "С-ВЯ/15-01-2025/000000001"
    # /vri не находит запись
    respx.get(f"{ARSHIN_BASE}/vri").mock(
        return_value=httpx.Response(200, json={"result": {"items": []}})
    )

    xlsx = _make_protocols_excel_row(cert)
    files = {
        "file": (
            "input.xlsx",
            xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    r = await async_client.post("/api/v1/protocols/context-by-excel", files=files)

    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["certificate"] == cert
    assert item["error"] == "not found"
    assert item["vri_id"] == ""


@pytest.mark.anyio
@respx.mock
async def test_manometers_pdf_files_happy_path(async_client, tmp_path, monkeypatch):
    cert = "С-ЕЖБ/05-06-2025/443771099"
    serial = "03607"
    protocol_num = "06/001/25"
    vri_id = "1-MANO"

    manometers_xlsx = _make_manometers_excel_row(certificate=cert, serial=serial)
    db_xlsx = _make_manometers_db_excel(
        serial=serial, certificate=cert, protocol_number=protocol_num
    )

    async def fake_pdf(html: str) -> bytes | None:
        assert "ПРОТОКОЛ" in html
        return b"%PDF-manometer%"

    monkeypatch.setattr("app.api.routes.protocols.html_to_pdf_bytes", fake_pdf)
    monkeypatch.setattr("app.api.routes.protocols.get_dated_exports_dir", lambda _day: tmp_path)

    respx.get(f"{ARSHIN_BASE}/vri").mock(
        side_effect=[
            httpx.Response(200, json={"result": {"items": [{"vri_id": vri_id}]}}),
            httpx.Response(
                200,
                json={
                    "result": {
                        "items": [
                            {
                                "result_docnum": "ET-123",
                                "verification_date": "01.01.2025",
                                "valid_date": "31.12.2025",
                            }
                        ]
                    }
                },
            ),
        ]
    )

    respx.get(f"{ARSHIN_BASE}/vri/{vri_id}").mock(
        return_value=httpx.Response(
            200,
            json={
                "result": {
                    "means": {
                        "mieta": [
                            {
                                "regNumber": "77090.19.1Р.00761951",
                                "mitypeNumber": "77090-19",
                                "mitypeTitle": "Преобразователи давления эталонные",
                                "notation": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                                "manufactureNum": "3127",
                                "manufactureYear": 2020,
                                "rankCode": "1Р",
                                "rankTitle": "Эталон 1-го разряда",
                            }
                        ]
                    },
                    "vriInfo": {
                        "docTitle": "МИ 123-45",
                        "vrfDate": "15.06.2025",
                        "validDate": "14.06.2026",
                        "applicable": {"certNum": cert},
                    },
                }
            },
        )
    )

    files = {
        "manometers_file": (
            "manometers.xlsx",
            manometers_xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
        "db_file": (
            "db.xlsx",
            db_xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
    }

    response = await async_client.post("/api/v1/protocols/manometers/pdf-files", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["errors"] == []
    assert len(body["files"]) == 1

    saved_path = Path(body["files"][0])
    assert saved_path.exists()
    assert saved_path.read_bytes() == b"%PDF-manometer%"
    assert saved_path.parent == tmp_path
    assert saved_path.name == "06-001-25.pdf"


@pytest.mark.anyio
@respx.mock
async def test_manometers_pdf_files_certificate_mismatch(async_client, tmp_path, monkeypatch):
    serial = "03607"
    excel_cert = "С-ЕЖБ/05-06-2025/443771999"
    db_cert = "С-ЕЖБ/05-06-2025/443771099"
    protocol_num = "06/001/25"

    manometers_xlsx = _make_manometers_excel_row(certificate=excel_cert, serial=serial)
    db_xlsx = _make_manometers_db_excel(
        serial=serial, certificate=db_cert, protocol_number=protocol_num
    )

    calls = {"pdf": 0}

    async def fake_pdf(html: str) -> bytes | None:
        calls["pdf"] += 1
        return b"%PDF%"

    monkeypatch.setattr("app.api.routes.protocols.html_to_pdf_bytes", fake_pdf)
    monkeypatch.setattr("app.api.routes.protocols.get_dated_exports_dir", lambda _day: tmp_path)

    files = {
        "manometers_file": (
            "manometers.xlsx",
            manometers_xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
        "db_file": (
            "db.xlsx",
            db_xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
    }

    response = await async_client.post("/api/v1/protocols/manometers/pdf-files", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 0
    assert body["files"] == []
    assert len(body["errors"]) == 1
    error = body["errors"][0]
    assert error["reason"] == "certificate mismatch between excel and db"
    assert error["serial"] == serial
    assert calls["pdf"] == 0

```

### 82. `tests/test_registry_ingest.py`

```python
from datetime import date

import pytest
from sqlalchemy import delete, select

from app.db import models
from app.db.session import get_sessionmaker
from app.services.registry_ingest import ingest_registry_rows


@pytest.mark.anyio
async def test_ingest_registry_rows_persists_owner_and_methodology():
    sessionmaker = get_sessionmaker()
    source_file = "test_ingest_registry.xlsx"
    owner_name = 'ООО "Тест Инжиниринг"'
    owner_inn = "1234567890"
    methodology_code = "МИ 2124-90"
    serial = " 03607 "

    rows = [
        {
            "Заводской №/ Буквенно-цифровое обозначение": serial,
            "Документ": "С-ЕЖБ/05-06-2025/443771099",
            "номер_протокола": "06/001/25",
            "Владелец СИ": owner_name,
            "ИНН": owner_inn,
            "Методика поверки": methodology_code,
            "Дата поверки": date(2025, 6, 5),
            "Действительно до": date(2026, 6, 4),
        }
    ]

    async with sessionmaker() as session:
        # cleanup in case of previous runs
        await session.execute(
            delete(models.VerificationRegistryEntry).where(
                models.VerificationRegistryEntry.source_file == source_file
            )
        )
        await session.execute(delete(models.Owner).where(models.Owner.name == owner_name))
        await session.commit()

        result = await ingest_registry_rows(
            session,
            source_file=source_file,
            rows=rows,
            source_sheet="tests",
        )

        assert result["processed"] == 1

        entry = (
            await session.execute(
                select(models.VerificationRegistryEntry).where(
                    models.VerificationRegistryEntry.source_file == source_file
                )
            )
        ).scalar_one()
        assert entry.normalized_serial == "03607"
        assert entry.document_no == "С-ЕЖБ/05-06-2025/443771099"

        owner = (
            await session.execute(select(models.Owner).where(models.Owner.name == owner_name))
        ).scalar_one()
        assert owner.inn == owner_inn

        methodology = (
            await session.execute(
                select(models.Methodology).where(models.Methodology.code == methodology_code)
            )
        ).scalar_one()
        assert methodology.allowable_variation_pct == pytest.approx(1.5)

        points = (
            (
                await session.execute(
                    select(models.MethodologyPoint)
                    .where(models.MethodologyPoint.methodology_id == methodology.id)
                    .order_by(models.MethodologyPoint.position)
                )
            )
            .scalars()
            .all()
        )
        point_labels = [point.label for point in points]
        assert "5.1" in point_labels
        assert "5.2.3" in point_labels

        # cleanup created data for isolation
        await session.execute(
            delete(models.VerificationRegistryEntry).where(
                models.VerificationRegistryEntry.source_file == source_file
            )
        )
        await session.execute(delete(models.Owner).where(models.Owner.name == owner_name))
        await session.commit()

```

### 83. `tests/test_repository_utils.py`

```python
from app.db.repositories import utils


def test_normalize_owner_alias_handles_quotes_and_case():
    assert utils.normalize_owner_alias(' "АО ""Прибор"" " ') == "ао прибор"


def test_normalize_methodology_alias_collapse_spaces():
    value = "МИ   2124-90 (ред. 2023)"
    assert utils.normalize_methodology_alias(value) == "ми 2124 90 ред 2023"

```

### 84. `tests/test_signatures.py`

```python
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

```

### 85. `tests/test_style.py`

```python
from __future__ import annotations

import subprocess
import sys


def test_ruff_clean() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

```

### 86. `uv.lock`

```
version = 1
revision = 3
requires-python = ">=3.13"

[[package]]
name = "alembic"
version = "1.16.5"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "mako" },
    { name = "sqlalchemy" },
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/9a/ca/4dc52902cf3491892d464f5265a81e9dff094692c8a049a3ed6a05fe7ee8/alembic-1.16.5.tar.gz", hash = "sha256:a88bb7f6e513bd4301ecf4c7f2206fe93f9913f9b48dac3b78babde2d6fe765e", size = 1969868, upload-time = "2025-08-27T18:02:05.668Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/39/4a/4c61d4c84cfd9befb6fa08a702535b27b21fff08c946bc2f6139decbf7f7/alembic-1.16.5-py3-none-any.whl", hash = "sha256:e845dfe090c5ffa7b92593ae6687c5cb1a101e91fa53868497dbd79847f9dbe3", size = 247355, upload-time = "2025-08-27T18:02:07.37Z" },
]

[[package]]
name = "annotated-types"
version = "0.7.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/ee/67/531ea369ba64dcff5ec9c3402f9f51bf748cec26dde048a2f973a4eea7f5/annotated_types-0.7.0.tar.gz", hash = "sha256:aff07c09a53a08bc8cfccb9c85b05f1aa9a2a6f23728d790723543408344ce89", size = 16081, upload-time = "2024-05-20T21:33:25.928Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/78/b6/6307fbef88d9b5ee7421e68d78a9f162e0da4900bc5f5793f6d3d0e34fb8/annotated_types-0.7.0-py3-none-any.whl", hash = "sha256:1f02e8b43a8fbbc3f3e0d4f0f4bfc8131bcb4eebe8849b8e5c773f3a1c582a53", size = 13643, upload-time = "2024-05-20T21:33:24.1Z" },
]

[[package]]
name = "anyio"
version = "4.10.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "idna" },
    { name = "sniffio" },
]
sdist = { url = "https://files.pythonhosted.org/packages/f1/b4/636b3b65173d3ce9a38ef5f0522789614e590dab6a8d505340a4efe4c567/anyio-4.10.0.tar.gz", hash = "sha256:3f3fae35c96039744587aa5b8371e7e8e603c0702999535961dd336026973ba6", size = 213252, upload-time = "2025-08-04T08:54:26.451Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/6f/12/e5e0282d673bb9746bacfb6e2dba8719989d3660cdb2ea79aee9a9651afb/anyio-4.10.0-py3-none-any.whl", hash = "sha256:60e474ac86736bbfd6f210f7a61218939c318f43f9972497381f1c5e930ed3d1", size = 107213, upload-time = "2025-08-04T08:54:24.882Z" },
]

[[package]]
name = "asyncpg"
version = "0.30.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/2f/4c/7c991e080e106d854809030d8584e15b2e996e26f16aee6d757e387bc17d/asyncpg-0.30.0.tar.gz", hash = "sha256:c551e9928ab6707602f44811817f82ba3c446e018bfe1d3abecc8ba5f3eac851", size = 957746, upload-time = "2024-10-20T00:30:41.127Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/3a/22/e20602e1218dc07692acf70d5b902be820168d6282e69ef0d3cb920dc36f/asyncpg-0.30.0-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:05b185ebb8083c8568ea8a40e896d5f7af4b8554b64d7719c0eaa1eb5a5c3a70", size = 670373, upload-time = "2024-10-20T00:29:55.165Z" },
    { url = "https://files.pythonhosted.org/packages/3d/b3/0cf269a9d647852a95c06eb00b815d0b95a4eb4b55aa2d6ba680971733b9/asyncpg-0.30.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:c47806b1a8cbb0a0db896f4cd34d89942effe353a5035c62734ab13b9f938da3", size = 634745, upload-time = "2024-10-20T00:29:57.14Z" },
    { url = "https://files.pythonhosted.org/packages/8e/6d/a4f31bf358ce8491d2a31bfe0d7bcf25269e80481e49de4d8616c4295a34/asyncpg-0.30.0-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:9b6fde867a74e8c76c71e2f64f80c64c0f3163e687f1763cfaf21633ec24ec33", size = 3512103, upload-time = "2024-10-20T00:29:58.499Z" },
    { url = "https://files.pythonhosted.org/packages/96/19/139227a6e67f407b9c386cb594d9628c6c78c9024f26df87c912fabd4368/asyncpg-0.30.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:46973045b567972128a27d40001124fbc821c87a6cade040cfcd4fa8a30bcdc4", size = 3592471, upload-time = "2024-10-20T00:30:00.354Z" },
    { url = "https://files.pythonhosted.org/packages/67/e4/ab3ca38f628f53f0fd28d3ff20edff1c975dd1cb22482e0061916b4b9a74/asyncpg-0.30.0-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:9110df111cabc2ed81aad2f35394a00cadf4f2e0635603db6ebbd0fc896f46a4", size = 3496253, upload-time = "2024-10-20T00:30:02.794Z" },
    { url = "https://files.pythonhosted.org/packages/ef/5f/0bf65511d4eeac3a1f41c54034a492515a707c6edbc642174ae79034d3ba/asyncpg-0.30.0-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:04ff0785ae7eed6cc138e73fc67b8e51d54ee7a3ce9b63666ce55a0bf095f7ba", size = 3662720, upload-time = "2024-10-20T00:30:04.501Z" },
    { url = "https://files.pythonhosted.org/packages/e7/31/1513d5a6412b98052c3ed9158d783b1e09d0910f51fbe0e05f56cc370bc4/asyncpg-0.30.0-cp313-cp313-win32.whl", hash = "sha256:ae374585f51c2b444510cdf3595b97ece4f233fde739aa14b50e0d64e8a7a590", size = 560404, upload-time = "2024-10-20T00:30:06.537Z" },
    { url = "https://files.pythonhosted.org/packages/c8/a4/cec76b3389c4c5ff66301cd100fe88c318563ec8a520e0b2e792b5b84972/asyncpg-0.30.0-cp313-cp313-win_amd64.whl", hash = "sha256:f59b430b8e27557c3fb9869222559f7417ced18688375825f8f12302c34e915e", size = 621623, upload-time = "2024-10-20T00:30:09.024Z" },
]

[[package]]
name = "black"
version = "25.1.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "click" },
    { name = "mypy-extensions" },
    { name = "packaging" },
    { name = "pathspec" },
    { name = "platformdirs" },
]
sdist = { url = "https://files.pythonhosted.org/packages/94/49/26a7b0f3f35da4b5a65f081943b7bcd22d7002f5f0fb8098ec1ff21cb6ef/black-25.1.0.tar.gz", hash = "sha256:33496d5cd1222ad73391352b4ae8da15253c5de89b93a80b3e2c8d9a19ec2666", size = 649449, upload-time = "2025-01-29T04:15:40.373Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/98/87/0edf98916640efa5d0696e1abb0a8357b52e69e82322628f25bf14d263d1/black-25.1.0-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:8f0b18a02996a836cc9c9c78e5babec10930862827b1b724ddfe98ccf2f2fe4f", size = 1650673, upload-time = "2025-01-29T05:37:20.574Z" },
    { url = "https://files.pythonhosted.org/packages/52/e5/f7bf17207cf87fa6e9b676576749c6b6ed0d70f179a3d812c997870291c3/black-25.1.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:afebb7098bfbc70037a053b91ae8437c3857482d3a690fefc03e9ff7aa9a5fd3", size = 1453190, upload-time = "2025-01-29T05:37:22.106Z" },
    { url = "https://files.pythonhosted.org/packages/e3/ee/adda3d46d4a9120772fae6de454c8495603c37c4c3b9c60f25b1ab6401fe/black-25.1.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:030b9759066a4ee5e5aca28c3c77f9c64789cdd4de8ac1df642c40b708be6171", size = 1782926, upload-time = "2025-01-29T04:18:58.564Z" },
    { url = "https://files.pythonhosted.org/packages/cc/64/94eb5f45dcb997d2082f097a3944cfc7fe87e071907f677e80788a2d7b7a/black-25.1.0-cp313-cp313-win_amd64.whl", hash = "sha256:a22f402b410566e2d1c950708c77ebf5ebd5d0d88a6a2e87c86d9fb48afa0d18", size = 1442613, upload-time = "2025-01-29T04:19:27.63Z" },
    { url = "https://files.pythonhosted.org/packages/09/71/54e999902aed72baf26bca0d50781b01838251a462612966e9fc4891eadd/black-25.1.0-py3-none-any.whl", hash = "sha256:95e8176dae143ba9097f351d174fdaf0ccd29efb414b362ae3fd72bf0f710717", size = 207646, upload-time = "2025-01-29T04:15:38.082Z" },
]

[[package]]
name = "certifi"
version = "2025.8.3"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/dc/67/960ebe6bf230a96cda2e0abcf73af550ec4f090005363542f0765df162e0/certifi-2025.8.3.tar.gz", hash = "sha256:e564105f78ded564e3ae7c923924435e1daa7463faeab5bb932bc53ffae63407", size = 162386, upload-time = "2025-08-03T03:07:47.08Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/e5/48/1549795ba7742c948d2ad169c1c8cdbae65bc450d6cd753d124b17c8cd32/certifi-2025.8.3-py3-none-any.whl", hash = "sha256:f6c12493cfb1b06ba2ff328595af9350c65d6644968e5d3a2ffd78699af217a5", size = 161216, upload-time = "2025-08-03T03:07:45.777Z" },
]

[[package]]
name = "click"
version = "8.2.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "colorama", marker = "sys_platform == 'win32'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/60/6c/8ca2efa64cf75a977a0d7fac081354553ebe483345c734fb6b6515d96bbc/click-8.2.1.tar.gz", hash = "sha256:27c491cc05d968d271d5a1db13e3b5a184636d9d930f148c50b038f0d0646202", size = 286342, upload-time = "2025-05-20T23:19:49.832Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/85/32/10bb5764d90a8eee674e9dc6f4db6a0ab47c8c4d0d83c27f7c39ac415a4d/click-8.2.1-py3-none-any.whl", hash = "sha256:61a3265b914e850b85317d0b3109c7f8cd35a670f963866005d6ef1d5175a12b", size = 102215, upload-time = "2025-05-20T23:19:47.796Z" },
]

[[package]]
name = "colorama"
version = "0.4.6"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/d8/53/6f443c9a4a8358a93a6792e2acffb9d9d5cb0a5cfd8802644b7b1c9a02e4/colorama-0.4.6.tar.gz", hash = "sha256:08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44", size = 27697, upload-time = "2022-10-25T02:36:22.414Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d1/d6/3965ed04c63042e047cb6a3e6ed1a63a35087b6a609aa3a15ed8ac56c221/colorama-0.4.6-py2.py3-none-any.whl", hash = "sha256:4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6", size = 25335, upload-time = "2022-10-25T02:36:20.889Z" },
]

[[package]]
name = "coverage"
version = "7.10.6"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/14/70/025b179c993f019105b79575ac6edb5e084fb0f0e63f15cdebef4e454fb5/coverage-7.10.6.tar.gz", hash = "sha256:f644a3ae5933a552a29dbb9aa2f90c677a875f80ebea028e5a52a4f429044b90", size = 823736, upload-time = "2025-08-29T15:35:16.668Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/bd/e7/917e5953ea29a28c1057729c1d5af9084ab6d9c66217523fd0e10f14d8f6/coverage-7.10.6-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:ffea0575345e9ee0144dfe5701aa17f3ba546f8c3bb48db62ae101afb740e7d6", size = 217351, upload-time = "2025-08-29T15:33:45.438Z" },
    { url = "https://files.pythonhosted.org/packages/eb/86/2e161b93a4f11d0ea93f9bebb6a53f113d5d6e416d7561ca41bb0a29996b/coverage-7.10.6-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:95d91d7317cde40a1c249d6b7382750b7e6d86fad9d8eaf4fa3f8f44cf171e80", size = 217600, upload-time = "2025-08-29T15:33:47.269Z" },
    { url = "https://files.pythonhosted.org/packages/0e/66/d03348fdd8df262b3a7fb4ee5727e6e4936e39e2f3a842e803196946f200/coverage-7.10.6-cp313-cp313-manylinux1_i686.manylinux_2_28_i686.manylinux_2_5_i686.whl", hash = "sha256:3e23dd5408fe71a356b41baa82892772a4cefcf758f2ca3383d2aa39e1b7a003", size = 248600, upload-time = "2025-08-29T15:33:48.953Z" },
    { url = "https://files.pythonhosted.org/packages/73/dd/508420fb47d09d904d962f123221bc249f64b5e56aa93d5f5f7603be475f/coverage-7.10.6-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:0f3f56e4cb573755e96a16501a98bf211f100463d70275759e73f3cbc00d4f27", size = 251206, upload-time = "2025-08-29T15:33:50.697Z" },
    { url = "https://files.pythonhosted.org/packages/e9/1f/9020135734184f439da85c70ea78194c2730e56c2d18aee6e8ff1719d50d/coverage-7.10.6-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:db4a1d897bbbe7339946ffa2fe60c10cc81c43fab8b062d3fcb84188688174a4", size = 252478, upload-time = "2025-08-29T15:33:52.303Z" },
    { url = "https://files.pythonhosted.org/packages/a4/a4/3d228f3942bb5a2051fde28c136eea23a761177dc4ff4ef54533164ce255/coverage-7.10.6-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:d8fd7879082953c156d5b13c74aa6cca37f6a6f4747b39538504c3f9c63d043d", size = 250637, upload-time = "2025-08-29T15:33:53.67Z" },
    { url = "https://files.pythonhosted.org/packages/36/e3/293dce8cdb9a83de971637afc59b7190faad60603b40e32635cbd15fbf61/coverage-7.10.6-cp313-cp313-musllinux_1_2_i686.whl", hash = "sha256:28395ca3f71cd103b8c116333fa9db867f3a3e1ad6a084aa3725ae002b6583bc", size = 248529, upload-time = "2025-08-29T15:33:55.022Z" },
    { url = "https://files.pythonhosted.org/packages/90/26/64eecfa214e80dd1d101e420cab2901827de0e49631d666543d0e53cf597/coverage-7.10.6-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:61c950fc33d29c91b9e18540e1aed7d9f6787cc870a3e4032493bbbe641d12fc", size = 250143, upload-time = "2025-08-29T15:33:56.386Z" },
    { url = "https://files.pythonhosted.org/packages/3e/70/bd80588338f65ea5b0d97e424b820fb4068b9cfb9597fbd91963086e004b/coverage-7.10.6-cp313-cp313-win32.whl", hash = "sha256:160c00a5e6b6bdf4e5984b0ef21fc860bc94416c41b7df4d63f536d17c38902e", size = 219770, upload-time = "2025-08-29T15:33:58.063Z" },
    { url = "https://files.pythonhosted.org/packages/a7/14/0b831122305abcc1060c008f6c97bbdc0a913ab47d65070a01dc50293c2b/coverage-7.10.6-cp313-cp313-win_amd64.whl", hash = "sha256:628055297f3e2aa181464c3808402887643405573eb3d9de060d81531fa79d32", size = 220566, upload-time = "2025-08-29T15:33:59.766Z" },
    { url = "https://files.pythonhosted.org/packages/83/c6/81a83778c1f83f1a4a168ed6673eeedc205afb562d8500175292ca64b94e/coverage-7.10.6-cp313-cp313-win_arm64.whl", hash = "sha256:df4ec1f8540b0bcbe26ca7dd0f541847cc8a108b35596f9f91f59f0c060bfdd2", size = 219195, upload-time = "2025-08-29T15:34:01.191Z" },
    { url = "https://files.pythonhosted.org/packages/d7/1c/ccccf4bf116f9517275fa85047495515add43e41dfe8e0bef6e333c6b344/coverage-7.10.6-cp313-cp313t-macosx_10_13_x86_64.whl", hash = "sha256:c9a8b7a34a4de3ed987f636f71881cd3b8339f61118b1aa311fbda12741bff0b", size = 218059, upload-time = "2025-08-29T15:34:02.91Z" },
    { url = "https://files.pythonhosted.org/packages/92/97/8a3ceff833d27c7492af4f39d5da6761e9ff624831db9e9f25b3886ddbca/coverage-7.10.6-cp313-cp313t-macosx_11_0_arm64.whl", hash = "sha256:8dd5af36092430c2b075cee966719898f2ae87b636cefb85a653f1d0ba5d5393", size = 218287, upload-time = "2025-08-29T15:34:05.106Z" },
    { url = "https://files.pythonhosted.org/packages/92/d8/50b4a32580cf41ff0423777a2791aaf3269ab60c840b62009aec12d3970d/coverage-7.10.6-cp313-cp313t-manylinux1_i686.manylinux_2_28_i686.manylinux_2_5_i686.whl", hash = "sha256:b0353b0f0850d49ada66fdd7d0c7cdb0f86b900bb9e367024fd14a60cecc1e27", size = 259625, upload-time = "2025-08-29T15:34:06.575Z" },
    { url = "https://files.pythonhosted.org/packages/7e/7e/6a7df5a6fb440a0179d94a348eb6616ed4745e7df26bf2a02bc4db72c421/coverage-7.10.6-cp313-cp313t-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:d6b9ae13d5d3e8aeca9ca94198aa7b3ebbc5acfada557d724f2a1f03d2c0b0df", size = 261801, upload-time = "2025-08-29T15:34:08.006Z" },
    { url = "https://files.pythonhosted.org/packages/3a/4c/a270a414f4ed5d196b9d3d67922968e768cd971d1b251e1b4f75e9362f75/coverage-7.10.6-cp313-cp313t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:675824a363cc05781b1527b39dc2587b8984965834a748177ee3c37b64ffeafb", size = 264027, upload-time = "2025-08-29T15:34:09.806Z" },
    { url = "https://files.pythonhosted.org/packages/9c/8b/3210d663d594926c12f373c5370bf1e7c5c3a427519a8afa65b561b9a55c/coverage-7.10.6-cp313-cp313t-musllinux_1_2_aarch64.whl", hash = "sha256:692d70ea725f471a547c305f0d0fc6a73480c62fb0da726370c088ab21aed282", size = 261576, upload-time = "2025-08-29T15:34:11.585Z" },
    { url = "https://files.pythonhosted.org/packages/72/d0/e1961eff67e9e1dba3fc5eb7a4caf726b35a5b03776892da8d79ec895775/coverage-7.10.6-cp313-cp313t-musllinux_1_2_i686.whl", hash = "sha256:851430a9a361c7a8484a36126d1d0ff8d529d97385eacc8dfdc9bfc8c2d2cbe4", size = 259341, upload-time = "2025-08-29T15:34:13.159Z" },
    { url = "https://files.pythonhosted.org/packages/3a/06/d6478d152cd189b33eac691cba27a40704990ba95de49771285f34a5861e/coverage-7.10.6-cp313-cp313t-musllinux_1_2_x86_64.whl", hash = "sha256:d9369a23186d189b2fc95cc08b8160ba242057e887d766864f7adf3c46b2df21", size = 260468, upload-time = "2025-08-29T15:34:14.571Z" },
    { url = "https://files.pythonhosted.org/packages/ed/73/737440247c914a332f0b47f7598535b29965bf305e19bbc22d4c39615d2b/coverage-7.10.6-cp313-cp313t-win32.whl", hash = "sha256:92be86fcb125e9bda0da7806afd29a3fd33fdf58fba5d60318399adf40bf37d0", size = 220429, upload-time = "2025-08-29T15:34:16.394Z" },
    { url = "https://files.pythonhosted.org/packages/bd/76/b92d3214740f2357ef4a27c75a526eb6c28f79c402e9f20a922c295c05e2/coverage-7.10.6-cp313-cp313t-win_amd64.whl", hash = "sha256:6b3039e2ca459a70c79523d39347d83b73f2f06af5624905eba7ec34d64d80b5", size = 221493, upload-time = "2025-08-29T15:34:17.835Z" },
    { url = "https://files.pythonhosted.org/packages/fc/8e/6dcb29c599c8a1f654ec6cb68d76644fe635513af16e932d2d4ad1e5ac6e/coverage-7.10.6-cp313-cp313t-win_arm64.whl", hash = "sha256:3fb99d0786fe17b228eab663d16bee2288e8724d26a199c29325aac4b0319b9b", size = 219757, upload-time = "2025-08-29T15:34:19.248Z" },
    { url = "https://files.pythonhosted.org/packages/d3/aa/76cf0b5ec00619ef208da4689281d48b57f2c7fde883d14bf9441b74d59f/coverage-7.10.6-cp314-cp314-macosx_10_13_x86_64.whl", hash = "sha256:6008a021907be8c4c02f37cdc3ffb258493bdebfeaf9a839f9e71dfdc47b018e", size = 217331, upload-time = "2025-08-29T15:34:20.846Z" },
    { url = "https://files.pythonhosted.org/packages/65/91/8e41b8c7c505d398d7730206f3cbb4a875a35ca1041efc518051bfce0f6b/coverage-7.10.6-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:5e75e37f23eb144e78940b40395b42f2321951206a4f50e23cfd6e8a198d3ceb", size = 217607, upload-time = "2025-08-29T15:34:22.433Z" },
    { url = "https://files.pythonhosted.org/packages/87/7f/f718e732a423d442e6616580a951b8d1ec3575ea48bcd0e2228386805e79/coverage-7.10.6-cp314-cp314-manylinux1_i686.manylinux_2_28_i686.manylinux_2_5_i686.whl", hash = "sha256:0f7cb359a448e043c576f0da00aa8bfd796a01b06aa610ca453d4dde09cc1034", size = 248663, upload-time = "2025-08-29T15:34:24.425Z" },
    { url = "https://files.pythonhosted.org/packages/e6/52/c1106120e6d801ac03e12b5285e971e758e925b6f82ee9b86db3aa10045d/coverage-7.10.6-cp314-cp314-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:c68018e4fc4e14b5668f1353b41ccf4bc83ba355f0e1b3836861c6f042d89ac1", size = 251197, upload-time = "2025-08-29T15:34:25.906Z" },
    { url = "https://files.pythonhosted.org/packages/3d/ec/3a8645b1bb40e36acde9c0609f08942852a4af91a937fe2c129a38f2d3f5/coverage-7.10.6-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:cd4b2b0707fc55afa160cd5fc33b27ccbf75ca11d81f4ec9863d5793fc6df56a", size = 252551, upload-time = "2025-08-29T15:34:27.337Z" },
    { url = "https://files.pythonhosted.org/packages/a1/70/09ecb68eeb1155b28a1d16525fd3a9b65fbe75337311a99830df935d62b6/coverage-7.10.6-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:4cec13817a651f8804a86e4f79d815b3b28472c910e099e4d5a0e8a3b6a1d4cb", size = 250553, upload-time = "2025-08-29T15:34:29.065Z" },
    { url = "https://files.pythonhosted.org/packages/c6/80/47df374b893fa812e953b5bc93dcb1427a7b3d7a1a7d2db33043d17f74b9/coverage-7.10.6-cp314-cp314-musllinux_1_2_i686.whl", hash = "sha256:f2a6a8e06bbda06f78739f40bfb56c45d14eb8249d0f0ea6d4b3d48e1f7c695d", size = 248486, upload-time = "2025-08-29T15:34:30.897Z" },
    { url = "https://files.pythonhosted.org/packages/4a/65/9f98640979ecee1b0d1a7164b589de720ddf8100d1747d9bbdb84be0c0fb/coverage-7.10.6-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:081b98395ced0d9bcf60ada7661a0b75f36b78b9d7e39ea0790bb4ed8da14747", size = 249981, upload-time = "2025-08-29T15:34:32.365Z" },
    { url = "https://files.pythonhosted.org/packages/1f/55/eeb6603371e6629037f47bd25bef300387257ed53a3c5fdb159b7ac8c651/coverage-7.10.6-cp314-cp314-win32.whl", hash = "sha256:6937347c5d7d069ee776b2bf4e1212f912a9f1f141a429c475e6089462fcecc5", size = 220054, upload-time = "2025-08-29T15:34:34.124Z" },
    { url = "https://files.pythonhosted.org/packages/15/d1/a0912b7611bc35412e919a2cd59ae98e7ea3b475e562668040a43fb27897/coverage-7.10.6-cp314-cp314-win_amd64.whl", hash = "sha256:adec1d980fa07e60b6ef865f9e5410ba760e4e1d26f60f7e5772c73b9a5b0713", size = 220851, upload-time = "2025-08-29T15:34:35.651Z" },
    { url = "https://files.pythonhosted.org/packages/ef/2d/11880bb8ef80a45338e0b3e0725e4c2d73ffbb4822c29d987078224fd6a5/coverage-7.10.6-cp314-cp314-win_arm64.whl", hash = "sha256:a80f7aef9535442bdcf562e5a0d5a5538ce8abe6bb209cfbf170c462ac2c2a32", size = 219429, upload-time = "2025-08-29T15:34:37.16Z" },
    { url = "https://files.pythonhosted.org/packages/83/c0/1f00caad775c03a700146f55536ecd097a881ff08d310a58b353a1421be0/coverage-7.10.6-cp314-cp314t-macosx_10_13_x86_64.whl", hash = "sha256:0de434f4fbbe5af4fa7989521c655c8c779afb61c53ab561b64dcee6149e4c65", size = 218080, upload-time = "2025-08-29T15:34:38.919Z" },
    { url = "https://files.pythonhosted.org/packages/a9/c4/b1c5d2bd7cc412cbeb035e257fd06ed4e3e139ac871d16a07434e145d18d/coverage-7.10.6-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:6e31b8155150c57e5ac43ccd289d079eb3f825187d7c66e755a055d2c85794c6", size = 218293, upload-time = "2025-08-29T15:34:40.425Z" },
    { url = "https://files.pythonhosted.org/packages/3f/07/4468d37c94724bf6ec354e4ec2f205fda194343e3e85fd2e59cec57e6a54/coverage-7.10.6-cp314-cp314t-manylinux1_i686.manylinux_2_28_i686.manylinux_2_5_i686.whl", hash = "sha256:98cede73eb83c31e2118ae8d379c12e3e42736903a8afcca92a7218e1f2903b0", size = 259800, upload-time = "2025-08-29T15:34:41.996Z" },
    { url = "https://files.pythonhosted.org/packages/82/d8/f8fb351be5fee31690cd8da768fd62f1cfab33c31d9f7baba6cd8960f6b8/coverage-7.10.6-cp314-cp314t-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:f863c08f4ff6b64fa8045b1e3da480f5374779ef187f07b82e0538c68cb4ff8e", size = 261965, upload-time = "2025-08-29T15:34:43.61Z" },
    { url = "https://files.pythonhosted.org/packages/e8/70/65d4d7cfc75c5c6eb2fed3ee5cdf420fd8ae09c4808723a89a81d5b1b9c3/coverage-7.10.6-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:2b38261034fda87be356f2c3f42221fdb4171c3ce7658066ae449241485390d5", size = 264220, upload-time = "2025-08-29T15:34:45.387Z" },
    { url = "https://files.pythonhosted.org/packages/98/3c/069df106d19024324cde10e4ec379fe2fb978017d25e97ebee23002fbadf/coverage-7.10.6-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:0e93b1476b79eae849dc3872faeb0bf7948fd9ea34869590bc16a2a00b9c82a7", size = 261660, upload-time = "2025-08-29T15:34:47.288Z" },
    { url = "https://files.pythonhosted.org/packages/fc/8a/2974d53904080c5dc91af798b3a54a4ccb99a45595cc0dcec6eb9616a57d/coverage-7.10.6-cp314-cp314t-musllinux_1_2_i686.whl", hash = "sha256:ff8a991f70f4c0cf53088abf1e3886edcc87d53004c7bb94e78650b4d3dac3b5", size = 259417, upload-time = "2025-08-29T15:34:48.779Z" },
    { url = "https://files.pythonhosted.org/packages/30/38/9616a6b49c686394b318974d7f6e08f38b8af2270ce7488e879888d1e5db/coverage-7.10.6-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:ac765b026c9f33044419cbba1da913cfb82cca1b60598ac1c7a5ed6aac4621a0", size = 260567, upload-time = "2025-08-29T15:34:50.718Z" },
    { url = "https://files.pythonhosted.org/packages/76/16/3ed2d6312b371a8cf804abf4e14895b70e4c3491c6e53536d63fd0958a8d/coverage-7.10.6-cp314-cp314t-win32.whl", hash = "sha256:441c357d55f4936875636ef2cfb3bee36e466dcf50df9afbd398ce79dba1ebb7", size = 220831, upload-time = "2025-08-29T15:34:52.653Z" },
    { url = "https://files.pythonhosted.org/packages/d5/e5/d38d0cb830abede2adb8b147770d2a3d0e7fecc7228245b9b1ae6c24930a/coverage-7.10.6-cp314-cp314t-win_amd64.whl", hash = "sha256:073711de3181b2e204e4870ac83a7c4853115b42e9cd4d145f2231e12d670930", size = 221950, upload-time = "2025-08-29T15:34:54.212Z" },
    { url = "https://files.pythonhosted.org/packages/f4/51/e48e550f6279349895b0ffcd6d2a690e3131ba3a7f4eafccc141966d4dea/coverage-7.10.6-cp314-cp314t-win_arm64.whl", hash = "sha256:137921f2bac5559334ba66122b753db6dc5d1cf01eb7b64eb412bb0d064ef35b", size = 219969, upload-time = "2025-08-29T15:34:55.83Z" },
    { url = "https://files.pythonhosted.org/packages/44/0c/50db5379b615854b5cf89146f8f5bd1d5a9693d7f3a987e269693521c404/coverage-7.10.6-py3-none-any.whl", hash = "sha256:92c4ecf6bf11b2e85fd4d8204814dc26e6a19f0c9d938c207c5cb0eadfcabbe3", size = 208986, upload-time = "2025-08-29T15:35:14.506Z" },
]

[[package]]
name = "et-xmlfile"
version = "2.0.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/d3/38/af70d7ab1ae9d4da450eeec1fa3918940a5fafb9055e934af8d6eb0c2313/et_xmlfile-2.0.0.tar.gz", hash = "sha256:dab3f4764309081ce75662649be815c4c9081e88f0837825f90fd28317d4da54", size = 17234, upload-time = "2024-10-25T17:25:40.039Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/c1/8b/5fe2cc11fee489817272089c4203e679c63b570a5aaeb18d852ae3cbba6a/et_xmlfile-2.0.0-py3-none-any.whl", hash = "sha256:7a91720bc756843502c3b7504c77b8fe44217c85c537d85037f0f536151b2caa", size = 18059, upload-time = "2024-10-25T17:25:39.051Z" },
]

[[package]]
name = "fastapi"
version = "0.116.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pydantic" },
    { name = "starlette" },
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/78/d7/6c8b3bfe33eeffa208183ec037fee0cce9f7f024089ab1c5d12ef04bd27c/fastapi-0.116.1.tar.gz", hash = "sha256:ed52cbf946abfd70c5a0dccb24673f0670deeb517a88b3544d03c2a6bf283143", size = 296485, upload-time = "2025-07-11T16:22:32.057Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/e5/47/d63c60f59a59467fda0f93f46335c9d18526d7071f025cb5b89d5353ea42/fastapi-0.116.1-py3-none-any.whl", hash = "sha256:c46ac7c312df840f0c9e220f7964bada936781bc4e2e6eb71f1c4d7553786565", size = 95631, upload-time = "2025-07-11T16:22:30.485Z" },
]

[[package]]
name = "greenlet"
version = "3.2.4"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/03/b8/704d753a5a45507a7aab61f18db9509302ed3d0a27ac7e0359ec2905b1a6/greenlet-3.2.4.tar.gz", hash = "sha256:0dca0d95ff849f9a364385f36ab49f50065d76964944638be9691e1832e9f86d", size = 188260, upload-time = "2025-08-07T13:24:33.51Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/49/e8/58c7f85958bda41dafea50497cbd59738c5c43dbbea5ee83d651234398f4/greenlet-3.2.4-cp313-cp313-macosx_11_0_universal2.whl", hash = "sha256:1a921e542453fe531144e91e1feedf12e07351b1cf6c9e8a3325ea600a715a31", size = 272814, upload-time = "2025-08-07T13:15:50.011Z" },
    { url = "https://files.pythonhosted.org/packages/62/dd/b9f59862e9e257a16e4e610480cfffd29e3fae018a68c2332090b53aac3d/greenlet-3.2.4-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:cd3c8e693bff0fff6ba55f140bf390fa92c994083f838fece0f63be121334945", size = 641073, upload-time = "2025-08-07T13:42:57.23Z" },
    { url = "https://files.pythonhosted.org/packages/f7/0b/bc13f787394920b23073ca3b6c4a7a21396301ed75a655bcb47196b50e6e/greenlet-3.2.4-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:710638eb93b1fa52823aa91bf75326f9ecdfd5e0466f00789246a5280f4ba0fc", size = 655191, upload-time = "2025-08-07T13:45:29.752Z" },
    { url = "https://files.pythonhosted.org/packages/f2/d6/6adde57d1345a8d0f14d31e4ab9c23cfe8e2cd39c3baf7674b4b0338d266/greenlet-3.2.4-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.whl", hash = "sha256:c5111ccdc9c88f423426df3fd1811bfc40ed66264d35aa373420a34377efc98a", size = 649516, upload-time = "2025-08-07T13:53:16.314Z" },
    { url = "https://files.pythonhosted.org/packages/7f/3b/3a3328a788d4a473889a2d403199932be55b1b0060f4ddd96ee7cdfcad10/greenlet-3.2.4-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:d76383238584e9711e20ebe14db6c88ddcedc1829a9ad31a584389463b5aa504", size = 652169, upload-time = "2025-08-07T13:18:32.861Z" },
    { url = "https://files.pythonhosted.org/packages/ee/43/3cecdc0349359e1a527cbf2e3e28e5f8f06d3343aaf82ca13437a9aa290f/greenlet-3.2.4-cp313-cp313-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:23768528f2911bcd7e475210822ffb5254ed10d71f4028387e5a99b4c6699671", size = 610497, upload-time = "2025-08-07T13:18:31.636Z" },
    { url = "https://files.pythonhosted.org/packages/b8/19/06b6cf5d604e2c382a6f31cafafd6f33d5dea706f4db7bdab184bad2b21d/greenlet-3.2.4-cp313-cp313-musllinux_1_1_aarch64.whl", hash = "sha256:00fadb3fedccc447f517ee0d3fd8fe49eae949e1cd0f6a611818f4f6fb7dc83b", size = 1121662, upload-time = "2025-08-07T13:42:41.117Z" },
    { url = "https://files.pythonhosted.org/packages/a2/15/0d5e4e1a66fab130d98168fe984c509249c833c1a3c16806b90f253ce7b9/greenlet-3.2.4-cp313-cp313-musllinux_1_1_x86_64.whl", hash = "sha256:d25c5091190f2dc0eaa3f950252122edbbadbb682aa7b1ef2f8af0f8c0afefae", size = 1149210, upload-time = "2025-08-07T13:18:24.072Z" },
    { url = "https://files.pythonhosted.org/packages/0b/55/2321e43595e6801e105fcfdee02b34c0f996eb71e6ddffca6b10b7e1d771/greenlet-3.2.4-cp313-cp313-win_amd64.whl", hash = "sha256:554b03b6e73aaabec3745364d6239e9e012d64c68ccd0b8430c64ccc14939a8b", size = 299685, upload-time = "2025-08-07T13:24:38.824Z" },
    { url = "https://files.pythonhosted.org/packages/22/5c/85273fd7cc388285632b0498dbbab97596e04b154933dfe0f3e68156c68c/greenlet-3.2.4-cp314-cp314-macosx_11_0_universal2.whl", hash = "sha256:49a30d5fda2507ae77be16479bdb62a660fa51b1eb4928b524975b3bde77b3c0", size = 273586, upload-time = "2025-08-07T13:16:08.004Z" },
    { url = "https://files.pythonhosted.org/packages/d1/75/10aeeaa3da9332c2e761e4c50d4c3556c21113ee3f0afa2cf5769946f7a3/greenlet-3.2.4-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:299fd615cd8fc86267b47597123e3f43ad79c9d8a22bebdce535e53550763e2f", size = 686346, upload-time = "2025-08-07T13:42:59.944Z" },
    { url = "https://files.pythonhosted.org/packages/c0/aa/687d6b12ffb505a4447567d1f3abea23bd20e73a5bed63871178e0831b7a/greenlet-3.2.4-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:c17b6b34111ea72fc5a4e4beec9711d2226285f0386ea83477cbb97c30a3f3a5", size = 699218, upload-time = "2025-08-07T13:45:30.969Z" },
    { url = "https://files.pythonhosted.org/packages/dc/8b/29aae55436521f1d6f8ff4e12fb676f3400de7fcf27fccd1d4d17fd8fecd/greenlet-3.2.4-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.whl", hash = "sha256:b4a1870c51720687af7fa3e7cda6d08d801dae660f75a76f3845b642b4da6ee1", size = 694659, upload-time = "2025-08-07T13:53:17.759Z" },
    { url = "https://files.pythonhosted.org/packages/92/2e/ea25914b1ebfde93b6fc4ff46d6864564fba59024e928bdc7de475affc25/greenlet-3.2.4-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:061dc4cf2c34852b052a8620d40f36324554bc192be474b9e9770e8c042fd735", size = 695355, upload-time = "2025-08-07T13:18:34.517Z" },
    { url = "https://files.pythonhosted.org/packages/72/60/fc56c62046ec17f6b0d3060564562c64c862948c9d4bc8aa807cf5bd74f4/greenlet-3.2.4-cp314-cp314-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:44358b9bf66c8576a9f57a590d5f5d6e72fa4228b763d0e43fee6d3b06d3a337", size = 657512, upload-time = "2025-08-07T13:18:33.969Z" },
    { url = "https://files.pythonhosted.org/packages/e3/a5/6ddab2b4c112be95601c13428db1d8b6608a8b6039816f2ba09c346c08fc/greenlet-3.2.4-cp314-cp314-win_amd64.whl", hash = "sha256:e37ab26028f12dbb0ff65f29a8d3d44a765c61e729647bf2ddfbbed621726f01", size = 303425, upload-time = "2025-08-07T13:32:27.59Z" },
]

[[package]]
name = "h11"
version = "0.16.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/01/ee/02a2c011bdab74c6fb3c75474d40b3052059d95df7e73351460c8588d963/h11-0.16.0.tar.gz", hash = "sha256:4e35b956cf45792e4caa5885e69fba00bdbc6ffafbfa020300e549b208ee5ff1", size = 101250, upload-time = "2025-04-24T03:35:25.427Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/04/4b/29cac41a4d98d144bf5f6d33995617b185d14b22401f75ca86f384e87ff1/h11-0.16.0-py3-none-any.whl", hash = "sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86", size = 37515, upload-time = "2025-04-24T03:35:24.344Z" },
]

[[package]]
name = "httpcore"
version = "1.0.9"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "certifi" },
    { name = "h11" },
]
sdist = { url = "https://files.pythonhosted.org/packages/06/94/82699a10bca87a5556c9c59b5963f2d039dbd239f25bc2a63907a05a14cb/httpcore-1.0.9.tar.gz", hash = "sha256:6e34463af53fd2ab5d807f399a9b45ea31c3dfa2276f15a2c3f00afff6e176e8", size = 85484, upload-time = "2025-04-24T22:06:22.219Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/7e/f5/f66802a942d491edb555dd61e3a9961140fd64c90bce1eafd741609d334d/httpcore-1.0.9-py3-none-any.whl", hash = "sha256:2d400746a40668fc9dec9810239072b40b4484b640a8c38fd654a024c7a1bf55", size = 78784, upload-time = "2025-04-24T22:06:20.566Z" },
]

[[package]]
name = "httptools"
version = "0.6.4"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/a7/9a/ce5e1f7e131522e6d3426e8e7a490b3a01f39a6696602e1c4f33f9e94277/httptools-0.6.4.tar.gz", hash = "sha256:4e93eee4add6493b59a5c514da98c939b244fce4a0d8879cd3f466562f4b7d5c", size = 240639, upload-time = "2024-10-16T19:45:08.902Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/94/a3/9fe9ad23fd35f7de6b91eeb60848986058bd8b5a5c1e256f5860a160cc3e/httptools-0.6.4-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:ade273d7e767d5fae13fa637f4d53b6e961fb7fd93c7797562663f0171c26660", size = 197214, upload-time = "2024-10-16T19:44:38.738Z" },
    { url = "https://files.pythonhosted.org/packages/ea/d9/82d5e68bab783b632023f2fa31db20bebb4e89dfc4d2293945fd68484ee4/httptools-0.6.4-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:856f4bc0478ae143bad54a4242fccb1f3f86a6e1be5548fecfd4102061b3a083", size = 102431, upload-time = "2024-10-16T19:44:39.818Z" },
    { url = "https://files.pythonhosted.org/packages/96/c1/cb499655cbdbfb57b577734fde02f6fa0bbc3fe9fb4d87b742b512908dff/httptools-0.6.4-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:322d20ea9cdd1fa98bd6a74b77e2ec5b818abdc3d36695ab402a0de8ef2865a3", size = 473121, upload-time = "2024-10-16T19:44:41.189Z" },
    { url = "https://files.pythonhosted.org/packages/af/71/ee32fd358f8a3bb199b03261f10921716990808a675d8160b5383487a317/httptools-0.6.4-cp313-cp313-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:4d87b29bd4486c0093fc64dea80231f7c7f7eb4dc70ae394d70a495ab8436071", size = 473805, upload-time = "2024-10-16T19:44:42.384Z" },
    { url = "https://files.pythonhosted.org/packages/8a/0a/0d4df132bfca1507114198b766f1737d57580c9ad1cf93c1ff673e3387be/httptools-0.6.4-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:342dd6946aa6bda4b8f18c734576106b8a31f2fe31492881a9a160ec84ff4bd5", size = 448858, upload-time = "2024-10-16T19:44:43.959Z" },
    { url = "https://files.pythonhosted.org/packages/1e/6a/787004fdef2cabea27bad1073bf6a33f2437b4dbd3b6fb4a9d71172b1c7c/httptools-0.6.4-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:4b36913ba52008249223042dca46e69967985fb4051951f94357ea681e1f5dc0", size = 452042, upload-time = "2024-10-16T19:44:45.071Z" },
    { url = "https://files.pythonhosted.org/packages/4d/dc/7decab5c404d1d2cdc1bb330b1bf70e83d6af0396fd4fc76fc60c0d522bf/httptools-0.6.4-cp313-cp313-win_amd64.whl", hash = "sha256:28908df1b9bb8187393d5b5db91435ccc9c8e891657f9cbb42a2541b44c82fc8", size = 87682, upload-time = "2024-10-16T19:44:46.46Z" },
]

[[package]]
name = "httpx"
version = "0.28.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "anyio" },
    { name = "certifi" },
    { name = "httpcore" },
    { name = "idna" },
]
sdist = { url = "https://files.pythonhosted.org/packages/b1/df/48c586a5fe32a0f01324ee087459e112ebb7224f646c0b5023f5e79e9956/httpx-0.28.1.tar.gz", hash = "sha256:75e98c5f16b0f35b567856f597f06ff2270a374470a5c2392242528e3e3e42fc", size = 141406, upload-time = "2024-12-06T15:37:23.222Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/2a/39/e50c7c3a983047577ee07d2a9e53faf5a69493943ec3f6a384bdc792deb2/httpx-0.28.1-py3-none-any.whl", hash = "sha256:d909fcccc110f8c7faf814ca82a9a4d816bc5a6dbfea25d6591d6985b8ba59ad", size = 73517, upload-time = "2024-12-06T15:37:21.509Z" },
]

[[package]]
name = "idna"
version = "3.10"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/f1/70/7703c29685631f5a7590aa73f1f1d3fa9a380e654b86af429e0934a32f7d/idna-3.10.tar.gz", hash = "sha256:12f65c9b470abda6dc35cf8e63cc574b1c52b11df2c86030af0ac09b01b13ea9", size = 190490, upload-time = "2024-09-15T18:07:39.745Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/76/c6/c88e154df9c4e1a2a66ccf0005a88dfb2650c1dffb6f5ce603dfbd452ce3/idna-3.10-py3-none-any.whl", hash = "sha256:946d195a0d259cbba61165e88e65941f16e9b36ea6ddb97f00452bae8b1287d3", size = 70442, upload-time = "2024-09-15T18:07:37.964Z" },
]

[[package]]
name = "iniconfig"
version = "2.1.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/f2/97/ebf4da567aa6827c909642694d71c9fcf53e5b504f2d96afea02718862f3/iniconfig-2.1.0.tar.gz", hash = "sha256:3abbd2e30b36733fee78f9c7f7308f2d0050e88f0087fd25c2645f63c773e1c7", size = 4793, upload-time = "2025-03-19T20:09:59.721Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/2c/e1/e6716421ea10d38022b952c159d5161ca1193197fb744506875fbb87ea7b/iniconfig-2.1.0-py3-none-any.whl", hash = "sha256:9deba5723312380e77435581c6bf4935c94cbfab9b1ed33ef8d238ea168eb760", size = 6050, upload-time = "2025-03-19T20:10:01.071Z" },
]

[[package]]
name = "jinja2"
version = "3.1.6"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "markupsafe" },
]
sdist = { url = "https://files.pythonhosted.org/packages/df/bf/f7da0350254c0ed7c72f3e33cef02e048281fec7ecec5f032d4aac52226b/jinja2-3.1.6.tar.gz", hash = "sha256:0137fb05990d35f1275a587e9aee6d56da821fc83491a0fb838183be43f66d6d", size = 245115, upload-time = "2025-03-05T20:05:02.478Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/62/a1/3d680cbfd5f4b8f15abc1d571870c5fc3e594bb582bc3b64ea099db13e56/jinja2-3.1.6-py3-none-any.whl", hash = "sha256:85ece4451f492d0c13c5dd7c13a64681a86afae63a5f347908daf103ce6d2f67", size = 134899, upload-time = "2025-03-05T20:05:00.369Z" },
]

[[package]]
name = "loguru"
version = "0.7.3"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "colorama", marker = "sys_platform == 'win32'" },
    { name = "win32-setctime", marker = "sys_platform == 'win32'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/3a/05/a1dae3dffd1116099471c643b8924f5aa6524411dc6c63fdae648c4f1aca/loguru-0.7.3.tar.gz", hash = "sha256:19480589e77d47b8d85b2c827ad95d49bf31b0dcde16593892eb51dd18706eb6", size = 63559, upload-time = "2024-12-06T11:20:56.608Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/0c/29/0348de65b8cc732daa3e33e67806420b2ae89bdce2b04af740289c5c6c8c/loguru-0.7.3-py3-none-any.whl", hash = "sha256:31a33c10c8e1e10422bfd431aeb5d351c7cf7fa671e3c4df004162264b28220c", size = 61595, upload-time = "2024-12-06T11:20:54.538Z" },
]

[[package]]
name = "mako"
version = "1.3.10"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "markupsafe" },
]
sdist = { url = "https://files.pythonhosted.org/packages/9e/38/bd5b78a920a64d708fe6bc8e0a2c075e1389d53bef8413725c63ba041535/mako-1.3.10.tar.gz", hash = "sha256:99579a6f39583fa7e5630a28c3c1f440e4e97a414b80372649c0ce338da2ea28", size = 392474, upload-time = "2025-04-10T12:44:31.16Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/87/fb/99f81ac72ae23375f22b7afdb7642aba97c00a713c217124420147681a2f/mako-1.3.10-py3-none-any.whl", hash = "sha256:baef24a52fc4fc514a0887ac600f9f1cff3d82c61d4d700a1fa84d597b88db59", size = 78509, upload-time = "2025-04-10T12:50:53.297Z" },
]

[[package]]
name = "markupsafe"
version = "3.0.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/b2/97/5d42485e71dfc078108a86d6de8fa46db44a1a9295e89c5d6d4a06e23a62/markupsafe-3.0.2.tar.gz", hash = "sha256:ee55d3edf80167e48ea11a923c7386f4669df67d7994554387f84e7d8b0a2bf0", size = 20537, upload-time = "2024-10-18T15:21:54.129Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/83/0e/67eb10a7ecc77a0c2bbe2b0235765b98d164d81600746914bebada795e97/MarkupSafe-3.0.2-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:ba9527cdd4c926ed0760bc301f6728ef34d841f405abf9d4f959c478421e4efd", size = 14274, upload-time = "2024-10-18T15:21:24.577Z" },
    { url = "https://files.pythonhosted.org/packages/2b/6d/9409f3684d3335375d04e5f05744dfe7e9f120062c9857df4ab490a1031a/MarkupSafe-3.0.2-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:f8b3d067f2e40fe93e1ccdd6b2e1d16c43140e76f02fb1319a05cf2b79d99430", size = 12352, upload-time = "2024-10-18T15:21:25.382Z" },
    { url = "https://files.pythonhosted.org/packages/d2/f5/6eadfcd3885ea85fe2a7c128315cc1bb7241e1987443d78c8fe712d03091/MarkupSafe-3.0.2-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:569511d3b58c8791ab4c2e1285575265991e6d8f8700c7be0e88f86cb0672094", size = 24122, upload-time = "2024-10-18T15:21:26.199Z" },
    { url = "https://files.pythonhosted.org/packages/0c/91/96cf928db8236f1bfab6ce15ad070dfdd02ed88261c2afafd4b43575e9e9/MarkupSafe-3.0.2-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:15ab75ef81add55874e7ab7055e9c397312385bd9ced94920f2802310c930396", size = 23085, upload-time = "2024-10-18T15:21:27.029Z" },
    { url = "https://files.pythonhosted.org/packages/c2/cf/c9d56af24d56ea04daae7ac0940232d31d5a8354f2b457c6d856b2057d69/MarkupSafe-3.0.2-cp313-cp313-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl", hash = "sha256:f3818cb119498c0678015754eba762e0d61e5b52d34c8b13d770f0719f7b1d79", size = 22978, upload-time = "2024-10-18T15:21:27.846Z" },
    { url = "https://files.pythonhosted.org/packages/2a/9f/8619835cd6a711d6272d62abb78c033bda638fdc54c4e7f4272cf1c0962b/MarkupSafe-3.0.2-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:cdb82a876c47801bb54a690c5ae105a46b392ac6099881cdfb9f6e95e4014c6a", size = 24208, upload-time = "2024-10-18T15:21:28.744Z" },
    { url = "https://files.pythonhosted.org/packages/f9/bf/176950a1792b2cd2102b8ffeb5133e1ed984547b75db47c25a67d3359f77/MarkupSafe-3.0.2-cp313-cp313-musllinux_1_2_i686.whl", hash = "sha256:cabc348d87e913db6ab4aa100f01b08f481097838bdddf7c7a84b7575b7309ca", size = 23357, upload-time = "2024-10-18T15:21:29.545Z" },
    { url = "https://files.pythonhosted.org/packages/ce/4f/9a02c1d335caabe5c4efb90e1b6e8ee944aa245c1aaaab8e8a618987d816/MarkupSafe-3.0.2-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:444dcda765c8a838eaae23112db52f1efaf750daddb2d9ca300bcae1039adc5c", size = 23344, upload-time = "2024-10-18T15:21:30.366Z" },
    { url = "https://files.pythonhosted.org/packages/ee/55/c271b57db36f748f0e04a759ace9f8f759ccf22b4960c270c78a394f58be/MarkupSafe-3.0.2-cp313-cp313-win32.whl", hash = "sha256:bcf3e58998965654fdaff38e58584d8937aa3096ab5354d493c77d1fdd66d7a1", size = 15101, upload-time = "2024-10-18T15:21:31.207Z" },
    { url = "https://files.pythonhosted.org/packages/29/88/07df22d2dd4df40aba9f3e402e6dc1b8ee86297dddbad4872bd5e7b0094f/MarkupSafe-3.0.2-cp313-cp313-win_amd64.whl", hash = "sha256:e6a2a455bd412959b57a172ce6328d2dd1f01cb2135efda2e4576e8a23fa3b0f", size = 15603, upload-time = "2024-10-18T15:21:32.032Z" },
    { url = "https://files.pythonhosted.org/packages/62/6a/8b89d24db2d32d433dffcd6a8779159da109842434f1dd2f6e71f32f738c/MarkupSafe-3.0.2-cp313-cp313t-macosx_10_13_universal2.whl", hash = "sha256:b5a6b3ada725cea8a5e634536b1b01c30bcdcd7f9c6fff4151548d5bf6b3a36c", size = 14510, upload-time = "2024-10-18T15:21:33.625Z" },
    { url = "https://files.pythonhosted.org/packages/7a/06/a10f955f70a2e5a9bf78d11a161029d278eeacbd35ef806c3fd17b13060d/MarkupSafe-3.0.2-cp313-cp313t-macosx_11_0_arm64.whl", hash = "sha256:a904af0a6162c73e3edcb969eeeb53a63ceeb5d8cf642fade7d39e7963a22ddb", size = 12486, upload-time = "2024-10-18T15:21:34.611Z" },
    { url = "https://files.pythonhosted.org/packages/34/cf/65d4a571869a1a9078198ca28f39fba5fbb910f952f9dbc5220afff9f5e6/MarkupSafe-3.0.2-cp313-cp313t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:4aa4e5faecf353ed117801a068ebab7b7e09ffb6e1d5e412dc852e0da018126c", size = 25480, upload-time = "2024-10-18T15:21:35.398Z" },
    { url = "https://files.pythonhosted.org/packages/0c/e3/90e9651924c430b885468b56b3d597cabf6d72be4b24a0acd1fa0e12af67/MarkupSafe-3.0.2-cp313-cp313t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:c0ef13eaeee5b615fb07c9a7dadb38eac06a0608b41570d8ade51c56539e509d", size = 23914, upload-time = "2024-10-18T15:21:36.231Z" },
    { url = "https://files.pythonhosted.org/packages/66/8c/6c7cf61f95d63bb866db39085150df1f2a5bd3335298f14a66b48e92659c/MarkupSafe-3.0.2-cp313-cp313t-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl", hash = "sha256:d16a81a06776313e817c951135cf7340a3e91e8c1ff2fac444cfd75fffa04afe", size = 23796, upload-time = "2024-10-18T15:21:37.073Z" },
    { url = "https://files.pythonhosted.org/packages/bb/35/cbe9238ec3f47ac9a7c8b3df7a808e7cb50fe149dc7039f5f454b3fba218/MarkupSafe-3.0.2-cp313-cp313t-musllinux_1_2_aarch64.whl", hash = "sha256:6381026f158fdb7c72a168278597a5e3a5222e83ea18f543112b2662a9b699c5", size = 25473, upload-time = "2024-10-18T15:21:37.932Z" },
    { url = "https://files.pythonhosted.org/packages/e6/32/7621a4382488aa283cc05e8984a9c219abad3bca087be9ec77e89939ded9/MarkupSafe-3.0.2-cp313-cp313t-musllinux_1_2_i686.whl", hash = "sha256:3d79d162e7be8f996986c064d1c7c817f6df3a77fe3d6859f6f9e7be4b8c213a", size = 24114, upload-time = "2024-10-18T15:21:39.799Z" },
    { url = "https://files.pythonhosted.org/packages/0d/80/0985960e4b89922cb5a0bac0ed39c5b96cbc1a536a99f30e8c220a996ed9/MarkupSafe-3.0.2-cp313-cp313t-musllinux_1_2_x86_64.whl", hash = "sha256:131a3c7689c85f5ad20f9f6fb1b866f402c445b220c19fe4308c0b147ccd2ad9", size = 24098, upload-time = "2024-10-18T15:21:40.813Z" },
    { url = "https://files.pythonhosted.org/packages/82/78/fedb03c7d5380df2427038ec8d973587e90561b2d90cd472ce9254cf348b/MarkupSafe-3.0.2-cp313-cp313t-win32.whl", hash = "sha256:ba8062ed2cf21c07a9e295d5b8a2a5ce678b913b45fdf68c32d95d6c1291e0b6", size = 15208, upload-time = "2024-10-18T15:21:41.814Z" },
    { url = "https://files.pythonhosted.org/packages/4f/65/6079a46068dfceaeabb5dcad6d674f5f5c61a6fa5673746f42a9f4c233b3/MarkupSafe-3.0.2-cp313-cp313t-win_amd64.whl", hash = "sha256:e444a31f8db13eb18ada366ab3cf45fd4b31e4db1236a4448f68778c1d1a5a2f", size = 15739, upload-time = "2024-10-18T15:21:42.784Z" },
]

[[package]]
name = "metrologenerator"
version = "0.1.0"
source = { virtual = "." }
dependencies = [
    { name = "alembic" },
    { name = "asyncpg" },
    { name = "fastapi" },
    { name = "httpx" },
    { name = "jinja2" },
    { name = "loguru" },
    { name = "openpyxl" },
    { name = "playwright" },
    { name = "pydantic-settings" },
    { name = "python-dateutil" },
    { name = "python-multipart" },
    { name = "python-slugify" },
    { name = "ruff" },
    { name = "sqlalchemy" },
    { name = "uvicorn", extra = ["standard"] },
]

[package.optional-dependencies]
dev = [
    { name = "black" },
    { name = "pytest" },
    { name = "pytest-asyncio" },
    { name = "pytest-cov" },
    { name = "respx" },
    { name = "ruff" },
]

[package.metadata]
requires-dist = [
    { name = "alembic", specifier = ">=1.13" },
    { name = "asyncpg" },
    { name = "black", marker = "extra == 'dev'" },
    { name = "fastapi" },
    { name = "httpx" },
    { name = "jinja2" },
    { name = "loguru" },
    { name = "openpyxl" },
    { name = "playwright" },
    { name = "pydantic-settings" },
    { name = "pytest", marker = "extra == 'dev'" },
    { name = "pytest-asyncio", marker = "extra == 'dev'" },
    { name = "pytest-cov", marker = "extra == 'dev'" },
    { name = "python-dateutil" },
    { name = "python-multipart" },
    { name = "python-slugify" },
    { name = "respx", marker = "extra == 'dev'" },
    { name = "ruff", specifier = ">=0.12.12" },
    { name = "ruff", marker = "extra == 'dev'" },
    { name = "sqlalchemy", specifier = ">=2.0" },
    { name = "uvicorn", extras = ["standard"] },
]
provides-extras = ["dev"]

[[package]]
name = "mypy-extensions"
version = "1.1.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/a2/6e/371856a3fb9d31ca8dac321cda606860fa4548858c0cc45d9d1d4ca2628b/mypy_extensions-1.1.0.tar.gz", hash = "sha256:52e68efc3284861e772bbcd66823fde5ae21fd2fdb51c62a211403730b916558", size = 6343, upload-time = "2025-04-22T14:54:24.164Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/79/7b/2c79738432f5c924bef5071f933bcc9efd0473bac3b4aa584a6f7c1c8df8/mypy_extensions-1.1.0-py3-none-any.whl", hash = "sha256:1be4cccdb0f2482337c4743e60421de3a356cd97508abadd57d47403e94f5505", size = 4963, upload-time = "2025-04-22T14:54:22.983Z" },
]

[[package]]
name = "openpyxl"
version = "3.1.5"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "et-xmlfile" },
]
sdist = { url = "https://files.pythonhosted.org/packages/3d/f9/88d94a75de065ea32619465d2f77b29a0469500e99012523b91cc4141cd1/openpyxl-3.1.5.tar.gz", hash = "sha256:cf0e3cf56142039133628b5acffe8ef0c12bc902d2aadd3e0fe5878dc08d1050", size = 186464, upload-time = "2024-06-28T14:03:44.161Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/c0/da/977ded879c29cbd04de313843e76868e6e13408a94ed6b987245dc7c8506/openpyxl-3.1.5-py2.py3-none-any.whl", hash = "sha256:5282c12b107bffeef825f4617dc029afaf41d0ea60823bbb665ef3079dc79de2", size = 250910, upload-time = "2024-06-28T14:03:41.161Z" },
]

[[package]]
name = "packaging"
version = "25.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/a1/d4/1fc4078c65507b51b96ca8f8c3ba19e6a61c8253c72794544580a7b6c24d/packaging-25.0.tar.gz", hash = "sha256:d443872c98d677bf60f6a1f2f8c1cb748e8fe762d2bf9d3148b5599295b0fc4f", size = 165727, upload-time = "2025-04-19T11:48:59.673Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/20/12/38679034af332785aac8774540895e234f4d07f7545804097de4b666afd8/packaging-25.0-py3-none-any.whl", hash = "sha256:29572ef2b1f17581046b3a2227d5c611fb25ec70ca1ba8554b24b0e69331a484", size = 66469, upload-time = "2025-04-19T11:48:57.875Z" },
]

[[package]]
name = "pathspec"
version = "0.12.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/ca/bc/f35b8446f4531a7cb215605d100cd88b7ac6f44ab3fc94870c120ab3adbf/pathspec-0.12.1.tar.gz", hash = "sha256:a482d51503a1ab33b1c67a6c3813a26953dbdc71c31dacaef9a838c4e29f5712", size = 51043, upload-time = "2023-12-10T22:30:45Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/cc/20/ff623b09d963f88bfde16306a54e12ee5ea43e9b597108672ff3a408aad6/pathspec-0.12.1-py3-none-any.whl", hash = "sha256:a0d503e138a4c123b27490a4f7beda6a01c6f288df0e4a8b79c7eb0dc7b4cc08", size = 31191, upload-time = "2023-12-10T22:30:43.14Z" },
]

[[package]]
name = "platformdirs"
version = "4.4.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/23/e8/21db9c9987b0e728855bd57bff6984f67952bea55d6f75e055c46b5383e8/platformdirs-4.4.0.tar.gz", hash = "sha256:ca753cf4d81dc309bc67b0ea38fd15dc97bc30ce419a7f58d13eb3bf14c4febf", size = 21634, upload-time = "2025-08-26T14:32:04.268Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/40/4b/2028861e724d3bd36227adfa20d3fd24c3fc6d52032f4a93c133be5d17ce/platformdirs-4.4.0-py3-none-any.whl", hash = "sha256:abd01743f24e5287cd7a5db3752faf1a2d65353f38ec26d98e25a6db65958c85", size = 18654, upload-time = "2025-08-26T14:32:02.735Z" },
]

[[package]]
name = "playwright"
version = "1.55.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "greenlet" },
    { name = "pyee" },
]
wheels = [
    { url = "https://files.pythonhosted.org/packages/80/3a/c81ff76df266c62e24f19718df9c168f49af93cabdbc4608ae29656a9986/playwright-1.55.0-py3-none-macosx_10_13_x86_64.whl", hash = "sha256:d7da108a95001e412effca4f7610de79da1637ccdf670b1ae3fdc08b9694c034", size = 40428109, upload-time = "2025-08-28T15:46:20.357Z" },
    { url = "https://files.pythonhosted.org/packages/cf/f5/bdb61553b20e907196a38d864602a9b4a461660c3a111c67a35179b636fa/playwright-1.55.0-py3-none-macosx_11_0_arm64.whl", hash = "sha256:8290cf27a5d542e2682ac274da423941f879d07b001f6575a5a3a257b1d4ba1c", size = 38687254, upload-time = "2025-08-28T15:46:23.925Z" },
    { url = "https://files.pythonhosted.org/packages/4a/64/48b2837ef396487807e5ab53c76465747e34c7143fac4a084ef349c293a8/playwright-1.55.0-py3-none-macosx_11_0_universal2.whl", hash = "sha256:25b0d6b3fd991c315cca33c802cf617d52980108ab8431e3e1d37b5de755c10e", size = 40428108, upload-time = "2025-08-28T15:46:27.119Z" },
    { url = "https://files.pythonhosted.org/packages/08/33/858312628aa16a6de97839adc2ca28031ebc5391f96b6fb8fdf1fcb15d6c/playwright-1.55.0-py3-none-manylinux1_x86_64.whl", hash = "sha256:c6d4d8f6f8c66c483b0835569c7f0caa03230820af8e500c181c93509c92d831", size = 45905643, upload-time = "2025-08-28T15:46:30.312Z" },
    { url = "https://files.pythonhosted.org/packages/83/83/b8d06a5b5721931aa6d5916b83168e28bd891f38ff56fe92af7bdee9860f/playwright-1.55.0-py3-none-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:29a0777c4ce1273acf90c87e4ae2fe0130182100d99bcd2ae5bf486093044838", size = 45296647, upload-time = "2025-08-28T15:46:33.221Z" },
    { url = "https://files.pythonhosted.org/packages/06/2e/9db64518aebcb3d6ef6cd6d4d01da741aff912c3f0314dadb61226c6a96a/playwright-1.55.0-py3-none-win32.whl", hash = "sha256:29e6d1558ad9d5b5c19cbec0a72f6a2e35e6353cd9f262e22148685b86759f90", size = 35476046, upload-time = "2025-08-28T15:46:36.184Z" },
    { url = "https://files.pythonhosted.org/packages/46/4f/9ba607fa94bb9cee3d4beb1c7b32c16efbfc9d69d5037fa85d10cafc618b/playwright-1.55.0-py3-none-win_amd64.whl", hash = "sha256:7eb5956473ca1951abb51537e6a0da55257bb2e25fc37c2b75af094a5c93736c", size = 35476048, upload-time = "2025-08-28T15:46:38.867Z" },
    { url = "https://files.pythonhosted.org/packages/21/98/5ca173c8ec906abde26c28e1ecb34887343fd71cc4136261b90036841323/playwright-1.55.0-py3-none-win_arm64.whl", hash = "sha256:012dc89ccdcbd774cdde8aeee14c08e0dd52ddb9135bf10e9db040527386bd76", size = 31225543, upload-time = "2025-08-28T15:46:41.613Z" },
]

[[package]]
name = "pluggy"
version = "1.6.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/f9/e2/3e91f31a7d2b083fe6ef3fa267035b518369d9511ffab804f839851d2779/pluggy-1.6.0.tar.gz", hash = "sha256:7dcc130b76258d33b90f61b658791dede3486c3e6bfb003ee5c9bfb396dd22f3", size = 69412, upload-time = "2025-05-15T12:30:07.975Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/54/20/4d324d65cc6d9205fabedc306948156824eb9f0ee1633355a8f7ec5c66bf/pluggy-1.6.0-py3-none-any.whl", hash = "sha256:e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746", size = 20538, upload-time = "2025-05-15T12:30:06.134Z" },
]

[[package]]
name = "pydantic"
version = "2.11.7"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "annotated-types" },
    { name = "pydantic-core" },
    { name = "typing-extensions" },
    { name = "typing-inspection" },
]
sdist = { url = "https://files.pythonhosted.org/packages/00/dd/4325abf92c39ba8623b5af936ddb36ffcfe0beae70405d456ab1fb2f5b8c/pydantic-2.11.7.tar.gz", hash = "sha256:d989c3c6cb79469287b1569f7447a17848c998458d49ebe294e975b9baf0f0db", size = 788350, upload-time = "2025-06-14T08:33:17.137Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/6a/c0/ec2b1c8712ca690e5d61979dee872603e92b8a32f94cc1b72d53beab008a/pydantic-2.11.7-py3-none-any.whl", hash = "sha256:dde5df002701f6de26248661f6835bbe296a47bf73990135c7d07ce741b9623b", size = 444782, upload-time = "2025-06-14T08:33:14.905Z" },
]

[[package]]
name = "pydantic-core"
version = "2.33.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/ad/88/5f2260bdfae97aabf98f1778d43f69574390ad787afb646292a638c923d4/pydantic_core-2.33.2.tar.gz", hash = "sha256:7cb8bc3605c29176e1b105350d2e6474142d7c1bd1d9327c4a9bdb46bf827acc", size = 435195, upload-time = "2025-04-23T18:33:52.104Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/46/8c/99040727b41f56616573a28771b1bfa08a3d3fe74d3d513f01251f79f172/pydantic_core-2.33.2-cp313-cp313-macosx_10_12_x86_64.whl", hash = "sha256:1082dd3e2d7109ad8b7da48e1d4710c8d06c253cbc4a27c1cff4fbcaa97a9e3f", size = 2015688, upload-time = "2025-04-23T18:31:53.175Z" },
    { url = "https://files.pythonhosted.org/packages/3a/cc/5999d1eb705a6cefc31f0b4a90e9f7fc400539b1a1030529700cc1b51838/pydantic_core-2.33.2-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:f517ca031dfc037a9c07e748cefd8d96235088b83b4f4ba8939105d20fa1dcd6", size = 1844808, upload-time = "2025-04-23T18:31:54.79Z" },
    { url = "https://files.pythonhosted.org/packages/6f/5e/a0a7b8885c98889a18b6e376f344da1ef323d270b44edf8174d6bce4d622/pydantic_core-2.33.2-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:0a9f2c9dd19656823cb8250b0724ee9c60a82f3cdf68a080979d13092a3b0fef", size = 1885580, upload-time = "2025-04-23T18:31:57.393Z" },
    { url = "https://files.pythonhosted.org/packages/3b/2a/953581f343c7d11a304581156618c3f592435523dd9d79865903272c256a/pydantic_core-2.33.2-cp313-cp313-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:2b0a451c263b01acebe51895bfb0e1cc842a5c666efe06cdf13846c7418caa9a", size = 1973859, upload-time = "2025-04-23T18:31:59.065Z" },
    { url = "https://files.pythonhosted.org/packages/e6/55/f1a813904771c03a3f97f676c62cca0c0a4138654107c1b61f19c644868b/pydantic_core-2.33.2-cp313-cp313-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:1ea40a64d23faa25e62a70ad163571c0b342b8bf66d5fa612ac0dec4f069d916", size = 2120810, upload-time = "2025-04-23T18:32:00.78Z" },
    { url = "https://files.pythonhosted.org/packages/aa/c3/053389835a996e18853ba107a63caae0b9deb4a276c6b472931ea9ae6e48/pydantic_core-2.33.2-cp313-cp313-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:0fb2d542b4d66f9470e8065c5469ec676978d625a8b7a363f07d9a501a9cb36a", size = 2676498, upload-time = "2025-04-23T18:32:02.418Z" },
    { url = "https://files.pythonhosted.org/packages/eb/3c/f4abd740877a35abade05e437245b192f9d0ffb48bbbbd708df33d3cda37/pydantic_core-2.33.2-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:9fdac5d6ffa1b5a83bca06ffe7583f5576555e6c8b3a91fbd25ea7780f825f7d", size = 2000611, upload-time = "2025-04-23T18:32:04.152Z" },
    { url = "https://files.pythonhosted.org/packages/59/a7/63ef2fed1837d1121a894d0ce88439fe3e3b3e48c7543b2a4479eb99c2bd/pydantic_core-2.33.2-cp313-cp313-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:04a1a413977ab517154eebb2d326da71638271477d6ad87a769102f7c2488c56", size = 2107924, upload-time = "2025-04-23T18:32:06.129Z" },
    { url = "https://files.pythonhosted.org/packages/04/8f/2551964ef045669801675f1cfc3b0d74147f4901c3ffa42be2ddb1f0efc4/pydantic_core-2.33.2-cp313-cp313-musllinux_1_1_aarch64.whl", hash = "sha256:c8e7af2f4e0194c22b5b37205bfb293d166a7344a5b0d0eaccebc376546d77d5", size = 2063196, upload-time = "2025-04-23T18:32:08.178Z" },
    { url = "https://files.pythonhosted.org/packages/26/bd/d9602777e77fc6dbb0c7db9ad356e9a985825547dce5ad1d30ee04903918/pydantic_core-2.33.2-cp313-cp313-musllinux_1_1_armv7l.whl", hash = "sha256:5c92edd15cd58b3c2d34873597a1e20f13094f59cf88068adb18947df5455b4e", size = 2236389, upload-time = "2025-04-23T18:32:10.242Z" },
    { url = "https://files.pythonhosted.org/packages/42/db/0e950daa7e2230423ab342ae918a794964b053bec24ba8af013fc7c94846/pydantic_core-2.33.2-cp313-cp313-musllinux_1_1_x86_64.whl", hash = "sha256:65132b7b4a1c0beded5e057324b7e16e10910c106d43675d9bd87d4f38dde162", size = 2239223, upload-time = "2025-04-23T18:32:12.382Z" },
    { url = "https://files.pythonhosted.org/packages/58/4d/4f937099c545a8a17eb52cb67fe0447fd9a373b348ccfa9a87f141eeb00f/pydantic_core-2.33.2-cp313-cp313-win32.whl", hash = "sha256:52fb90784e0a242bb96ec53f42196a17278855b0f31ac7c3cc6f5c1ec4811849", size = 1900473, upload-time = "2025-04-23T18:32:14.034Z" },
    { url = "https://files.pythonhosted.org/packages/a0/75/4a0a9bac998d78d889def5e4ef2b065acba8cae8c93696906c3a91f310ca/pydantic_core-2.33.2-cp313-cp313-win_amd64.whl", hash = "sha256:c083a3bdd5a93dfe480f1125926afcdbf2917ae714bdb80b36d34318b2bec5d9", size = 1955269, upload-time = "2025-04-23T18:32:15.783Z" },
    { url = "https://files.pythonhosted.org/packages/f9/86/1beda0576969592f1497b4ce8e7bc8cbdf614c352426271b1b10d5f0aa64/pydantic_core-2.33.2-cp313-cp313-win_arm64.whl", hash = "sha256:e80b087132752f6b3d714f041ccf74403799d3b23a72722ea2e6ba2e892555b9", size = 1893921, upload-time = "2025-04-23T18:32:18.473Z" },
    { url = "https://files.pythonhosted.org/packages/a4/7d/e09391c2eebeab681df2b74bfe6c43422fffede8dc74187b2b0bf6fd7571/pydantic_core-2.33.2-cp313-cp313t-macosx_11_0_arm64.whl", hash = "sha256:61c18fba8e5e9db3ab908620af374db0ac1baa69f0f32df4f61ae23f15e586ac", size = 1806162, upload-time = "2025-04-23T18:32:20.188Z" },
    { url = "https://files.pythonhosted.org/packages/f1/3d/847b6b1fed9f8ed3bb95a9ad04fbd0b212e832d4f0f50ff4d9ee5a9f15cf/pydantic_core-2.33.2-cp313-cp313t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:95237e53bb015f67b63c91af7518a62a8660376a6a0db19b89acc77a4d6199f5", size = 1981560, upload-time = "2025-04-23T18:32:22.354Z" },
    { url = "https://files.pythonhosted.org/packages/6f/9a/e73262f6c6656262b5fdd723ad90f518f579b7bc8622e43a942eec53c938/pydantic_core-2.33.2-cp313-cp313t-win_amd64.whl", hash = "sha256:c2fc0a768ef76c15ab9238afa6da7f69895bb5d1ee83aeea2e3509af4472d0b9", size = 1935777, upload-time = "2025-04-23T18:32:25.088Z" },
]

[[package]]
name = "pydantic-settings"
version = "2.10.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pydantic" },
    { name = "python-dotenv" },
    { name = "typing-inspection" },
]
sdist = { url = "https://files.pythonhosted.org/packages/68/85/1ea668bbab3c50071ca613c6ab30047fb36ab0da1b92fa8f17bbc38fd36c/pydantic_settings-2.10.1.tar.gz", hash = "sha256:06f0062169818d0f5524420a360d632d5857b83cffd4d42fe29597807a1614ee", size = 172583, upload-time = "2025-06-24T13:26:46.841Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/58/f0/427018098906416f580e3cf1366d3b1abfb408a0652e9f31600c24a1903c/pydantic_settings-2.10.1-py3-none-any.whl", hash = "sha256:a60952460b99cf661dc25c29c0ef171721f98bfcb52ef8d9ea4c943d7c8cc796", size = 45235, upload-time = "2025-06-24T13:26:45.485Z" },
]

[[package]]
name = "pyee"
version = "13.0.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/95/03/1fd98d5841cd7964a27d729ccf2199602fe05eb7a405c1462eb7277945ed/pyee-13.0.0.tar.gz", hash = "sha256:b391e3c5a434d1f5118a25615001dbc8f669cf410ab67d04c4d4e07c55481c37", size = 31250, upload-time = "2025-03-17T18:53:15.955Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/9b/4d/b9add7c84060d4c1906abe9a7e5359f2a60f7a9a4f67268b2766673427d8/pyee-13.0.0-py3-none-any.whl", hash = "sha256:48195a3cddb3b1515ce0695ed76036b5ccc2ef3a9f963ff9f77aec0139845498", size = 15730, upload-time = "2025-03-17T18:53:14.532Z" },
]

[[package]]
name = "pygments"
version = "2.19.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/b0/77/a5b8c569bf593b0140bde72ea885a803b82086995367bf2037de0159d924/pygments-2.19.2.tar.gz", hash = "sha256:636cb2477cec7f8952536970bc533bc43743542f70392ae026374600add5b887", size = 4968631, upload-time = "2025-06-21T13:39:12.283Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/c7/21/705964c7812476f378728bdf590ca4b771ec72385c533964653c68e86bdc/pygments-2.19.2-py3-none-any.whl", hash = "sha256:86540386c03d588bb81d44bc3928634ff26449851e99741617ecb9037ee5ec0b", size = 1225217, upload-time = "2025-06-21T13:39:07.939Z" },
]

[[package]]
name = "pytest"
version = "8.4.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "colorama", marker = "sys_platform == 'win32'" },
    { name = "iniconfig" },
    { name = "packaging" },
    { name = "pluggy" },
    { name = "pygments" },
]
sdist = { url = "https://files.pythonhosted.org/packages/08/ba/45911d754e8eba3d5a841a5ce61a65a685ff1798421ac054f85aa8747dfb/pytest-8.4.1.tar.gz", hash = "sha256:7c67fd69174877359ed9371ec3af8a3d2b04741818c51e5e99cc1742251fa93c", size = 1517714, upload-time = "2025-06-18T05:48:06.109Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/29/16/c8a903f4c4dffe7a12843191437d7cd8e32751d5de349d45d3fe69544e87/pytest-8.4.1-py3-none-any.whl", hash = "sha256:539c70ba6fcead8e78eebbf1115e8b589e7565830d7d006a8723f19ac8a0afb7", size = 365474, upload-time = "2025-06-18T05:48:03.955Z" },
]

[[package]]
name = "pytest-asyncio"
version = "1.1.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pytest" },
]
sdist = { url = "https://files.pythonhosted.org/packages/4e/51/f8794af39eeb870e87a8c8068642fc07bce0c854d6865d7dd0f2a9d338c2/pytest_asyncio-1.1.0.tar.gz", hash = "sha256:796aa822981e01b68c12e4827b8697108f7205020f24b5793b3c41555dab68ea", size = 46652, upload-time = "2025-07-16T04:29:26.393Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/c7/9d/bf86eddabf8c6c9cb1ea9a869d6873b46f105a5d292d3a6f7071f5b07935/pytest_asyncio-1.1.0-py3-none-any.whl", hash = "sha256:5fe2d69607b0bd75c656d1211f969cadba035030156745ee09e7d71740e58ecf", size = 15157, upload-time = "2025-07-16T04:29:24.929Z" },
]

[[package]]
name = "pytest-cov"
version = "6.2.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "coverage" },
    { name = "pluggy" },
    { name = "pytest" },
]
sdist = { url = "https://files.pythonhosted.org/packages/18/99/668cade231f434aaa59bbfbf49469068d2ddd945000621d3d165d2e7dd7b/pytest_cov-6.2.1.tar.gz", hash = "sha256:25cc6cc0a5358204b8108ecedc51a9b57b34cc6b8c967cc2c01a4e00d8a67da2", size = 69432, upload-time = "2025-06-12T10:47:47.684Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/bc/16/4ea354101abb1287856baa4af2732be351c7bee728065aed451b678153fd/pytest_cov-6.2.1-py3-none-any.whl", hash = "sha256:f5bc4c23f42f1cdd23c70b1dab1bbaef4fc505ba950d53e0081d0730dd7e86d5", size = 24644, upload-time = "2025-06-12T10:47:45.932Z" },
]

[[package]]
name = "python-dateutil"
version = "2.9.0.post0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "six" },
]
sdist = { url = "https://files.pythonhosted.org/packages/66/c0/0c8b6ad9f17a802ee498c46e004a0eb49bc148f2fd230864601a86dcf6db/python-dateutil-2.9.0.post0.tar.gz", hash = "sha256:37dd54208da7e1cd875388217d5e00ebd4179249f90fb72437e91a35459a0ad3", size = 342432, upload-time = "2024-03-01T18:36:20.211Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/ec/57/56b9bcc3c9c6a792fcbaf139543cee77261f3651ca9da0c93f5c1221264b/python_dateutil-2.9.0.post0-py2.py3-none-any.whl", hash = "sha256:a8b2bc7bffae282281c8140a97d3aa9c14da0b136dfe83f850eea9a5f7470427", size = 229892, upload-time = "2024-03-01T18:36:18.57Z" },
]

[[package]]
name = "python-dotenv"
version = "1.1.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/f6/b0/4bc07ccd3572a2f9df7e6782f52b0c6c90dcbb803ac4a167702d7d0dfe1e/python_dotenv-1.1.1.tar.gz", hash = "sha256:a8a6399716257f45be6a007360200409fce5cda2661e3dec71d23dc15f6189ab", size = 41978, upload-time = "2025-06-24T04:21:07.341Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/5f/ed/539768cf28c661b5b068d66d96a2f155c4971a5d55684a514c1a0e0dec2f/python_dotenv-1.1.1-py3-none-any.whl", hash = "sha256:31f23644fe2602f88ff55e1f5c79ba497e01224ee7737937930c448e4d0e24dc", size = 20556, upload-time = "2025-06-24T04:21:06.073Z" },
]

[[package]]
name = "python-multipart"
version = "0.0.20"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/f3/87/f44d7c9f274c7ee665a29b885ec97089ec5dc034c7f3fafa03da9e39a09e/python_multipart-0.0.20.tar.gz", hash = "sha256:8dd0cab45b8e23064ae09147625994d090fa46f5b0d1e13af944c331a7fa9d13", size = 37158, upload-time = "2024-12-16T19:45:46.972Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/45/58/38b5afbc1a800eeea951b9285d3912613f2603bdf897a4ab0f4bd7f405fc/python_multipart-0.0.20-py3-none-any.whl", hash = "sha256:8a62d3a8335e06589fe01f2a3e178cdcc632f3fbe0d492ad9ee0ec35aab1f104", size = 24546, upload-time = "2024-12-16T19:45:44.423Z" },
]

[[package]]
name = "python-slugify"
version = "8.0.4"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "text-unidecode" },
]
sdist = { url = "https://files.pythonhosted.org/packages/87/c7/5e1547c44e31da50a460df93af11a535ace568ef89d7a811069ead340c4a/python-slugify-8.0.4.tar.gz", hash = "sha256:59202371d1d05b54a9e7720c5e038f928f45daaffe41dd10822f3907b937c856", size = 10921, upload-time = "2024-02-08T18:32:45.488Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/a4/62/02da182e544a51a5c3ccf4b03ab79df279f9c60c5e82d5e8bec7ca26ac11/python_slugify-8.0.4-py2.py3-none-any.whl", hash = "sha256:276540b79961052b66b7d116620b36518847f52d5fd9e3a70164fc8c50faa6b8", size = 10051, upload-time = "2024-02-08T18:32:43.911Z" },
]

[[package]]
name = "pyyaml"
version = "6.0.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/54/ed/79a089b6be93607fa5cdaedf301d7dfb23af5f25c398d5ead2525b063e17/pyyaml-6.0.2.tar.gz", hash = "sha256:d584d9ec91ad65861cc08d42e834324ef890a082e591037abe114850ff7bbc3e", size = 130631, upload-time = "2024-08-06T20:33:50.674Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/ef/e3/3af305b830494fa85d95f6d95ef7fa73f2ee1cc8ef5b495c7c3269fb835f/PyYAML-6.0.2-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:efdca5630322a10774e8e98e1af481aad470dd62c3170801852d752aa7a783ba", size = 181309, upload-time = "2024-08-06T20:32:43.4Z" },
    { url = "https://files.pythonhosted.org/packages/45/9f/3b1c20a0b7a3200524eb0076cc027a970d320bd3a6592873c85c92a08731/PyYAML-6.0.2-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:50187695423ffe49e2deacb8cd10510bc361faac997de9efef88badc3bb9e2d1", size = 171679, upload-time = "2024-08-06T20:32:44.801Z" },
    { url = "https://files.pythonhosted.org/packages/7c/9a/337322f27005c33bcb656c655fa78325b730324c78620e8328ae28b64d0c/PyYAML-6.0.2-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:0ffe8360bab4910ef1b9e87fb812d8bc0a308b0d0eef8c8f44e0254ab3b07133", size = 733428, upload-time = "2024-08-06T20:32:46.432Z" },
    { url = "https://files.pythonhosted.org/packages/a3/69/864fbe19e6c18ea3cc196cbe5d392175b4cf3d5d0ac1403ec3f2d237ebb5/PyYAML-6.0.2-cp313-cp313-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:17e311b6c678207928d649faa7cb0d7b4c26a0ba73d41e99c4fff6b6c3276484", size = 763361, upload-time = "2024-08-06T20:32:51.188Z" },
    { url = "https://files.pythonhosted.org/packages/04/24/b7721e4845c2f162d26f50521b825fb061bc0a5afcf9a386840f23ea19fa/PyYAML-6.0.2-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:70b189594dbe54f75ab3a1acec5f1e3faa7e8cf2f1e08d9b561cb41b845f69d5", size = 759523, upload-time = "2024-08-06T20:32:53.019Z" },
    { url = "https://files.pythonhosted.org/packages/2b/b2/e3234f59ba06559c6ff63c4e10baea10e5e7df868092bf9ab40e5b9c56b6/PyYAML-6.0.2-cp313-cp313-musllinux_1_1_aarch64.whl", hash = "sha256:41e4e3953a79407c794916fa277a82531dd93aad34e29c2a514c2c0c5fe971cc", size = 726660, upload-time = "2024-08-06T20:32:54.708Z" },
    { url = "https://files.pythonhosted.org/packages/fe/0f/25911a9f080464c59fab9027482f822b86bf0608957a5fcc6eaac85aa515/PyYAML-6.0.2-cp313-cp313-musllinux_1_1_x86_64.whl", hash = "sha256:68ccc6023a3400877818152ad9a1033e3db8625d899c72eacb5a668902e4d652", size = 751597, upload-time = "2024-08-06T20:32:56.985Z" },
    { url = "https://files.pythonhosted.org/packages/14/0d/e2c3b43bbce3cf6bd97c840b46088a3031085179e596d4929729d8d68270/PyYAML-6.0.2-cp313-cp313-win32.whl", hash = "sha256:bc2fa7c6b47d6bc618dd7fb02ef6fdedb1090ec036abab80d4681424b84c1183", size = 140527, upload-time = "2024-08-06T20:33:03.001Z" },
    { url = "https://files.pythonhosted.org/packages/fa/de/02b54f42487e3d3c6efb3f89428677074ca7bf43aae402517bc7cca949f3/PyYAML-6.0.2-cp313-cp313-win_amd64.whl", hash = "sha256:8388ee1976c416731879ac16da0aff3f63b286ffdd57cdeb95f3f2e085687563", size = 156446, upload-time = "2024-08-06T20:33:04.33Z" },
]

[[package]]
name = "respx"
version = "0.22.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "httpx" },
]
sdist = { url = "https://files.pythonhosted.org/packages/f4/7c/96bd0bc759cf009675ad1ee1f96535edcb11e9666b985717eb8c87192a95/respx-0.22.0.tar.gz", hash = "sha256:3c8924caa2a50bd71aefc07aa812f2466ff489f1848c96e954a5362d17095d91", size = 28439, upload-time = "2024-12-19T22:33:59.374Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/8e/67/afbb0978d5399bc9ea200f1d4489a23c9a1dad4eee6376242b8182389c79/respx-0.22.0-py2.py3-none-any.whl", hash = "sha256:631128d4c9aba15e56903fb5f66fb1eff412ce28dd387ca3a81339e52dbd3ad0", size = 25127, upload-time = "2024-12-19T22:33:57.837Z" },
]

[[package]]
name = "ruff"
version = "0.12.12"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/a8/f0/e0965dd709b8cabe6356811c0ee8c096806bb57d20b5019eb4e48a117410/ruff-0.12.12.tar.gz", hash = "sha256:b86cd3415dbe31b3b46a71c598f4c4b2f550346d1ccf6326b347cc0c8fd063d6", size = 5359915, upload-time = "2025-09-04T16:50:18.273Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/09/79/8d3d687224d88367b51c7974cec1040c4b015772bfbeffac95face14c04a/ruff-0.12.12-py3-none-linux_armv6l.whl", hash = "sha256:de1c4b916d98ab289818e55ce481e2cacfaad7710b01d1f990c497edf217dafc", size = 12116602, upload-time = "2025-09-04T16:49:18.892Z" },
    { url = "https://files.pythonhosted.org/packages/c3/c3/6e599657fe192462f94861a09aae935b869aea8a1da07f47d6eae471397c/ruff-0.12.12-py3-none-macosx_10_12_x86_64.whl", hash = "sha256:7acd6045e87fac75a0b0cdedacf9ab3e1ad9d929d149785903cff9bb69ad9727", size = 12868393, upload-time = "2025-09-04T16:49:23.043Z" },
    { url = "https://files.pythonhosted.org/packages/e8/d2/9e3e40d399abc95336b1843f52fc0daaceb672d0e3c9290a28ff1a96f79d/ruff-0.12.12-py3-none-macosx_11_0_arm64.whl", hash = "sha256:abf4073688d7d6da16611f2f126be86523a8ec4343d15d276c614bda8ec44edb", size = 12036967, upload-time = "2025-09-04T16:49:26.04Z" },
    { url = "https://files.pythonhosted.org/packages/e9/03/6816b2ed08836be272e87107d905f0908be5b4a40c14bfc91043e76631b8/ruff-0.12.12-py3-none-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:968e77094b1d7a576992ac078557d1439df678a34c6fe02fd979f973af167577", size = 12276038, upload-time = "2025-09-04T16:49:29.056Z" },
    { url = "https://files.pythonhosted.org/packages/9f/d5/707b92a61310edf358a389477eabd8af68f375c0ef858194be97ca5b6069/ruff-0.12.12-py3-none-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:42a67d16e5b1ffc6d21c5f67851e0e769517fb57a8ebad1d0781b30888aa704e", size = 11901110, upload-time = "2025-09-04T16:49:32.07Z" },
    { url = "https://files.pythonhosted.org/packages/9d/3d/f8b1038f4b9822e26ec3d5b49cf2bc313e3c1564cceb4c1a42820bf74853/ruff-0.12.12-py3-none-manylinux_2_17_i686.manylinux2014_i686.whl", hash = "sha256:b216ec0a0674e4b1214dcc998a5088e54eaf39417327b19ffefba1c4a1e4971e", size = 13668352, upload-time = "2025-09-04T16:49:35.148Z" },
    { url = "https://files.pythonhosted.org/packages/98/0e/91421368ae6c4f3765dd41a150f760c5f725516028a6be30e58255e3c668/ruff-0.12.12-py3-none-manylinux_2_17_ppc64.manylinux2014_ppc64.whl", hash = "sha256:59f909c0fdd8f1dcdbfed0b9569b8bf428cf144bec87d9de298dcd4723f5bee8", size = 14638365, upload-time = "2025-09-04T16:49:38.892Z" },
    { url = "https://files.pythonhosted.org/packages/74/5d/88f3f06a142f58ecc8ecb0c2fe0b82343e2a2b04dcd098809f717cf74b6c/ruff-0.12.12-py3-none-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:9ac93d87047e765336f0c18eacad51dad0c1c33c9df7484c40f98e1d773876f5", size = 14060812, upload-time = "2025-09-04T16:49:42.732Z" },
    { url = "https://files.pythonhosted.org/packages/13/fc/8962e7ddd2e81863d5c92400820f650b86f97ff919c59836fbc4c1a6d84c/ruff-0.12.12-py3-none-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:01543c137fd3650d322922e8b14cc133b8ea734617c4891c5a9fccf4bfc9aa92", size = 13050208, upload-time = "2025-09-04T16:49:46.434Z" },
    { url = "https://files.pythonhosted.org/packages/53/06/8deb52d48a9a624fd37390555d9589e719eac568c020b27e96eed671f25f/ruff-0.12.12-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:2afc2fa864197634e549d87fb1e7b6feb01df0a80fd510d6489e1ce8c0b1cc45", size = 13311444, upload-time = "2025-09-04T16:49:49.931Z" },
    { url = "https://files.pythonhosted.org/packages/2a/81/de5a29af7eb8f341f8140867ffb93f82e4fde7256dadee79016ac87c2716/ruff-0.12.12-py3-none-manylinux_2_31_riscv64.whl", hash = "sha256:0c0945246f5ad776cb8925e36af2438e66188d2b57d9cf2eed2c382c58b371e5", size = 13279474, upload-time = "2025-09-04T16:49:53.465Z" },
    { url = "https://files.pythonhosted.org/packages/7f/14/d9577fdeaf791737ada1b4f5c6b59c21c3326f3f683229096cccd7674e0c/ruff-0.12.12-py3-none-musllinux_1_2_aarch64.whl", hash = "sha256:a0fbafe8c58e37aae28b84a80ba1817f2ea552e9450156018a478bf1fa80f4e4", size = 12070204, upload-time = "2025-09-04T16:49:56.882Z" },
    { url = "https://files.pythonhosted.org/packages/77/04/a910078284b47fad54506dc0af13839c418ff704e341c176f64e1127e461/ruff-0.12.12-py3-none-musllinux_1_2_armv7l.whl", hash = "sha256:b9c456fb2fc8e1282affa932c9e40f5ec31ec9cbb66751a316bd131273b57c23", size = 11880347, upload-time = "2025-09-04T16:49:59.729Z" },
    { url = "https://files.pythonhosted.org/packages/df/58/30185fcb0e89f05e7ea82e5817b47798f7fa7179863f9d9ba6fd4fe1b098/ruff-0.12.12-py3-none-musllinux_1_2_i686.whl", hash = "sha256:5f12856123b0ad0147d90b3961f5c90e7427f9acd4b40050705499c98983f489", size = 12891844, upload-time = "2025-09-04T16:50:02.591Z" },
    { url = "https://files.pythonhosted.org/packages/21/9c/28a8dacce4855e6703dcb8cdf6c1705d0b23dd01d60150786cd55aa93b16/ruff-0.12.12-py3-none-musllinux_1_2_x86_64.whl", hash = "sha256:26a1b5a2bf7dd2c47e3b46d077cd9c0fc3b93e6c6cc9ed750bd312ae9dc302ee", size = 13360687, upload-time = "2025-09-04T16:50:05.8Z" },
    { url = "https://files.pythonhosted.org/packages/c8/fa/05b6428a008e60f79546c943e54068316f32ec8ab5c4f73e4563934fbdc7/ruff-0.12.12-py3-none-win32.whl", hash = "sha256:173be2bfc142af07a01e3a759aba6f7791aa47acf3604f610b1c36db888df7b1", size = 12052870, upload-time = "2025-09-04T16:50:09.121Z" },
    { url = "https://files.pythonhosted.org/packages/85/60/d1e335417804df452589271818749d061b22772b87efda88354cf35cdb7a/ruff-0.12.12-py3-none-win_amd64.whl", hash = "sha256:e99620bf01884e5f38611934c09dd194eb665b0109104acae3ba6102b600fd0d", size = 13178016, upload-time = "2025-09-04T16:50:12.559Z" },
    { url = "https://files.pythonhosted.org/packages/28/7e/61c42657f6e4614a4258f1c3b0c5b93adc4d1f8575f5229d1906b483099b/ruff-0.12.12-py3-none-win_arm64.whl", hash = "sha256:2a8199cab4ce4d72d158319b63370abf60991495fb733db96cd923a34c52d093", size = 12256762, upload-time = "2025-09-04T16:50:15.737Z" },
]

[[package]]
name = "six"
version = "1.17.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/94/e7/b2c673351809dca68a0e064b6af791aa332cf192da575fd474ed7d6f16a2/six-1.17.0.tar.gz", hash = "sha256:ff70335d468e7eb6ec65b95b99d3a2836546063f63acc5171de367e834932a81", size = 34031, upload-time = "2024-12-04T17:35:28.174Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/b7/ce/149a00dd41f10bc29e5921b496af8b574d8413afcd5e30dfa0ed46c2cc5e/six-1.17.0-py2.py3-none-any.whl", hash = "sha256:4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274", size = 11050, upload-time = "2024-12-04T17:35:26.475Z" },
]

[[package]]
name = "sniffio"
version = "1.3.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/a2/87/a6771e1546d97e7e041b6ae58d80074f81b7d5121207425c964ddf5cfdbd/sniffio-1.3.1.tar.gz", hash = "sha256:f4324edc670a0f49750a81b895f35c3adb843cca46f0530f79fc1babb23789dc", size = 20372, upload-time = "2024-02-25T23:20:04.057Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/e9/44/75a9c9421471a6c4805dbf2356f7c181a29c1879239abab1ea2cc8f38b40/sniffio-1.3.1-py3-none-any.whl", hash = "sha256:2f6da418d1f1e0fddd844478f41680e794e6051915791a034ff65e5f100525a2", size = 10235, upload-time = "2024-02-25T23:20:01.196Z" },
]

[[package]]
name = "sqlalchemy"
version = "2.0.43"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "greenlet", marker = "(python_full_version < '3.14' and platform_machine == 'AMD64') or (python_full_version < '3.14' and platform_machine == 'WIN32') or (python_full_version < '3.14' and platform_machine == 'aarch64') or (python_full_version < '3.14' and platform_machine == 'amd64') or (python_full_version < '3.14' and platform_machine == 'ppc64le') or (python_full_version < '3.14' and platform_machine == 'win32') or (python_full_version < '3.14' and platform_machine == 'x86_64')" },
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/d7/bc/d59b5d97d27229b0e009bd9098cd81af71c2fa5549c580a0a67b9bed0496/sqlalchemy-2.0.43.tar.gz", hash = "sha256:788bfcef6787a7764169cfe9859fe425bf44559619e1d9f56f5bddf2ebf6f417", size = 9762949, upload-time = "2025-08-11T14:24:58.438Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/41/1c/a7260bd47a6fae7e03768bf66451437b36451143f36b285522b865987ced/sqlalchemy-2.0.43-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:e7c08f57f75a2bb62d7ee80a89686a5e5669f199235c6d1dac75cd59374091c3", size = 2130598, upload-time = "2025-08-11T15:51:15.903Z" },
    { url = "https://files.pythonhosted.org/packages/8e/84/8a337454e82388283830b3586ad7847aa9c76fdd4f1df09cdd1f94591873/sqlalchemy-2.0.43-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:14111d22c29efad445cd5021a70a8b42f7d9152d8ba7f73304c4d82460946aaa", size = 2118415, upload-time = "2025-08-11T15:51:17.256Z" },
    { url = "https://files.pythonhosted.org/packages/cf/ff/22ab2328148492c4d71899d62a0e65370ea66c877aea017a244a35733685/sqlalchemy-2.0.43-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:21b27b56eb2f82653168cefe6cb8e970cdaf4f3a6cb2c5e3c3c1cf3158968ff9", size = 3248707, upload-time = "2025-08-11T15:52:38.444Z" },
    { url = "https://files.pythonhosted.org/packages/dc/29/11ae2c2b981de60187f7cbc84277d9d21f101093d1b2e945c63774477aba/sqlalchemy-2.0.43-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:9c5a9da957c56e43d72126a3f5845603da00e0293720b03bde0aacffcf2dc04f", size = 3253602, upload-time = "2025-08-11T15:56:37.348Z" },
    { url = "https://files.pythonhosted.org/packages/b8/61/987b6c23b12c56d2be451bc70900f67dd7d989d52b1ee64f239cf19aec69/sqlalchemy-2.0.43-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:5d79f9fdc9584ec83d1b3c75e9f4595c49017f5594fee1a2217117647225d738", size = 3183248, upload-time = "2025-08-11T15:52:39.865Z" },
    { url = "https://files.pythonhosted.org/packages/86/85/29d216002d4593c2ce1c0ec2cec46dda77bfbcd221e24caa6e85eff53d89/sqlalchemy-2.0.43-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:9df7126fd9db49e3a5a3999442cc67e9ee8971f3cb9644250107d7296cb2a164", size = 3219363, upload-time = "2025-08-11T15:56:39.11Z" },
    { url = "https://files.pythonhosted.org/packages/b6/e4/bd78b01919c524f190b4905d47e7630bf4130b9f48fd971ae1c6225b6f6a/sqlalchemy-2.0.43-cp313-cp313-win32.whl", hash = "sha256:7f1ac7828857fcedb0361b48b9ac4821469f7694089d15550bbcf9ab22564a1d", size = 2096718, upload-time = "2025-08-11T15:55:05.349Z" },
    { url = "https://files.pythonhosted.org/packages/ac/a5/ca2f07a2a201f9497de1928f787926613db6307992fe5cda97624eb07c2f/sqlalchemy-2.0.43-cp313-cp313-win_amd64.whl", hash = "sha256:971ba928fcde01869361f504fcff3b7143b47d30de188b11c6357c0505824197", size = 2123200, upload-time = "2025-08-11T15:55:07.932Z" },
    { url = "https://files.pythonhosted.org/packages/b8/d9/13bdde6521f322861fab67473cec4b1cc8999f3871953531cf61945fad92/sqlalchemy-2.0.43-py3-none-any.whl", hash = "sha256:1681c21dd2ccee222c2fe0bef671d1aef7c504087c9c4e800371cfcc8ac966fc", size = 1924759, upload-time = "2025-08-11T15:39:53.024Z" },
]

[[package]]
name = "starlette"
version = "0.47.3"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "anyio" },
]
sdist = { url = "https://files.pythonhosted.org/packages/15/b9/cc3017f9a9c9b6e27c5106cc10cc7904653c3eec0729793aec10479dd669/starlette-0.47.3.tar.gz", hash = "sha256:6bc94f839cc176c4858894f1f8908f0ab79dfec1a6b8402f6da9be26ebea52e9", size = 2584144, upload-time = "2025-08-24T13:36:42.122Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/ce/fd/901cfa59aaa5b30a99e16876f11abe38b59a1a2c51ffb3d7142bb6089069/starlette-0.47.3-py3-none-any.whl", hash = "sha256:89c0778ca62a76b826101e7c709e70680a1699ca7da6b44d38eb0a7e61fe4b51", size = 72991, upload-time = "2025-08-24T13:36:40.887Z" },
]

[[package]]
name = "text-unidecode"
version = "1.3"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/ab/e2/e9a00f0ccb71718418230718b3d900e71a5d16e701a3dae079a21e9cd8f8/text-unidecode-1.3.tar.gz", hash = "sha256:bad6603bb14d279193107714b288be206cac565dfa49aa5b105294dd5c4aab93", size = 76885, upload-time = "2019-08-30T21:36:45.405Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/a6/a5/c0b6468d3824fe3fde30dbb5e1f687b291608f9473681bbf7dabbf5a87d7/text_unidecode-1.3-py2.py3-none-any.whl", hash = "sha256:1311f10e8b895935241623731c2ba64f4c455287888b18189350b67134a822e8", size = 78154, upload-time = "2019-08-30T21:37:03.543Z" },
]

[[package]]
name = "typing-extensions"
version = "4.15.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/72/94/1a15dd82efb362ac84269196e94cf00f187f7ed21c242792a923cdb1c61f/typing_extensions-4.15.0.tar.gz", hash = "sha256:0cea48d173cc12fa28ecabc3b837ea3cf6f38c6d1136f85cbaaf598984861466", size = 109391, upload-time = "2025-08-25T13:49:26.313Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/18/67/36e9267722cc04a6b9f15c7f3441c2363321a3ea07da7ae0c0707beb2a9c/typing_extensions-4.15.0-py3-none-any.whl", hash = "sha256:f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548", size = 44614, upload-time = "2025-08-25T13:49:24.86Z" },
]

[[package]]
name = "typing-inspection"
version = "0.4.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/f8/b1/0c11f5058406b3af7609f121aaa6b609744687f1d158b3c3a5bf4cc94238/typing_inspection-0.4.1.tar.gz", hash = "sha256:6ae134cc0203c33377d43188d4064e9b357dba58cff3185f22924610e70a9d28", size = 75726, upload-time = "2025-05-21T18:55:23.885Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/17/69/cd203477f944c353c31bade965f880aa1061fd6bf05ded0726ca845b6ff7/typing_inspection-0.4.1-py3-none-any.whl", hash = "sha256:389055682238f53b04f7badcb49b989835495a96700ced5dab2d8feae4b26f51", size = 14552, upload-time = "2025-05-21T18:55:22.152Z" },
]

[[package]]
name = "uvicorn"
version = "0.35.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "click" },
    { name = "h11" },
]
sdist = { url = "https://files.pythonhosted.org/packages/5e/42/e0e305207bb88c6b8d3061399c6a961ffe5fbb7e2aa63c9234df7259e9cd/uvicorn-0.35.0.tar.gz", hash = "sha256:bc662f087f7cf2ce11a1d7fd70b90c9f98ef2e2831556dd078d131b96cc94a01", size = 78473, upload-time = "2025-06-28T16:15:46.058Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d2/e2/dc81b1bd1dcfe91735810265e9d26bc8ec5da45b4c0f6237e286819194c3/uvicorn-0.35.0-py3-none-any.whl", hash = "sha256:197535216b25ff9b785e29a0b79199f55222193d47f820816e7da751e9bc8d4a", size = 66406, upload-time = "2025-06-28T16:15:44.816Z" },
]

[package.optional-dependencies]
standard = [
    { name = "colorama", marker = "sys_platform == 'win32'" },
    { name = "httptools" },
    { name = "python-dotenv" },
    { name = "pyyaml" },
    { name = "uvloop", marker = "platform_python_implementation != 'PyPy' and sys_platform != 'cygwin' and sys_platform != 'win32'" },
    { name = "watchfiles" },
    { name = "websockets" },
]

[[package]]
name = "uvloop"
version = "0.21.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/af/c0/854216d09d33c543f12a44b393c402e89a920b1a0a7dc634c42de91b9cf6/uvloop-0.21.0.tar.gz", hash = "sha256:3bf12b0fda68447806a7ad847bfa591613177275d35b6724b1ee573faa3704e3", size = 2492741, upload-time = "2024-10-14T23:38:35.489Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/3f/8d/2cbef610ca21539f0f36e2b34da49302029e7c9f09acef0b1c3b5839412b/uvloop-0.21.0-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:bfd55dfcc2a512316e65f16e503e9e450cab148ef11df4e4e679b5e8253a5281", size = 1468123, upload-time = "2024-10-14T23:38:00.688Z" },
    { url = "https://files.pythonhosted.org/packages/93/0d/b0038d5a469f94ed8f2b2fce2434a18396d8fbfb5da85a0a9781ebbdec14/uvloop-0.21.0-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:787ae31ad8a2856fc4e7c095341cccc7209bd657d0e71ad0dc2ea83c4a6fa8af", size = 819325, upload-time = "2024-10-14T23:38:02.309Z" },
    { url = "https://files.pythonhosted.org/packages/50/94/0a687f39e78c4c1e02e3272c6b2ccdb4e0085fda3b8352fecd0410ccf915/uvloop-0.21.0-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:5ee4d4ef48036ff6e5cfffb09dd192c7a5027153948d85b8da7ff705065bacc6", size = 4582806, upload-time = "2024-10-14T23:38:04.711Z" },
    { url = "https://files.pythonhosted.org/packages/d2/19/f5b78616566ea68edd42aacaf645adbf71fbd83fc52281fba555dc27e3f1/uvloop-0.21.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:f3df876acd7ec037a3d005b3ab85a7e4110422e4d9c1571d4fc89b0fc41b6816", size = 4701068, upload-time = "2024-10-14T23:38:06.385Z" },
    { url = "https://files.pythonhosted.org/packages/47/57/66f061ee118f413cd22a656de622925097170b9380b30091b78ea0c6ea75/uvloop-0.21.0-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:bd53ecc9a0f3d87ab847503c2e1552b690362e005ab54e8a48ba97da3924c0dc", size = 4454428, upload-time = "2024-10-14T23:38:08.416Z" },
    { url = "https://files.pythonhosted.org/packages/63/9a/0962b05b308494e3202d3f794a6e85abe471fe3cafdbcf95c2e8c713aabd/uvloop-0.21.0-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:a5c39f217ab3c663dc699c04cbd50c13813e31d917642d459fdcec07555cc553", size = 4660018, upload-time = "2024-10-14T23:38:10.888Z" },
]

[[package]]
name = "watchfiles"
version = "1.1.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "anyio" },
]
sdist = { url = "https://files.pythonhosted.org/packages/2a/9a/d451fcc97d029f5812e898fd30a53fd8c15c7bbd058fd75cfc6beb9bd761/watchfiles-1.1.0.tar.gz", hash = "sha256:693ed7ec72cbfcee399e92c895362b6e66d63dac6b91e2c11ae03d10d503e575", size = 94406, upload-time = "2025-06-15T19:06:59.42Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d3/42/fae874df96595556a9089ade83be34a2e04f0f11eb53a8dbf8a8a5e562b4/watchfiles-1.1.0-cp313-cp313-macosx_10_12_x86_64.whl", hash = "sha256:5007f860c7f1f8df471e4e04aaa8c43673429047d63205d1630880f7637bca30", size = 402004, upload-time = "2025-06-15T19:05:38.499Z" },
    { url = "https://files.pythonhosted.org/packages/fa/55/a77e533e59c3003d9803c09c44c3651224067cbe7fb5d574ddbaa31e11ca/watchfiles-1.1.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:20ecc8abbd957046f1fe9562757903f5eaf57c3bce70929fda6c7711bb58074a", size = 393671, upload-time = "2025-06-15T19:05:39.52Z" },
    { url = "https://files.pythonhosted.org/packages/05/68/b0afb3f79c8e832e6571022611adbdc36e35a44e14f129ba09709aa4bb7a/watchfiles-1.1.0-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:f2f0498b7d2a3c072766dba3274fe22a183dbea1f99d188f1c6c72209a1063dc", size = 449772, upload-time = "2025-06-15T19:05:40.897Z" },
    { url = "https://files.pythonhosted.org/packages/ff/05/46dd1f6879bc40e1e74c6c39a1b9ab9e790bf1f5a2fe6c08b463d9a807f4/watchfiles-1.1.0-cp313-cp313-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:239736577e848678e13b201bba14e89718f5c2133dfd6b1f7846fa1b58a8532b", size = 456789, upload-time = "2025-06-15T19:05:42.045Z" },
    { url = "https://files.pythonhosted.org/packages/8b/ca/0eeb2c06227ca7f12e50a47a3679df0cd1ba487ea19cf844a905920f8e95/watchfiles-1.1.0-cp313-cp313-manylinux_2_17_i686.manylinux2014_i686.whl", hash = "sha256:eff4b8d89f444f7e49136dc695599a591ff769300734446c0a86cba2eb2f9895", size = 482551, upload-time = "2025-06-15T19:05:43.781Z" },
    { url = "https://files.pythonhosted.org/packages/31/47/2cecbd8694095647406645f822781008cc524320466ea393f55fe70eed3b/watchfiles-1.1.0-cp313-cp313-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:12b0a02a91762c08f7264e2e79542f76870c3040bbc847fb67410ab81474932a", size = 597420, upload-time = "2025-06-15T19:05:45.244Z" },
    { url = "https://files.pythonhosted.org/packages/d9/7e/82abc4240e0806846548559d70f0b1a6dfdca75c1b4f9fa62b504ae9b083/watchfiles-1.1.0-cp313-cp313-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:29e7bc2eee15cbb339c68445959108803dc14ee0c7b4eea556400131a8de462b", size = 477950, upload-time = "2025-06-15T19:05:46.332Z" },
    { url = "https://files.pythonhosted.org/packages/25/0d/4d564798a49bf5482a4fa9416dea6b6c0733a3b5700cb8a5a503c4b15853/watchfiles-1.1.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:d9481174d3ed982e269c090f780122fb59cee6c3796f74efe74e70f7780ed94c", size = 451706, upload-time = "2025-06-15T19:05:47.459Z" },
    { url = "https://files.pythonhosted.org/packages/81/b5/5516cf46b033192d544102ea07c65b6f770f10ed1d0a6d388f5d3874f6e4/watchfiles-1.1.0-cp313-cp313-musllinux_1_1_aarch64.whl", hash = "sha256:80f811146831c8c86ab17b640801c25dc0a88c630e855e2bef3568f30434d52b", size = 625814, upload-time = "2025-06-15T19:05:48.654Z" },
    { url = "https://files.pythonhosted.org/packages/0c/dd/7c1331f902f30669ac3e754680b6edb9a0dd06dea5438e61128111fadd2c/watchfiles-1.1.0-cp313-cp313-musllinux_1_1_x86_64.whl", hash = "sha256:60022527e71d1d1fda67a33150ee42869042bce3d0fcc9cc49be009a9cded3fb", size = 622820, upload-time = "2025-06-15T19:05:50.088Z" },
    { url = "https://files.pythonhosted.org/packages/1b/14/36d7a8e27cd128d7b1009e7715a7c02f6c131be9d4ce1e5c3b73d0e342d8/watchfiles-1.1.0-cp313-cp313-win32.whl", hash = "sha256:32d6d4e583593cb8576e129879ea0991660b935177c0f93c6681359b3654bfa9", size = 279194, upload-time = "2025-06-15T19:05:51.186Z" },
    { url = "https://files.pythonhosted.org/packages/25/41/2dd88054b849aa546dbeef5696019c58f8e0774f4d1c42123273304cdb2e/watchfiles-1.1.0-cp313-cp313-win_amd64.whl", hash = "sha256:f21af781a4a6fbad54f03c598ab620e3a77032c5878f3d780448421a6e1818c7", size = 292349, upload-time = "2025-06-15T19:05:52.201Z" },
    { url = "https://files.pythonhosted.org/packages/c8/cf/421d659de88285eb13941cf11a81f875c176f76a6d99342599be88e08d03/watchfiles-1.1.0-cp313-cp313-win_arm64.whl", hash = "sha256:5366164391873ed76bfdf618818c82084c9db7fac82b64a20c44d335eec9ced5", size = 283836, upload-time = "2025-06-15T19:05:53.265Z" },
    { url = "https://files.pythonhosted.org/packages/45/10/6faf6858d527e3599cc50ec9fcae73590fbddc1420bd4fdccfebffeedbc6/watchfiles-1.1.0-cp313-cp313t-macosx_10_12_x86_64.whl", hash = "sha256:17ab167cca6339c2b830b744eaf10803d2a5b6683be4d79d8475d88b4a8a4be1", size = 400343, upload-time = "2025-06-15T19:05:54.252Z" },
    { url = "https://files.pythonhosted.org/packages/03/20/5cb7d3966f5e8c718006d0e97dfe379a82f16fecd3caa7810f634412047a/watchfiles-1.1.0-cp313-cp313t-macosx_11_0_arm64.whl", hash = "sha256:328dbc9bff7205c215a7807da7c18dce37da7da718e798356212d22696404339", size = 392916, upload-time = "2025-06-15T19:05:55.264Z" },
    { url = "https://files.pythonhosted.org/packages/8c/07/d8f1176328fa9e9581b6f120b017e286d2a2d22ae3f554efd9515c8e1b49/watchfiles-1.1.0-cp313-cp313t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:f7208ab6e009c627b7557ce55c465c98967e8caa8b11833531fdf95799372633", size = 449582, upload-time = "2025-06-15T19:05:56.317Z" },
    { url = "https://files.pythonhosted.org/packages/66/e8/80a14a453cf6038e81d072a86c05276692a1826471fef91df7537dba8b46/watchfiles-1.1.0-cp313-cp313t-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:a8f6f72974a19efead54195bc9bed4d850fc047bb7aa971268fd9a8387c89011", size = 456752, upload-time = "2025-06-15T19:05:57.359Z" },
    { url = "https://files.pythonhosted.org/packages/5a/25/0853b3fe0e3c2f5af9ea60eb2e781eade939760239a72c2d38fc4cc335f6/watchfiles-1.1.0-cp313-cp313t-manylinux_2_17_i686.manylinux2014_i686.whl", hash = "sha256:d181ef50923c29cf0450c3cd47e2f0557b62218c50b2ab8ce2ecaa02bd97e670", size = 481436, upload-time = "2025-06-15T19:05:58.447Z" },
    { url = "https://files.pythonhosted.org/packages/fe/9e/4af0056c258b861fbb29dcb36258de1e2b857be4a9509e6298abcf31e5c9/watchfiles-1.1.0-cp313-cp313t-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:adb4167043d3a78280d5d05ce0ba22055c266cf8655ce942f2fb881262ff3cdf", size = 596016, upload-time = "2025-06-15T19:05:59.59Z" },
    { url = "https://files.pythonhosted.org/packages/c5/fa/95d604b58aa375e781daf350897aaaa089cff59d84147e9ccff2447c8294/watchfiles-1.1.0-cp313-cp313t-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:8c5701dc474b041e2934a26d31d39f90fac8a3dee2322b39f7729867f932b1d4", size = 476727, upload-time = "2025-06-15T19:06:01.086Z" },
    { url = "https://files.pythonhosted.org/packages/65/95/fe479b2664f19be4cf5ceeb21be05afd491d95f142e72d26a42f41b7c4f8/watchfiles-1.1.0-cp313-cp313t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:b067915e3c3936966a8607f6fe5487df0c9c4afb85226613b520890049deea20", size = 451864, upload-time = "2025-06-15T19:06:02.144Z" },
    { url = "https://files.pythonhosted.org/packages/d3/8a/3c4af14b93a15ce55901cd7a92e1a4701910f1768c78fb30f61d2b79785b/watchfiles-1.1.0-cp313-cp313t-musllinux_1_1_aarch64.whl", hash = "sha256:9c733cda03b6d636b4219625a4acb5c6ffb10803338e437fb614fef9516825ef", size = 625626, upload-time = "2025-06-15T19:06:03.578Z" },
    { url = "https://files.pythonhosted.org/packages/da/f5/cf6aa047d4d9e128f4b7cde615236a915673775ef171ff85971d698f3c2c/watchfiles-1.1.0-cp313-cp313t-musllinux_1_1_x86_64.whl", hash = "sha256:cc08ef8b90d78bfac66f0def80240b0197008e4852c9f285907377b2947ffdcb", size = 622744, upload-time = "2025-06-15T19:06:05.066Z" },
    { url = "https://files.pythonhosted.org/packages/2c/00/70f75c47f05dea6fd30df90f047765f6fc2d6eb8b5a3921379b0b04defa2/watchfiles-1.1.0-cp314-cp314-macosx_10_12_x86_64.whl", hash = "sha256:9974d2f7dc561cce3bb88dfa8eb309dab64c729de85fba32e98d75cf24b66297", size = 402114, upload-time = "2025-06-15T19:06:06.186Z" },
    { url = "https://files.pythonhosted.org/packages/53/03/acd69c48db4a1ed1de26b349d94077cca2238ff98fd64393f3e97484cae6/watchfiles-1.1.0-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:c68e9f1fcb4d43798ad8814c4c1b61547b014b667216cb754e606bfade587018", size = 393879, upload-time = "2025-06-15T19:06:07.369Z" },
    { url = "https://files.pythonhosted.org/packages/2f/c8/a9a2a6f9c8baa4eceae5887fecd421e1b7ce86802bcfc8b6a942e2add834/watchfiles-1.1.0-cp314-cp314-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:95ab1594377effac17110e1352989bdd7bdfca9ff0e5eeccd8c69c5389b826d0", size = 450026, upload-time = "2025-06-15T19:06:08.476Z" },
    { url = "https://files.pythonhosted.org/packages/fe/51/d572260d98388e6e2b967425c985e07d47ee6f62e6455cefb46a6e06eda5/watchfiles-1.1.0-cp314-cp314-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:fba9b62da882c1be1280a7584ec4515d0a6006a94d6e5819730ec2eab60ffe12", size = 457917, upload-time = "2025-06-15T19:06:09.988Z" },
    { url = "https://files.pythonhosted.org/packages/c6/2d/4258e52917bf9f12909b6ec314ff9636276f3542f9d3807d143f27309104/watchfiles-1.1.0-cp314-cp314-manylinux_2_17_i686.manylinux2014_i686.whl", hash = "sha256:3434e401f3ce0ed6b42569128b3d1e3af773d7ec18751b918b89cd49c14eaafb", size = 483602, upload-time = "2025-06-15T19:06:11.088Z" },
    { url = "https://files.pythonhosted.org/packages/84/99/bee17a5f341a4345fe7b7972a475809af9e528deba056f8963d61ea49f75/watchfiles-1.1.0-cp314-cp314-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:fa257a4d0d21fcbca5b5fcba9dca5a78011cb93c0323fb8855c6d2dfbc76eb77", size = 596758, upload-time = "2025-06-15T19:06:12.197Z" },
    { url = "https://files.pythonhosted.org/packages/40/76/e4bec1d59b25b89d2b0716b41b461ed655a9a53c60dc78ad5771fda5b3e6/watchfiles-1.1.0-cp314-cp314-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:7fd1b3879a578a8ec2076c7961076df540b9af317123f84569f5a9ddee64ce92", size = 477601, upload-time = "2025-06-15T19:06:13.391Z" },
    { url = "https://files.pythonhosted.org/packages/1f/fa/a514292956f4a9ce3c567ec0c13cce427c158e9f272062685a8a727d08fc/watchfiles-1.1.0-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:62cc7a30eeb0e20ecc5f4bd113cd69dcdb745a07c68c0370cea919f373f65d9e", size = 451936, upload-time = "2025-06-15T19:06:14.656Z" },
    { url = "https://files.pythonhosted.org/packages/32/5d/c3bf927ec3bbeb4566984eba8dd7a8eb69569400f5509904545576741f88/watchfiles-1.1.0-cp314-cp314-musllinux_1_1_aarch64.whl", hash = "sha256:891c69e027748b4a73847335d208e374ce54ca3c335907d381fde4e41661b13b", size = 626243, upload-time = "2025-06-15T19:06:16.232Z" },
    { url = "https://files.pythonhosted.org/packages/e6/65/6e12c042f1a68c556802a84d54bb06d35577c81e29fba14019562479159c/watchfiles-1.1.0-cp314-cp314-musllinux_1_1_x86_64.whl", hash = "sha256:12fe8eaffaf0faa7906895b4f8bb88264035b3f0243275e0bf24af0436b27259", size = 623073, upload-time = "2025-06-15T19:06:17.457Z" },
    { url = "https://files.pythonhosted.org/packages/89/ab/7f79d9bf57329e7cbb0a6fd4c7bd7d0cee1e4a8ef0041459f5409da3506c/watchfiles-1.1.0-cp314-cp314t-macosx_10_12_x86_64.whl", hash = "sha256:bfe3c517c283e484843cb2e357dd57ba009cff351edf45fb455b5fbd1f45b15f", size = 400872, upload-time = "2025-06-15T19:06:18.57Z" },
    { url = "https://files.pythonhosted.org/packages/df/d5/3f7bf9912798e9e6c516094db6b8932df53b223660c781ee37607030b6d3/watchfiles-1.1.0-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:a9ccbf1f129480ed3044f540c0fdbc4ee556f7175e5ab40fe077ff6baf286d4e", size = 392877, upload-time = "2025-06-15T19:06:19.55Z" },
    { url = "https://files.pythonhosted.org/packages/0d/c5/54ec7601a2798604e01c75294770dbee8150e81c6e471445d7601610b495/watchfiles-1.1.0-cp314-cp314t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:ba0e3255b0396cac3cc7bbace76404dd72b5438bf0d8e7cefa2f79a7f3649caa", size = 449645, upload-time = "2025-06-15T19:06:20.66Z" },
    { url = "https://files.pythonhosted.org/packages/0a/04/c2f44afc3b2fce21ca0b7802cbd37ed90a29874f96069ed30a36dfe57c2b/watchfiles-1.1.0-cp314-cp314t-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:4281cd9fce9fc0a9dbf0fc1217f39bf9cf2b4d315d9626ef1d4e87b84699e7e8", size = 457424, upload-time = "2025-06-15T19:06:21.712Z" },
    { url = "https://files.pythonhosted.org/packages/9f/b0/eec32cb6c14d248095261a04f290636da3df3119d4040ef91a4a50b29fa5/watchfiles-1.1.0-cp314-cp314t-manylinux_2_17_i686.manylinux2014_i686.whl", hash = "sha256:6d2404af8db1329f9a3c9b79ff63e0ae7131986446901582067d9304ae8aaf7f", size = 481584, upload-time = "2025-06-15T19:06:22.777Z" },
    { url = "https://files.pythonhosted.org/packages/d1/e2/ca4bb71c68a937d7145aa25709e4f5d68eb7698a25ce266e84b55d591bbd/watchfiles-1.1.0-cp314-cp314t-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:e78b6ed8165996013165eeabd875c5dfc19d41b54f94b40e9fff0eb3193e5e8e", size = 596675, upload-time = "2025-06-15T19:06:24.226Z" },
    { url = "https://files.pythonhosted.org/packages/a1/dd/b0e4b7fb5acf783816bc950180a6cd7c6c1d2cf7e9372c0ea634e722712b/watchfiles-1.1.0-cp314-cp314t-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:249590eb75ccc117f488e2fabd1bfa33c580e24b96f00658ad88e38844a040bb", size = 477363, upload-time = "2025-06-15T19:06:25.42Z" },
    { url = "https://files.pythonhosted.org/packages/69/c4/088825b75489cb5b6a761a4542645718893d395d8c530b38734f19da44d2/watchfiles-1.1.0-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:d05686b5487cfa2e2c28ff1aa370ea3e6c5accfe6435944ddea1e10d93872147", size = 452240, upload-time = "2025-06-15T19:06:26.552Z" },
    { url = "https://files.pythonhosted.org/packages/10/8c/22b074814970eeef43b7c44df98c3e9667c1f7bf5b83e0ff0201b0bd43f9/watchfiles-1.1.0-cp314-cp314t-musllinux_1_1_aarch64.whl", hash = "sha256:d0e10e6f8f6dc5762adee7dece33b722282e1f59aa6a55da5d493a97282fedd8", size = 625607, upload-time = "2025-06-15T19:06:27.606Z" },
    { url = "https://files.pythonhosted.org/packages/32/fa/a4f5c2046385492b2273213ef815bf71a0d4c1943b784fb904e184e30201/watchfiles-1.1.0-cp314-cp314t-musllinux_1_1_x86_64.whl", hash = "sha256:af06c863f152005c7592df1d6a7009c836a247c9d8adb78fef8575a5a98699db", size = 623315, upload-time = "2025-06-15T19:06:29.076Z" },
]

[[package]]
name = "websockets"
version = "15.0.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/21/e6/26d09fab466b7ca9c7737474c52be4f76a40301b08362eb2dbc19dcc16c1/websockets-15.0.1.tar.gz", hash = "sha256:82544de02076bafba038ce055ee6412d68da13ab47f0c60cab827346de828dee", size = 177016, upload-time = "2025-03-05T20:03:41.606Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/cb/9f/51f0cf64471a9d2b4d0fc6c534f323b664e7095640c34562f5182e5a7195/websockets-15.0.1-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:ee443ef070bb3b6ed74514f5efaa37a252af57c90eb33b956d35c8e9c10a1931", size = 175440, upload-time = "2025-03-05T20:02:36.695Z" },
    { url = "https://files.pythonhosted.org/packages/8a/05/aa116ec9943c718905997412c5989f7ed671bc0188ee2ba89520e8765d7b/websockets-15.0.1-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:5a939de6b7b4e18ca683218320fc67ea886038265fd1ed30173f5ce3f8e85675", size = 173098, upload-time = "2025-03-05T20:02:37.985Z" },
    { url = "https://files.pythonhosted.org/packages/ff/0b/33cef55ff24f2d92924923c99926dcce78e7bd922d649467f0eda8368923/websockets-15.0.1-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:746ee8dba912cd6fc889a8147168991d50ed70447bf18bcda7039f7d2e3d9151", size = 173329, upload-time = "2025-03-05T20:02:39.298Z" },
    { url = "https://files.pythonhosted.org/packages/31/1d/063b25dcc01faa8fada1469bdf769de3768b7044eac9d41f734fd7b6ad6d/websockets-15.0.1-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:595b6c3969023ecf9041b2936ac3827e4623bfa3ccf007575f04c5a6aa318c22", size = 183111, upload-time = "2025-03-05T20:02:40.595Z" },
    { url = "https://files.pythonhosted.org/packages/93/53/9a87ee494a51bf63e4ec9241c1ccc4f7c2f45fff85d5bde2ff74fcb68b9e/websockets-15.0.1-cp313-cp313-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl", hash = "sha256:3c714d2fc58b5ca3e285461a4cc0c9a66bd0e24c5da9911e30158286c9b5be7f", size = 182054, upload-time = "2025-03-05T20:02:41.926Z" },
    { url = "https://files.pythonhosted.org/packages/ff/b2/83a6ddf56cdcbad4e3d841fcc55d6ba7d19aeb89c50f24dd7e859ec0805f/websockets-15.0.1-cp313-cp313-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:0f3c1e2ab208db911594ae5b4f79addeb3501604a165019dd221c0bdcabe4db8", size = 182496, upload-time = "2025-03-05T20:02:43.304Z" },
    { url = "https://files.pythonhosted.org/packages/98/41/e7038944ed0abf34c45aa4635ba28136f06052e08fc2168520bb8b25149f/websockets-15.0.1-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:229cf1d3ca6c1804400b0a9790dc66528e08a6a1feec0d5040e8b9eb14422375", size = 182829, upload-time = "2025-03-05T20:02:48.812Z" },
    { url = "https://files.pythonhosted.org/packages/e0/17/de15b6158680c7623c6ef0db361da965ab25d813ae54fcfeae2e5b9ef910/websockets-15.0.1-cp313-cp313-musllinux_1_2_i686.whl", hash = "sha256:756c56e867a90fb00177d530dca4b097dd753cde348448a1012ed6c5131f8b7d", size = 182217, upload-time = "2025-03-05T20:02:50.14Z" },
    { url = "https://files.pythonhosted.org/packages/33/2b/1f168cb6041853eef0362fb9554c3824367c5560cbdaad89ac40f8c2edfc/websockets-15.0.1-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:558d023b3df0bffe50a04e710bc87742de35060580a293c2a984299ed83bc4e4", size = 182195, upload-time = "2025-03-05T20:02:51.561Z" },
    { url = "https://files.pythonhosted.org/packages/86/eb/20b6cdf273913d0ad05a6a14aed4b9a85591c18a987a3d47f20fa13dcc47/websockets-15.0.1-cp313-cp313-win32.whl", hash = "sha256:ba9e56e8ceeeedb2e080147ba85ffcd5cd0711b89576b83784d8605a7df455fa", size = 176393, upload-time = "2025-03-05T20:02:53.814Z" },
    { url = "https://files.pythonhosted.org/packages/1b/6c/c65773d6cab416a64d191d6ee8a8b1c68a09970ea6909d16965d26bfed1e/websockets-15.0.1-cp313-cp313-win_amd64.whl", hash = "sha256:e09473f095a819042ecb2ab9465aee615bd9c2028e4ef7d933600a8401c79561", size = 176837, upload-time = "2025-03-05T20:02:55.237Z" },
    { url = "https://files.pythonhosted.org/packages/fa/a8/5b41e0da817d64113292ab1f8247140aac61cbf6cfd085d6a0fa77f4984f/websockets-15.0.1-py3-none-any.whl", hash = "sha256:f7a866fbc1e97b5c617ee4116daaa09b722101d4a3c170c787450ba409f9736f", size = 169743, upload-time = "2025-03-05T20:03:39.41Z" },
]

[[package]]
name = "win32-setctime"
version = "1.2.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/b3/8f/705086c9d734d3b663af0e9bb3d4de6578d08f46b1b101c2442fd9aecaa2/win32_setctime-1.2.0.tar.gz", hash = "sha256:ae1fdf948f5640aae05c511ade119313fb6a30d7eabe25fef9764dca5873c4c0", size = 4867, upload-time = "2024-12-07T15:28:28.314Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/e1/07/c6fe3ad3e685340704d314d765b7912993bcb8dc198f0e7a89382d37974b/win32_setctime-1.2.0-py3-none-any.whl", hash = "sha256:95d644c4e708aba81dc3704a116d8cbc974d70b3bdb8be1d150e36be6e9d1390", size = 4083, upload-time = "2024-12-07T15:28:26.465Z" },
]

```
