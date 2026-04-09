# Metrologenerator

FastAPI‑сервис для автоматизации подготовки протоколов поверки манометров и выгрузок из Аршина. Приложение принимает Excel‑шаблоны, находит сведения в реестре, подтягивает детали из API Аршин и генерирует HTML/PDF протоколы с заполненными таблицами. В текущей версии у проекта появился отдельный frontend в стиле `metroLog`: с темами, пользователями, авторизацией, мониторингом и графическим экраном генерации.

## Возможности
- Загрузка Excel с приборами (`/api/v1/protocols/context-by-excel`, `/manometers/pdf-files`) и автоматическое построение контекста протокола.
- Импорт выгрузок БД реестра через `/api/v1/registry/import` с нормализацией владельцев, методик и номеров свидетельств.
- Вызовы к Аршину (`/api/v1/resolve/*`) для поиска `vri_id`, сведений об эталонах и сертификатов.
- Хранение справочников методик/владельцев в Postgres с автоматическим наполнением при старте приложения.
- Генерация PDF средствами Playwright (Chromium) и сохранение файлов в `exports/`.
- Пользовательский контур: bootstrap‑admin, логин, профили, роли, временные пароли, темы интерфейса.
- Графический интерфейс `frontend/` на React/Vite/Tailwind с shell-структурой, похожей на `metroLog`.
- Системные ручки `/api/v1/system/*` для истории экспортов и открытия сохранённых PDF прямо из UI.

## Технологический стек
- Python 3.13, FastAPI, SQLAlchemy 2, Alembic.
- Frontend: React 19, Vite, Tailwind CSS, Zustand, React Query.
- PostgreSQL (локально можно использовать `dev.db`/SQLite, но целевой режим — Postgres).
- HTTP клиенты: `httpx`, `respx` в тестах.
- Инструменты качества: `pytest`, `pytest-asyncio`, `ruff`, `black`.
- Сборка/зависимости через `uv`, контейнеризация — Docker/Compose.

## Структура проекта
| Каталог / файл | Назначение |
| --- | --- |
| `app/api/routes/` | FastAPI‑ручки (`protocols`, `arshin`, `registry`, `methodologies`, `owners`, `auth`, `users`, `system`). |
| `app/services/` | Основная бизнес‑логика: генераторы таблиц, билдер протоколов, Playwright PDF, Arshin client. |
| `app/templates/` | HTML/Jinja2 формы протоколов (`pressure.html`, `controller_43790_12.html`). |
| `app/core/` | Настройки (`config.py`) и логирование. |
| `app/db/` | Модели SQLAlchemy, репозитории и сиды. |
| `frontend/` | React/Vite UI для генерации, мониторинга, авторизации и управления пользователями. |
| `data/` | Примеры Excel/вспомогательные данные (`data/input/*`, `data/signatures`). |
| `exports/` | Готовые PDF, создаются автоматически. |
| `output/` | Временные артефакты (HTML и т.п.). |
| `docker-entrypoint.sh` | Применяет миграции и стартует Uvicorn в контейнере. |

## Требования
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) 0.4+
- Node.js 20+ и npm (для локального frontend dev/build).
- PostgreSQL 16 (или совместимый) — для Docker используется контейнер `postgres:16-alpine`.
- Playwright Chromium (для PDF). В контейнере браузер устанавливается автоматически; локально нужно выполнить `uv run playwright install --with-deps chromium`.
- Docker + Docker Compose (опционально, для контейнерного запуска).

## Подготовка окружения (локально)
1. Склонируйте репозиторий и перейдите в каталог проекта.
2. Скопируйте `.env.example` → `.env` в корне. Укажите `DATABASE_URL`, `ARSHIN_TIMEOUT`, `ARSHIN_CONCURRENCY`, `USER_AGENT`. Для локального Postgres:
   `DATABASE_URL=postgresql+asyncpg://metrologenerator:metrologenerator@127.0.0.1:5433/metrologenerator`
   Для локального API по умолчанию используются:
   `API_HOST=127.0.0.1`
   `API_PORT=8001`
   `API_RELOAD=false`
   Для пользовательского контура также важны:
   `SECRET_KEY`
   `BOOTSTRAP_ADMIN_EMAIL`
   `BOOTSTRAP_ADMIN_PASSWORD`
   `BACKEND_CORS_ORIGINS=http://localhost:5174`
3. Установите зависимости: `uv sync`.
4. Установите frontend‑зависимости: `npm --prefix frontend install`.
5. Установите Playwright Chromium: `uv run playwright install --with-deps chromium`.
6. Примените миграции: `uv run alembic upgrade head`.
7. При необходимости заполните справочники: `uv run python -m app.db.seed` (FastAPI делает то же при старте, но команда полезна для CI).

## Запуск API (локально)
```bash
uv run metrogen
# сервис поднимется на http://127.0.0.1:8001
```

## Запуск frontend (локально)
```bash
npm run dev:frontend
# dev UI поднимется на http://127.0.0.1:5174
```

Backend и frontend работают как отдельные dev-сервера. Для production-like запуска frontend нужно собрать:

```bash
npm run build:frontend
```

После этого `frontend/dist` будет обслуживаться самим FastAPI, и UI откроется с того же хоста, что и backend.

Для симметричного локального запуска, как в `metroLog`, можно использовать:

```bash
npm run setup:local
npm run dev
```

## Docker / Compose
```bash
docker compose up --build
```
- Контейнер `db` (Postgres 16) проброшен на `localhost:5433` → `5432`.
- Контейнер `api` публикуется на хост-порт из `.env` через `API_PORT` (по умолчанию `8001`).
- Контейнер `frontend` публикуется на `FRONTEND_PORT` (по умолчанию `5174`).
- Эти порты намеренно сдвинуты относительно соседнего репозитория `metroLog` (`5432/8000/5173`), чтобы оба проекта можно было держать поднятыми одновременно.
- `docker-entrypoint.sh` внутри `api` применяет миграции и запускает Uvicorn из собранного контейнерного `.venv`, без догрузки зависимостей на старте.
- Для `api` используется отдельный Docker volume `/app/.venv`, чтобы bind-mount проекта не подмешивал хостовое виртуальное окружение в контейнер.
- Во время сборки образа выполняется `uv sync --frozen --no-dev` и `/app/.venv/bin/python -m playwright install --with-deps chromium`, поэтому PDF работает «из коробки».

Остановка: `docker compose down` (дополнительно `-v`, если нужно удалить volume `pgdata`).

## Работа с API

### Протоколы
- `POST /api/v1/protocols/context-by-excel` — принимает Excel с колонками как минимум `Обозначение СИ`, `Заводской номер`, `Методика поверки`, `Свидетельство о поверке`. Возвращает список контекстов (по одному на строку Excel) и предложенное имя файла.
- `POST /api/v1/protocols/html-by-excel` — тот же формат, но возвращает HTML первой строки (удобно для отладки шаблонов).
- `POST /api/v1/protocols/manometers/pdf-files` — основной сценарий. Параметры multipart:
  - `manometers_file`: Excel с данными поверяемых СИ.
  - `db_file` (опционально, но желательно): выгрузка из БД (начиная с 5‑й строки заголовка). Если передан, файл импортируется в базу, и протоколы получают номера/сертификаты из реестра.
  - Ответ содержит список путей к сохранённым PDF в `exports/PDF Манометры <месяц>`.
- `POST /api/v1/protocols/manometers/failed/pdf-files` — аналогичный сценарий, но для непригодных манометров (без таблицы результатов и с отметкой "НЕ соответствует" в первом пункте).

Пример запроса (контекст по Excel):
```bash
curl -X POST \
     -F "file=@data/input/Поверка манометры 06.2025.xlsm" \
     http://127.0.0.1:8001/api/v1/protocols/context-by-excel
```

### Работа с реестром
- `POST /api/v1/registry/import` — загружает Excel выгрузку, ищет заголовки из `REGISTRY_SERIAL_KEYS` и кладёт строки в таблицу `verification_registry_entries`.  
  Пример:
  ```bash
  curl -X POST \
       -F "db_file=@data/input/09\ БД.xlsx" \
       "http://127.0.0.1:8001/api/v1/registry/import?instrument_kind=manometers"
  ```

### Ручки для Аршина
- `GET /api/v1/resolve/vri-id?cert=<номер>` — ищет `vri_id` по номеру свидетельства.
- `GET /api/v1/resolve/vri/{vri_id}` — возвращает краткие сведения и строку эталона.
- `POST /api/v1/resolve/vri-details-by-excel` — принимает Excel со списком сертификатов, пакетно ищет `vri_id` и детали.

### Методики и владельцы
- `GET /api/v1/methodologies` и `GET /api/v1/owners` возвращают сохранённые записи (для UI/служебных нужд).

### Пользователи и UI
- `POST /api/v1/auth/login` — логин.
- `GET /api/v1/auth/me` — текущий пользователь.
- `PATCH /api/v1/auth/me` — профиль и пользовательские настройки.
- `POST /api/v1/auth/change-password` — смена пароля.
- `POST /api/v1/auth/test-mention-email` — тест SMTP-уведомления.
- `GET /api/v1/users` / `POST /api/v1/users` — список и создание пользователей.
- `GET /api/v1/system/status` — сводка для dashboard/monitoring UI.
- `GET /api/v1/system/export-file?path=...` — открыть сохранённый экспорт из интерфейса.

## Формат входных Excel
- `manometers_file`: минимум столбцы `Обозначение СИ`, `Заводской номер`, `Методика поверки`, `Свидетельство о поверке`, `Дата поверки`, `Владелец СИ`. Дополнительные поля (`Модификация`, `Прочие сведения`, `Температура`, `Давление`, `Влажность`) делают протокол полнее.
- `db_file`: заголовок в 5‑й строке (как в официальных реестровых выгрузках), данные с 6‑й строки. Обязательно наличие колонок из `REGISTRY_SERIAL_KEYS` (см. `app/services/registry_ingest.py`).
- Примеры лежат в `data/input/` и используются в автотестах.

## Каталоги артефактов
- `exports/` — основная папка с PDF; вложенные директории типа `PDF Манометры 06` создаются автоматически.
- `frontend/dist/` — production-сборка UI, если выполнен `npm run build:frontend`.
- `output/` — временные файлы (HTML, CSV), которые можно удалять вручную.
- `data/signatures/` — изображения подписей, подхватываются `app/utils/signatures.py`.
- `pgdata/` — volume Postgres внутри Docker Compose.

## Тестирование и качество
- Юнит/интеграционные тесты: `uv run pytest -q`
- Покрытие: `uv run pytest --cov=app`
- Проверка стиля: `uv run ruff check .`
- Форматирование: `uv run ruff format .` (или `uv run black .` — опционально)
- Frontend lint/build: `npm run lint:frontend`, `npm run build:frontend`
- Пре-коммиты: `pip install pre-commit && pre-commit install`

## Типовой рабочий процесс
1. Обновить зависимости (`uv sync`) и браузер Playwright после изменения `uv.lock`.
2. Заполнить `.env`, поднять Postgres (локально или через Docker).
3. Импортировать свежую выгрузку БД (`/registry/import`) и Excel с приборами (`/protocols/manometers/pdf-files`).
4. Проверить `exports/PDF …` — папка содержит готовые протоколы.

## Troubleshooting
- **Playwright падает с `Executable doesn't exist`** — запустите `uv run playwright install --with-deps chromium` (локально) или пересоберите контейнер.
- **Порт Postgres занят** — для `metroGen` по умолчанию используется `5433`, чтобы не конфликтовать с `metroLog`.
- **Порт API занят** — измените `API_PORT` в `.env`; локальный запуск `uv run metrogen` и `docker compose up` будут использовать этот порт на хосте.
- **Frontend не открывается через backend** — убедитесь, что выполнен `npm run build:frontend`, и в `frontend/dist` лежит `index.html`.
- **Нет логина в UI** — проверьте, что выполнены миграции и создан bootstrap‑admin из `.env`.
- **Аршин отвечает медленно** — увеличьте `ARSHIN_TIMEOUT` и уменьшите `ARSHIN_CONCURRENCY` в `.env`.
- **Нет доступа к PDF** — убедитесь, что у пользователя есть права на каталог `exports/`; Docker создаёт volume автоматически.
- **Сборка падает на миграциях** — проверьте `DATABASE_URL` и подключение Postgres; `docker-entrypoint.sh` выполняет Alembic внутри контейнерного `.venv`.
- **Контейнер пытается скачать `black`, `pathspec` или другие dev-зависимости на старте** — пересоздайте контейнеры и volume после обновления compose-конфига: `docker compose down -v && docker compose up --build`.

## Развитие и миграции
- Новая миграция: `uv run alembic revision --autogenerate -m "feat: ..."`
- Применение миграций: `uv run alembic upgrade head`
- Наполнение справочников: `uv run python -m app.db.seed`
- При обновлении `pyproject.toml` не забудьте регенерировать `uv.lock`: `uv lock`.

## Полезные ссылки
- **AGENTS.md** — проектные правила и чек‑листы.
- **data/input/** — эталонные Excel для тестовых запусков и curl‑примеров.
- **tests/** — см. реализацию моков Arshin (`respx`) и примеры использования.
