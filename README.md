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
