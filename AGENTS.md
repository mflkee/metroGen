# Repository Guidelines

## Project Structure & Module Organization
- `app/`: FastAPI application code.
  - `api/routes/`: HTTP routes (e.g., `arshin.py`).
  - `core/`: config via Pydantic settings (`config.py`), logging (`logging.py`).
  - `services/`: external integrations (e.g., `arshin_client.py` using `httpx`).
  - `schemas/`: Pydantic models for requests/responses.
  - `utils/`: helpers (e.g., `excel.py`).
- `tests/`: pytest suite with async fixtures and `respx` mocks.
- `pyproject.toml`, `uv.lock`: packaging + locked dependencies.
- `.env.example`: copy to `.env` for local settings.

## Build, Test, and Development Commands
- Install deps: `uv sync` (preferred, uses `uv.lock`) or `pip install -e .[dev]`.
- Run API: `uvicorn app.main:app --reload` (http://127.0.0.1:8000).
- Run tests: `pytest -q` or with coverage `pytest --cov=app -q`.
- Lint/format: follow PEP 8; use `ruff`/`black` if configured.

## Coding Style & Naming Conventions
- Python 3.13, 4-space indents, type hints for public functions.
- Names: modules/functions `snake_case`; classes/Pydantic `PascalCase`.
- Layout: routes in `app/api/routes`, services in `app/services`, schemas in `app/schemas`.
- Separation: keep I/O in routes; put external calls/parsing in services/utils.
- Config/logging: import `settings` from `app.core.config`; call `setup_logging()` from `app.core.logging`.

## Testing Guidelines
- Frameworks: `pytest`, `pytest-asyncio`, `respx`, `pytest-cov`.
- Naming: files `tests/test_*.py`; prefer async tests for endpoints.
- HTTP mocking: use `respx` for external requests.
- Coverage: aim to cover new routes/services; run `pytest --cov=app` before submitting.

## Commit & Pull Request Guidelines
- Commits: concise, imperative subject (≤72 chars). Example: `feat(api): add /resolve/vri-details-by-excel`.
- PRs: include description, linked issues, test results, and API examples (curl/payloads). Add screenshots when relevant (e.g., Swagger, example responses).
- Documentation: update README/docs and schemas when adding/modifying endpoints.

## Security & Configuration Tips
- Copy `.env.example` to `.env`; never commit secrets. Notable vars: `APP_NAME`, `ARSHIN_TIMEOUT`, `ARSHIN_CONCURRENCY`, `USER_AGENT`.
- Outbound HTTP: use `httpx.AsyncClient` and respect timeouts from `settings`.
- Isolation: keep external API logic in `app/services`; validate responses with Pydantic models where feasible.

