Генератор протоколов для mkair. FastAPI-приложение находится в каталоге `app/` (роуты в `app/api/routes/`, схемы — `app/schemas/`, сервисы — `app/services/`, утилиты — `app/utils/`, общие настройки и логирование — `app/core/`).

Быстрый старт
1. Скопируйте `app/.env.example` в корень как `.env` и задайте локальные секреты: `DATABASE_URL`, `ARSHIN_TIMEOUT`, `ARSHIN_CONCURRENCY`, `USER_AGENT` и т.д.
2. Установите зависимости строго по лок-файлу: `uv sync` (предпочтительно) или `pip install -e .[dev]`.
3. Примените миграции: `uv run alembic upgrade head`.
4. (Опционально) Один раз заполните справочники: `uv run python -m app.db.seed`. Приложение делает то же при старте, поэтому команда нужна в основном для CI и первичной настройки.
5. Запустите API локально: `uvicorn app.main:app --reload` → http://127.0.0.1:8000.

Docker
- Полная сборка и запуск: `docker compose up --build`. В образ копируются `pyproject.toml` и `uv.lock`, поэтому обновляйте лок-файл командой `uv sync` при изменении зависимостей.
- Скрипт `docker-entrypoint.sh` внутри контейнера запускает миграции и поднимает Uvicorn; при необходимости можно переопределить entrypoint.

База данных
- Роуты контроллеров/манометров принимают Excel из реестра, нормализуют строки и делают upsert в Postgres, поэтому повторные загрузки идемпотентны.
- `verification_registry_entries` кеширует строки выгрузки с индексами по номеру, документу и протоколу.
- `measuring_instruments` связывает приборы с владельцами, методиками и записями реестра.
- `etalon_devices` и `etalon_certifications` сохраняют ответы Аршина для повторного использования.
- `methodologies`, `methodology_aliases`, `methodology_points` описывают перечень МП, псевдонимы и набор пунктов (флаги/клаузулы/custom).
- `owners` и `owner_aliases` заменяют Python-словари, давая единый источник истины (название + ИНН).

Тесты и линтеры
- Тесты: `pytest -q`, при необходимости покрытия `pytest --cov=app -q`.
- Линтеры/формат: `ruff check .` и `ruff format .`; при желании дополнительно `black .`.

Pre-commit
- Установка хуков: `pip install pre-commit && pre-commit install`.
- Запускаются Ruff (линт/формат) и опционально Black (см. `.pre-commit-config.yaml`).
