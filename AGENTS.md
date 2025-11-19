# Агентная архитектура Metrologenerator

Документ фиксирует реальные агенты сервиса формирования протоколов поверки: их роли, границы, зависимости и характер обработки ошибок. Его цель — чтобы новый разработчик видел, какие модули за что отвечают и как они стыкуются друг с другом.

## Ключевые сущности и артефакты
- **ProtocolContextItem (`app/schemas/protocol.py`)** — единый контракт между сборщиком контекста и слоями экспорта. Содержит исходный сертификат, `vri_id`, подготовленный `context`, сырой ответ Аршина и поле `error`.
- **Реляционные модели и репозитории (`app/db/models.py`, `app/db/repositories`)** — Owners/Methodologies/VerificationRegistryEntry/Etalon*/Protocol. Репозитории навешивают нормы: нормализация алиасов, idempotent upsert, деактивация устаревших записей.
- **Аршин-пейлоады (`app/services/arshin_client.py`)** — ответы `fetch_vri_*` и `resolve_etalon_*`, кешируемые в `TTLCache` (`app/services/cache.py`) для снижения нагрузки.
- **Excel-данные (`app/utils/excel.py`)** — чтение строк через `read_rows_as_dicts`/`read_rows_with_required_headers`, извлечение сертификатов (`extract_certificate_number`) и серийных номеров.
- **Шаблонный слой (`app/services/templates.py`, `app/services/generators/*`, `app/templates/*.html`)** — `resolve_template_id` + `TableGenerator` → сформированная таблица, далее Jinja2/Playwright превращают контекст в HTML/PDF.

## Агентные контуры

### 1. FastAPI gateway
- **Файлы:** `app/main.py`, `app/api/routes/*.py`, `app/api/deps.py`.
- **Роль и зависимости:** поднимает FastAPI-приложение, выполняет lifespan-сид (`seed_from_config`), пробрасывает роутеры, создаёт зависимости: на каждый запрос выделяется `httpx.AsyncClient` с таймаутами/лимитами и `AsyncSession`; `get_semaphore` даёт глобальный `asyncio.Semaphore` для исходящих запросов.
- **Триггеры/жизненный цикл:** HTTP вызовы `/api/v1/*` — от справочников до генерации PDF. Каждый запрос асинхронен, ресурсы высвобождаются по завершении.
- **Границы и ошибки:** бизнес-логика отсутствует. Роутеры валидируют вход, некорректные данные → `HTTPException 4xx`, а необработанные ошибки фиксируются и возвращаются как 5xx. Асинхронность обеспечивает FastAPI + asyncio/SQLAlchemy.

### 2. Arshin resolve agent
- **Файлы:** `app/api/routes/arshin.py`, `app/services/arshin_client.py`, `app/services/cache.py`.
- **Роль:** поиск `vri_id`, подробностей поверки и свидетельств эталонов. Публичные ручки: `GET /vri-id`, `GET /vri/{id}`, `POST /vri-details-by-excel`.
- **Поведение:** `_request_json` выполняет GET с экспоненциальным бэкоффом, джиттером, повторными попытками для 429/5xx. `fetch_vri_id_by_certificate`, `fetch_vri_details` и `resolve_etalon_certs_from_details` используют общий `TTLCache` и `asyncio.Semaphore` из `get_semaphore` для ограничения параллельности.
- **Ошибки и границы:** ввод валидируется (пустой cert/vri_id → 400). HTTP ошибки логгируются через Loguru и пробрасываются, Excel-эндпоинт возвращает per-row `error`. Сервис только нормализует и доставляет данные Аршина — не пишет их в БД.

### 3. Registry intake agent
- **Файлы:** `app/api/routes/registry.py`, `app/services/registry_ingest.py`, `app/cli.py`.
- **Роль:** загрузка выгрузок реестра поверок, нормализация строк до `VerificationRegistryEntry` и обогащение справочников.
- **Триггеры:** HTTP POST `/api/v1/registry/import` и CLI `python -m app.cli import-registry <file>` (с параметрами листа/заголовков/типа прибора).
- **Поведение:** `read_rows_with_required_headers` подбирает лист с колонками серийных номеров → `ingest_registry_rows` нормализует владельцев/методики/серийники, вызывает `RegistryRepository.upsert_entry`, деактивирует предыдущие записи источника, дополнительно вызывает `ensure_owner`/`ensure_methodology` для справочников. CLI использует те же функции через `get_sessionmaker`.
- **Ошибки и границы:** пустые файлы или отсутствие нужных колонок → `HTTP 400`/`ValueError`. Агент не строит протоколы — только поддерживает состояние реестра.

### 4. Protocol assembly agent
- **Файлы:** `app/api/routes/protocols.py`, `app/services/protocol_builder.py`, `app/services/mappings.py`, `app/services/generators/*`, `app/services/templates.py`, `app/utils/signatures.py`.
- **Роль:** собрать полный `ProtocolContextItem` из Excel, Аршина и локальной БД, а затем подготовить HTML/PDF.
- **Пайплайн:**
  1. Роутеры (`/context-by-excel`, `/html-by-excel`, `/controllers|manometers/pdf-files`) читают Excel (`read_rows_as_dicts`).
  2. `extract_certificate_number` → `fetch_vri_id_by_certificate` → `fetch_vri_details` и `find_etalon_certificates` добавляют сетевые данные. Для массовых PDF `_build_context_from_db` подбирает записи `VerificationRegistryEntry`, учитывает режим строгого совпадения сертификата и автоподстановку названий приборов.
  3. `build_protocol_context` резолвит владельцев/ИНН (`resolve_owner_and_inn`), методики (`resolve_methodology` + загрузка точек), считает диапазоны/допуски, добавляет сигнатуры (`get_signature_render`), таблицы (`TableGenerator` из `app/services/generators`) и метаданные (`make_protocol_number`, `suggest_filename`).
  4. `_build_contexts_concurrently` запускает обработку строк с ограничением `settings.PROTOCOL_BUILD_CONCURRENCY`; `manometers_pdf_files` задействует `_retry_context_rows` с `settings.PROTOCOL_RETRY_*` для 429/сетевых ошибок. Каждый воркер получает собственный `AsyncSession` через `_make_worker_session_factory`, чтобы избежать конфликтов flush.
- **Ошибки и границы:** все проблемы фиксируются в `ProtocolContextItem.error` (например, `serial number is empty`, `owner INN not found`). Роутеры агрегируют ошибки и продолжают остальные строки; критические ситуации в HTML/PDF ручках → `HTTP 400/502`. Агент отвечает только за подготовку контекста и файлов, не хранит результаты в БД.

### 5. Rendering & export agent
- **Файлы:** `app/services/html_renderer.py`, `app/services/pdf.py`, `app/templates/*.html`, `app/utils/paths.py`, экспортные куски `app/api/routes/protocols.py`.
- **Роль:** превратить контекст в HTML/PDF и сохранить на диск.
- **Поведение:** `render_protocol_html` выбирает шаблон через `resolve_template_id`, использует `Jinja2Templates` с фильтром `fmt2` и StrictUndefined. `html_to_pdf_bytes` рендерит PDF через Playwright Chromium; если браузер недоступен, возвращает `None`, что превращается в `pdf generation unavailable` и при полном фейле → `HTTP 500`.
- **Файловые операции:** `_exports_folder_label`, `get_named_exports_dir`, `get_output_dir`, `_unique_output_path` и `sanitize_filename` гарантируют безопасные каталоги (`PDF Манометры 04`, и т.п.) и уникальные имена (`protocol(1).pdf`). Контроллеры/манометры подбирают месяц из имени выгрузки, ведут логи прогресса и собирают списки ошибок/сохранённых путей.

### 6. Data steward agent
- **Файлы:** `app/db/*`, `app/services/mappings.py`, `app/api/routes/methodologies.py`, `app/api/routes/owners.py`, `scripts/bootstrap_database.py`, `app/db/seed.py`.
- **Роль:** поддержка справочников владельцев/методик/эталонов и непротиворечивая нормализация алиасов.
- **Поведение:**
  - `ensure_owner`/`ensure_methodology` создают записи, подтягивая ИНН/алиасы из `data/*.json`, нормализуют кавычки (`normalize_owner_alias`), дозаполняют пустые поля.
  - CRUD-роуты `/api/v1/owners` и `/api/v1/methodologies` позволяют операторам управлять сущностями, автоматически классифицируя точки (`MethodologyPointType`).
  - `scripts/bootstrap_database.py` проверяет PostgreSQL, при необходимости создаёт базу, запускает `alembic upgrade head`, затем `seed_from_config` заполняет справочники.
- **Границы:** не выполняет сетевые вызовы и генерацию протоколов, а гарантирует корректность справочных данных.

### 7. Automation & quality agents
- **Файлы:** `scripts/run_quality_checks.py`, `scripts/import_verification_methods.py`, `tests/`, `app/cli.py`.
- **Роль:** обеспечить качество и массовые операции.
- **Поведение:**
  - `run_quality_checks.py` подгружает `.env`, проверяет `DATABASE_URL`, прогоняет Ruff format/lint (с автопочинкой по желанию) и pytest.
  - `import_verification_methods.py` импортирует JSON выгрузку методик, создаёт точки (`MethodologyPointPayload`) и алиасы.
  - `app/cli.py import-registry` предоставляет CLI-обёртку над реестровым агентом.
  - Тесты используют `pytest-asyncio` и `respx` для моков Аршин/HTTP.
- **Ошибки:** скрипты печатают прогресс и возвращают ненулевые коды при сбоях; импорт методик пропускает записи без кода/точек.

### 8. Support & observability
- **Файлы:** `app/core/config.py`, `app/core/logging.py`, `app/api/deps.py`, `app/services/cache.py`, `app/utils/excel.py`, `app/utils/normalization.py`, `app/utils/signatures.py`, `app/utils/paths.py`.
- **Роль:** общесистемные сервисы — конфигурация, логирование, TTL-кеш, нормализация, генерация подписей и путей.
- **Поведение:**
  - `Settings` читает `.env`, задаёт таймауты, лимиты, директории экспорта и параметры повторов для протоколов.
  - `setup_logging` заменяет loguru-синк на единый формат.
  - `get_http_client` и `get_semaphore` управляют pooled HTTP клиентами и глобальной конкуренцией.
  - `TTLCache` (15 минут, 4096 записей) используется Аршин-агентом; `normalize_serial`/`sanitize_filename`/`get_named_exports_dir` приводят данные к безопасным ключам/путям.
  - `get_signature_render` случайно подбирает подписи по имени поверителя, добавляя стили в контекст.

## Типовые сценарии взаимодействия
1. **Excel → контекст (`/api/v1/protocols/context-by-excel`)**: FastAPI читает Excel, Arshin-agent ищет `vri_id` + детали, Protocol assembly строит `ProtocolContextItem`, ошибки остаются в `error`. Успешные строки дополняются `protocol_number`, шаблонные поля готовят Rendering-слой.
2. **Контроллеры/манометры → PDF (`/api/v1/protocols/controllers|manometers/pdf-files`)**: по желанию обновляется реестр (`ingest_registry_rows`), затем для каждой строки `_build_context_from_db` собирает контекст, Rendering агент формирует HTML → PDF, сохраняет файлы через `get_named_exports_dir`, возвращает список путей и ошибок. При отсутствии Playwright каждый элемент фиксирует `pdf generation unavailable` и итоговая ручка отвечает 500, если не удалось сохранить ни один файл.
3. **HTML предпросмотр (`/api/v1/protocols/html-by-excel`)**: на основе Excel-строки и (опционально) свежего реестра строится одиночный контекст, рендерится HTML, сохраняется в `output/` и возвращается пользователю. Ошибки сборки контекста → `502`.
4. **Импорт реестра/справочников (HTTP или CLI)**: `import_registry_file` и `app/cli import-registry` приводят Excel к `VerificationRegistryEntry`, создают владельцев/методики при необходимости и деактивируют старые записи источника. `scripts/import_verification_methods.py` расширяет методики из JSON, `bootstrap_database.py` применяет миграции.

## Изменения относительно предыдущей версии
- Добавлены уточнения по конкуренции (`PROTOCOL_BUILD_CONCURRENCY`, `_retry_context_rows`), изоляции `AsyncSession` и правилам повторов при генерации массовых PDF.
- Задокументированы ручки `html-by-excel`, `controllers/manometers/pdf-files` и сценарии сохранения файлов (уникальные имена, выбор директорий, реакция на отсутствие Playwright).
- Уточнены роли Registry intake (деактивация записей, `ensure_owner`/`ensure_methodology`) и Data steward (bootstrap, CRUD, автоалиасы) агентов.
- Добавлены Automation & quality инструменты (CLI import, run_quality_checks, импорт методик) и связанные зависимости.
- Раздел «Типовые сценарии» расширен HTML предпросмотром и деталями обработки ошибок.
