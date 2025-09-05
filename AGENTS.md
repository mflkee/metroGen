# Repository Guidelines

## Project Structure & Module Organization
- `app/`: FastAPI application code.
  - `api/routes/`: HTTP routes (e.g., `arshin.py`).
  - `core/`: config (`config.py` via pydantic‑settings), logging (`logging.py`).
  - `services/`: external integrations (e.g., `arshin_client.py` using httpx).
  - `schemas/`: Pydantic models for request/response.
  - `utils/`: helpers (e.g., `excel.py`).
- `tests/`: pytest suite with async fixtures and respx mocks.
- `pyproject.toml` + `uv.lock`: Python package and lockfile.
- `.env.example`: copy to `.env` for local settings.

## Build, Test, and Development Commands
- Install deps (choose one): `uv sync` (recommended, uses `uv.lock`) or `pip install -e .[dev]`.
- Run API locally: `uvicorn app.main:app --reload` (default: http://127.0.0.1:8000).
- Run tests: `pytest -q` or with coverage `pytest --cov=app -q`.
- Lint/format (if needed): follow PEP 8; prefer `ruff`/`black` if added.

## Coding Style & Naming Conventions
- Python 3.13, 4‑space indents, type hints required for public functions.
- Modules and functions: `snake_case`; classes and Pydantic models: `PascalCase`.
- Routes live in `app/api/routes`, services in `app/services`, schemas in `app/schemas`.
- Keep I/O at route layer; put external calls and parsing in services/utils.
- Use `settings` from `app.core.config` and `setup_logging()` from `app.core.logging`.

## Testing Guidelines
- Frameworks: `pytest`, `pytest-asyncio`, `respx`, `pytest-cov`.
- File names: `tests/test_*.py`; shared fixtures in `tests/conftest.py`.
- Write async tests for endpoints and mock HTTP with `respx`.
- Aim to cover new routes/services; run `pytest --cov=app` before submitting.

## Commit & Pull Request Guidelines
- Commits: concise, imperative subject (≤72 chars). Example: `feat(api): add /resolve/vri-details-by-excel`.
- PRs: include description, linked issues, test results, and API examples (curl or payloads).
- Add screenshots when relevant (e.g., Swagger, example response JSON).

## Security & Configuration Tips
- Copy `.env.example` to `.env`; never commit secrets. Notable vars: `APP_NAME`, `ARSHIN_TIMEOUT`, `ARSHIN_CONCURRENCY`, `USER_AGENT`.
- Outbound HTTP: use `httpx.AsyncClient` and respect timeouts from `settings`.
- Keep external API logic isolated in `app/services` and validate responses via Pydantic schemas where feasible.

