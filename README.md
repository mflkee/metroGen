# Metrologenerator

FastAPI‑сервис для автоматизации подготовки протоколов поверки манометров и выгрузок из Аршина. Приложение принимает Excel‑шаблоны, находит сведения в реестре, подтягивает детали из API Аршин и генерирует HTML/PDF протоколы с заполненными таблицами.

## Возможности
- Загрузка Excel с приборами (`/api/v1/protocols/context-by-excel`, `/manometers/pdf-files`) и автоматическое построение контекста протокола.
- Импорт выгрузок БД реестра через `/api/v1/registry/import` с нормализацией владельцев, методик и номеров свидетельств.
- Вызовы к Аршину (`/api/v1/resolve/*`) для поиска `vri_id`, сведений об эталонах и сертификатов.
- Хранение справочников методик/владельцев в Postgres с автоматическим наполнением при старте приложения.
- Генерация PDF средствами Playwright (Chromium) и сохранение файлов в `exports/`.

## Технологический стек
- Python 3.13, FastAPI, SQLAlchemy 2, Alembic.
- PostgreSQL (локально можно использовать `dev.db`/SQLite, но целевой режим — Postgres).
- HTTP клиенты: `httpx`, `respx` в тестах.
- Инструменты качества: `pytest`, `pytest-asyncio`, `ruff`, `black`.
- Сборка/зависимости через `uv`, контейнеризация — Docker/Compose.

## Структура проекта
| Каталог / файл | Назначение |
| --- | --- |
| `app/api/routes/` | FastAPI‑ручки (`protocols`, `arshin`, `registry`, `methodologies`, `owners`). |
| `app/services/` | Основная бизнес‑логика: генераторы таблиц, билдер протоколов, Playwright PDF, Arshin client. |
| `app/templates/` | HTML/Jinja2 формы протоколов (`pressure.html`, `controller_43790_12.html`). |
| `app/core/` | Настройки (`config.py`) и логирование. |
| `app/db/` | Модели SQLAlchemy, репозитории и сиды. |
| `data/` | Примеры Excel/вспомогательные данные (`data/input/*`, `data/signatures`). |
| `exports/` | Готовые PDF, создаются автоматически. |
| `output/` | Временные артефакты (HTML и т.п.). |
| `docker-entrypoint.sh` | Применяет миграции и стартует Uvicorn в контейнере. |

## Требования
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) 0.4+
- PostgreSQL 16 (или совместимый) — для Docker используется контейнер `postgres:16-alpine`.
- Playwright Chromium (для PDF). В контейнере браузер устанавливается автоматически; локально нужно выполнить `uv run playwright install --with-deps chromium`.
- Docker + Docker Compose (опционально, для контейнерного запуска).

## Подготовка окружения (локально)
1. Склонируйте репозиторий и перейдите в каталог проекта.
2. Скопируйте `app/.env.example` → `.env` в корне. Укажите `DATABASE_URL`, `ARSHIN_TIMEOUT`, `ARSHIN_CONCURRENCY`, `USER_AGENT`. Для локального Postgres:  
   `DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/metrologenerator`
3. Установите зависимости: `uv sync`.
4. Установите Playwright Chromium: `uv run playwright install --with-deps chromium`.
5. Примените миграции: `uv run alembic upgrade head`.
6. При необходимости заполните справочники: `uv run python -m app.db.seed` (FastAPI делает то же при старте, но команда полезна для CI).

## Запуск API (локально)
```bash
uv run uvicorn app.main:app --reload
# сервис поднимется на http://127.0.0.1:8000
```

## Docker / Compose
```bash
docker compose up --build
```
- Контейнер `db` (Postgres 16) проброшен на `localhost:15432` → `5432`.
- `docker-entrypoint.sh` внутри `api` применяет миграции и запускает Uvicorn.
- Во время сборки образа выполняется `uv sync --frozen --no-dev` и `/.venv/bin/python -m playwright install --with-deps chromium`, поэтому PDF работает «из коробки».

Остановка: `docker compose down` (дополнительно `-v`, если нужно удалить volume `pgdata`).

## Работа с API

### Протоколы
- `POST /api/v1/protocols/context-by-excel` — принимает Excel с колонками как минимум `Обозначение СИ`, `Заводской номер`, `Методика поверки`, `Свидетельство о поверке`. Возвращает список контекстов (по одному на строку Excel) и предложенное имя файла.
- `POST /api/v1/protocols/html-by-excel` — тот же формат, но возвращает HTML первой строки (удобно для отладки шаблонов).
- `POST /api/v1/protocols/manometers/pdf-files` — основной сценарий. Параметры multipart:
  - `manometers_file`: Excel с данными поверяемых СИ.
  - `db_file` (опционально, но желательно): выгрузка из БД (начиная с 5‑й строки заголовка). Если передан, файл импортируется в базу, и протоколы получают номера/сертификаты из реестра.
  - Ответ содержит список путей к сохранённым PDF в `exports/PDF Манометры <месяц>`.

Пример запроса (контекст по Excel):
```bash
curl -X POST \
     -F "file=@data/input/Поверка манометры 06.2025.xlsm" \
     http://127.0.0.1:8000/api/v1/protocols/context-by-excel
```

### Работа с реестром
- `POST /api/v1/registry/import` — загружает Excel выгрузку, ищет заголовки из `REGISTRY_SERIAL_KEYS` и кладёт строки в таблицу `verification_registry_entries`.  
  Пример:
  ```bash
  curl -X POST \
       -F "db_file=@data/input/09\ БД.xlsx" \
       "http://127.0.0.1:8000/api/v1/registry/import?instrument_kind=manometers"
  ```

### Ручки для Аршина
- `GET /api/v1/resolve/vri-id?cert=<номер>` — ищет `vri_id` по номеру свидетельства.
- `GET /api/v1/resolve/vri/{vri_id}` — возвращает краткие сведения и строку эталона.
- `POST /api/v1/resolve/vri-details-by-excel` — принимает Excel со списком сертификатов, пакетно ищет `vri_id` и детали.

### Методики и владельцы
- `GET /api/v1/methodologies` и `GET /api/v1/owners` возвращают сохранённые записи (для UI/служебных нужд).

## Формат входных Excel
- `manometers_file`: минимум столбцы `Обозначение СИ`, `Заводской номер`, `Методика поверки`, `Свидетельство о поверке`, `Дата поверки`, `Владелец СИ`. Дополнительные поля (`Модификация`, `Прочие сведения`, `Температура`, `Давление`, `Влажность`) делают протокол полнее.
- `db_file`: заголовок в 5‑й строке (как в официальных реестровых выгрузках), данные с 6‑й строки. Обязательно наличие колонок из `REGISTRY_SERIAL_KEYS` (см. `app/services/registry_ingest.py`).
- Примеры лежат в `data/input/` и используются в автотестах.

## Каталоги артефактов
- `exports/` — основная папка с PDF; вложенные директории типа `PDF Манометры 06` создаются автоматически.
- `output/` — временные файлы (HTML, CSV), которые можно удалять вручную.
- `data/signatures/` — изображения подписей, подхватываются `app/utils/signatures.py`.
- `pgdata/` — volume Postgres внутри Docker Compose.

## Тестирование и качество
- Юнит/интеграционные тесты: `uv run pytest -q`
- Покрытие: `uv run pytest --cov=app`
- Проверка стиля: `uv run ruff check .`
- Форматирование: `uv run ruff format .` (или `uv run black .` — опционально)
- Пре-коммиты: `pip install pre-commit && pre-commit install`

## Типовой рабочий процесс
1. Обновить зависимости (`uv sync`) и браузер Playwright после изменения `uv.lock`.
2. Заполнить `.env`, поднять Postgres (локально или через Docker).
3. Импортировать свежую выгрузку БД (`/registry/import`) и Excel с приборами (`/protocols/manometers/pdf-files`).
4. Проверить `exports/PDF …` — папка содержит готовые протоколы.

## Troubleshooting
- **Playwright падает с `Executable doesn't exist`** — запустите `uv run playwright install --with-deps chromium` (локально) или пересоберите контейнер.
- **Порт 5432 занят** — docker‑compose уже перенесён на `15432`. Если нужно другое значение, измените `docker-compose.yml` и `.env`.
- **Аршин отвечает медленно** — увеличьте `ARSHIN_TIMEOUT` и уменьшите `ARSHIN_CONCURRENCY` в `.env`.
- **Нет доступа к PDF** — убедитесь, что у пользователя есть права на каталог `exports/`; Docker создаёт volume автоматически.
- **Сборка падает на миграциях** — проверьте `DATABASE_URL` и подключение Postgres; `docker-entrypoint.sh` выполняет `uv run alembic upgrade head`.

## Развитие и миграции
- Новая миграция: `uv run alembic revision --autogenerate -m "feat: ..."`
- Применение миграций: `uv run alembic upgrade head`
- Наполнение справочников: `uv run python -m app.db.seed`
- При обновлении `pyproject.toml` не забудьте регенерировать `uv.lock`: `uv lock`.

## Полезные ссылки
- **AGENTS.md** — проектные правила и чек‑листы.
- **data/input/** — эталонные Excel для тестовых запусков и curl‑примеров.
- **tests/** — см. реализацию моков Arshin (`respx`) и примеры использования.
