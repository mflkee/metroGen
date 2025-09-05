Protocol generator for mkair

Quick start
- Install deps: `uv sync` (preferred) or `pip install -e .[dev]`
- Run API: `uvicorn app.main:app --reload` → http://127.0.0.1:8000
- Run tests: `pytest -q` or with coverage `pytest --cov=app -q`

Code style
- Lint/format via Ruff: `ruff check .` and `ruff format .`
- Optionally Black: `black .`

Pre-commit
- Install: `pip install pre-commit` then `pre-commit install`
- Hooks: Ruff (lint+format), optional Black (see `.pre-commit-config.yaml`)
