# Агентная архитектура Metrologenerator

Документ фиксирует текущее состояние агентной архитектуры сервиса генерации протоколов поверки.
Цель: дать новому разработчику рабочую карту модулей, зависимостей и поведения при ошибках.

## Область покрытия
Актуализация выполнена по всем исходным текстовым файлам репозитория:
- root-конфиги и инфраструктура (`README.md`, `pyproject.toml`, Docker/Alembic/pytest config);
- backend-код (`app/**`);
- миграции (`migrations/**`);
- служебные скрипты (`scripts/**`);
- тесты (`tests/**`);
- шаблоны (`app/templates/**`);
- справочные legacy-вложения (`data/attachments/**`) и JSON-данные (`app/data/*.json`, `data/verification_methods_*.json`).

Исключены только не-исходные артефакты: `.venv`, `.uv-env`, `__pycache__`, `output/`, `exports/`, бинарные Excel/DB.

## Ключевые сущности и контракты
- **ProtocolContextItem** (`app/schemas/protocol.py`): row-level контракт конвейера; хранит `certificate`, `vri_id`, `context`, `raw_details`, `error`.
- **VerificationRegistryEntry** (`app/db/models.py`): нормализованный снимок строки реестра (источник, серийник, документ, протокол, даты, `payload`, `is_active`, `instrument_kind`).
- **Owner / OwnerAlias**: справочник владельцев и нормализованные алиасы.
- **Methodology / MethodologyAlias / MethodologyPoint**: справочник методик, fuzzy-алиасы, структурированные пункты методики с типами (`bool|clause|custom`).
- **EtalonDevice / EtalonCertification**: выделенные сущности эталонов и их свидетельств.
- **MeasuringInstrument / Protocol**: модель связей исторических сущностей (на текущем этапе генерация протоколов идёт без обязательного сохранения Protocol в БД).
- **Arshin payloads** (`app/services/arshin_client.py`): сетевые ответы `/vri`, `/vri/{id}` и резолв эталонных свидетельств.
- **Template registry + table generators** (`app/services/templates.py`, `app/services/generators/*`): выбор шаблона и генерация табличной части.

## Сквозные зависимости
1. FastAPI endpoint принимает файл/запрос.
2. Excel parser (`app/utils/excel.py`) извлекает строки и ключевые поля.
3. Для контекстов вызывается Arshin client (`fetch_vri_id_by_certificate` -> `fetch_vri_details` -> `find_etalon_certificates`).
4. Builder (`app/services/protocol_builder.py`) объединяет Excel + Arshin + DB справочники (owners/methodologies/signatures/templates).
5. Renderer (`render_protocol_html`) формирует HTML по выбранному шаблону.
6. PDF service (`html_to_pdf_bytes`) рендерит PDF через Playwright.
7. Export helpers (`app/utils/paths.py`, `_unique_output_path`) сохраняют файлы безопасно и уникально.

## Агентные контуры

### 1. FastAPI gateway agent
- **Файлы:** `app/main.py`, `app/api/deps.py`, `app/api/routes/*.py`.
- **Цель:** предоставить HTTP-вход и DI-контейнер для сессий/HTTP-клиента/ограничения конкуренции.
- **Триггеры:** запросы на `/api/v1/*`.
- **Жизненный цикл:**
  1. Startup: `lifespan` пытается выполнить `seed_from_config`.
  2. Request: создаётся `httpx.AsyncClient` и `AsyncSession`.
  3. Завершение: ресурсы закрываются dependency-контекстом.
- **Ошибки:** входная валидация и бизнес-ошибки отдаются через `HTTPException`; startup seed errors логируются и не останавливают приложение.

### 2. Arshin resolve agent
- **Файлы:** `app/api/routes/arshin.py`, `app/services/arshin_client.py`, `app/services/cache.py`.
- **Цель:** резолв `vri_id`, получение деталей поверки, поиск свидетельств эталонов.
- **Триггеры:** `GET /api/v1/resolve/vri-id`, `GET /api/v1/resolve/vri/{id}`, `POST /api/v1/resolve/vri-details-by-excel`.
- **Жизненный цикл:**
  1. Валидация входа.
  2. `_request_json` с retry/backoff/jitter и семафором.
  3. Кеширование (TTLCache) на lookup-операциях.
  4. Для архивных свидетельств сначала пробуется `year` из номера сертификата, затем запрос без `year`.
  5. Для эталонов перебираются варианты фильтров/годов и пагинация `/vri`.
- **Ошибки:** retry только на `429/5xx`; terminal HTTP/transport ошибки логируются; excel-ручка возвращает per-row `error` без падения всего запроса.

### 3. Registry intake agent
- **Файлы:** `app/api/routes/registry.py`, `app/services/registry_ingest.py`, `app/cli.py`.
- **Цель:** импортировать выгрузки реестра поверок в `verification_registry_entries` и синхронизировать справочники.
- **Триггеры:**
  - HTTP: `POST /api/v1/registry/import`;
  - CLI: `python -m app.cli import-registry <file>`.
- **Жизненный цикл:**
  1. Поиск листа с требуемыми заголовками (`REGISTRY_SERIAL_KEYS`).
  2. `deactivate_for_source` для предыдущей версии источника.
  3. Upsert строк (`upsert_entry`) с нормализацией дат/серийников/номера протокола.
  4. `ensure_owner` и `ensure_methodology` для enrichment справочников.
- **Ошибки:** пустой/неподходящий файл -> `HTTP 400` или `ValueError`; импорт логирует прогресс батчами.

### 4. Protocol orchestration agent
- **Файлы:** `app/api/routes/protocols.py`.
- **Цель:** оркестровать конвейеры контекста/HTML/PDF для разных типов приборов.
- **Триггеры и маршруты:**
  - `/context-by-excel`;
  - `/html-by-excel`;
  - `/controllers/pdf-files`;
  - `/manometers/pdf-files`;
  - `/manometers/failed/pdf-files`;
  - `/manometers/html-preview`;
  - `/thermometers/pdf-files`;
  - `/thermometers/html-preview`.
- **Ключевая логика:**
  - асинхронная сборка строк (в массовых сценариях через `_build_contexts_concurrently`);
  - retry row-level ошибок через `_retry_context_rows` (маркеры: `retryable status`, `transport error`, `timeout`);
  - изоляция воркеров по SQLAlchemy session (`_make_worker_session_factory`);
  - выбор DB row по серийнику/дате (`_select_registry_entry`);
  - режимы строгой сверки сертификата:
    - `manometers`, `thermometers` -> `strict_certificate_match=True`;
    - `controllers` -> `strict_certificate_match=False`.
- **Ошибки:**
  - row-level ошибки сохраняются в `ProtocolContextItem.error` и не прерывают batch;
  - в HTML-preview при невозможности собрать контекст -> `HTTP 502`;
  - при отсутствии Playwright и нуле сохранённых PDF -> `HTTP 500`.

### 5. Protocol context assembly agent
- **Файлы:** `app/services/protocol_builder.py`, `app/services/mappings.py`, `app/services/generators/*`, `app/services/templates.py`, `app/utils/signatures.py`.
- **Цель:** построить полноценный `context` для шаблона.
- **Жизненный цикл:**
  1. Нормализация owner/methodology (через DB + JSON seeds).
  2. Парсинг диапазонов/единиц из Excel и fallback из Arshin `additional_info`.
  3. Сопоставление всех эталонов и свидетельств (включая multi-etalon).
  4. Выбор шаблона (`pressure_common`, `controller_43790_12`, `rtd_platinum`).
  5. Генерация таблиц и derived-полей (`mpi_years`, technical metrics RTD).
  6. Подстановка подписей поверителя/стажёра.
- **Критичная граница:** builder не пишет данные в БД.
- **Ошибки:**
  - при отсутствии ИНН владельца бросается `ValueError("owner INN not found ...")`;
  - сетевые ошибки Arshin ловятся внешним оркестратором в `protocols.py`.

### 6. Rendering & export agent
- **Файлы:** `app/services/html_renderer.py`, `app/services/pdf.py`, `app/templates/*.html`, `app/utils/paths.py`.
- **Цель:** HTML/PDF-рендер и сохранение файлов.
- **Жизненный цикл:**
  1. Шаблон выбирается по `resolve_template_id`.
  2. Контекст нормализуется для template compatibility.
  3. HTML -> PDF через Playwright Chromium.
  4. Файл пишется в `exports/<folder>` с уникализацией имени.
- **Файловые правила:**
  - каталоги формируются через `get_named_exports_dir`;
  - массовые run-экспорты используют лейблы вида `Generation pressure|rtd|Контроллеры <MM> - <run_id>`;
  - имена файлов безопасны через `sanitize_filename` и уникализируются `_unique_output_path`.
- **Ошибки:** Playwright import failure -> `None`, дальнейшая обработка в роутере.

### 7. Data stewardship agent
- **Файлы:** `app/db/*`, `app/api/routes/owners.py`, `app/api/routes/methodologies.py`, `app/db/seed.py`, `scripts/bootstrap_database.py`, `scripts/import_verification_methods.py`.
- **Цель:** поддерживать консистентные справочники владельцев и методик.
- **Триггеры:** CRUD API, startup seed, bootstrap/import scripts.
- **Жизненный цикл:**
  - alias-нормализация и idempotent upsert;
  - auto-population алиасов/ИНН из JSON;
  - миграции + optional create DB + seed.
- **Ошибки:**
  - в API валидация точек/пустых полей -> `HTTP 400`;
  - bootstrap/import scripts завершаются ненулевым кодом при сбое.

### 8. Automation & quality agent
- **Файлы:** `scripts/run_quality_checks.py`, `tests/*`, `pytest.ini`, `.pre-commit-config.yaml`.
- **Цель:** защитить регрессии межкомпонентных контрактов.
- **Что проверяется тестами:**
  - Arshin retries/year fallback/pagination;
  - route-level orchestration и ошибки сертификатов;
  - protocol builder (range parsing, template selection, etalon merge, trainee logic);
  - registry ingest и repository normalization;
  - PDF fallback при отсутствии Playwright.

### 9. Legacy reference agent (не runtime)
- **Файлы:** `data/attachments/*.cs`, `data/attachments/*.html`.
- **Роль:** исторический C# конвейер и шаблоны для сравнения поведения.
- **Граница:** текущий Python/FastAPI runtime эти файлы не исполняет.

## Типовые сценарии взаимодействия
1. **Excel -> context (`/api/v1/protocols/context-by-excel`)**
   - Читаются строки Excel.
   - Для каждой: сертификат -> `vri_id` -> `details` -> `etalon certs`.
   - Builder формирует `context`; ошибки остаются в `ProtocolContextItem.error`.

2. **Универсальный HTML (`/api/v1/protocols/html-by-excel`)**
   - Опционально импортируется `db_file` в реестр.
   - Тип прибора определяется автоматически (`manometers|controllers|thermometers`) или через параметр.
   - Контекст строится через DB-поиск или fallback к Excel-only pipeline.

3. **Массовый PDF по БД (`controllers|manometers|thermometers/pdf-files`)**
   - Опциональный реимпорт реестра.
   - Контексты строятся конкурентно; для manometers/thermometers есть дополнительные retries.
   - Экспортируются PDF и возвращаются `files + errors`.

4. **Брак манометров (`/manometers/failed/pdf-files`)**
   - Используется тот же контекст, но перед рендером выставляется `verification_failed` и скрывается таблица результатов.

5. **Локальные preview (`/manometers/html-preview`, `/thermometers/html-preview`)**
   - Выбирается одна строка по `row`.
   - HTML возвращается в ответе и сохраняется в `output/`.

6. **Импорт реестра (HTTP/CLI)**
   - Строки приводятся к `VerificationRegistryEntry`.
   - Старые записи того же источника деактивируются.
   - Справочники owners/methodologies дозаполняются автоматически.

## Границы ответственности
- `arshin_client` не пишет в БД.
- `registry_ingest` не генерирует HTML/PDF.
- `protocol_builder` не отвечает за файловую систему и HTTP-ответы.
- `html_renderer/pdf` не знают о бизнес-валидации реестра/сертификатов.
- `tests` фиксируют контракты, но не участвуют в runtime.

## Изменения относительно предыдущей версии
- Добавлены и описаны термометрические ветки:
  - `POST /api/v1/protocols/thermometers/pdf-files`;
  - `POST /api/v1/protocols/thermometers/html-preview`.
- Добавлен отдельный сценарий `POST /api/v1/protocols/manometers/failed/pdf-files` (браковочные протоколы).
- Уточнена фактическая карта strict certificate match: `manometers/thermometers=true`, `controllers=false`.
- Уточнена модель retries в массовой генерации: row-level retry по маркерам транспортных/лимитных ошибок.
- Зафиксированы текущие export naming conventions (`Generation <label> <month> - <run_id>`).
- Добавлен раздел про `data/attachments/*` как legacy-reference (неисполняемый контур).
- Уточнено, что builder валидирует обязательность ИНН владельца и может завершаться `ValueError`.
