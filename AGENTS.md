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
