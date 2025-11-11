# Агентная архитектура Metrologenerator

Документ описывает реальные компоненты («агенты») сервиса генерации протоколов поверки. В нём зафиксированы роли модулей, их границы ответственности, точки интеграции и особенности обработки ошибок. Старое содержимое с общими правилами удалено и заменено архитектурным обзором.

## Ключевые сущности и артефакты
- **ProtocolContextItem (`app/schemas/protocol.py`)** — контракт, которым обмениваются сборщики контекста и слои экспорта. Содержит сертификат, `vri_id`, файл и полный контекст.
- **SQLAlchemy-модели (`app/db/models.py`)** — Owners, Methodologies, VerificationRegistryEntry, Etalon* и Protocol. Репозитории в `app/db/repositories` навешивают бизнес-правила (нормализация алиасов, idempotent upsert).
- **Аршин-пейлоады** — ответы `fetch_vri_*` и `resolve_etalon_*` из `app/services/arshin_client.py`, кешируемые в `TTLCache`.
- **Excel-данные** — строки, полученные через `app/utils/excel.py` (`read_rows_as_dicts`, `read_rows_with_required_headers`, `extract_certificate_number`).
- **Шаблоны (`app/services/templates.py`, `app/templates/*.html`)** и генераторы таблиц (`app/services/generators/*`). Связываются через `resolve_template_id` и `get_by_template`.

## Агентные контуры

### 1. FastAPI gateway
- **Файлы:** `app/main.py`, `app/api/routes/*.py`, `app/api/deps.py`.
- **Роль:** точка входа HTTP API. Настраивает lifespan-хук для автосида (`seed_from_config`), подключает роутеры, создаёт зависимости (HTTP-клиент c таймаутами и глобальный семафор, `AsyncSession`).
- **Триггеры:** HTTP запросы. Например, `/api/v1/protocols/context-by-excel`, `/api/v1/resolve/vri-id`, `/api/v1/registry/import`.
- **Границы:** не содержит бизнес-логики — делегирует в сервисы. Ошибки валидации переводятся в `HTTPException`. Асинхронность обеспечивается FastAPI + `asyncio`.

### 2. Arshin resolve agent
- **Файлы:** `app/api/routes/arshin.py`, `app/services/arshin_client.py`, `app/services/cache.py`.
- **Роль:** поиск `vri_id`, деталей поверки и свидетельств эталонов через eAPI Аршин.
- **Поведение:** `_request_json` выполняет get-запросы с экспоненциальным бэкоффом, джиттером и повторными попытками для статусов 429/5xx. Ограничение параллельности — общий `asyncio.Semaphore` из `get_semaphore`.
- **Границы:** сервис отвечает только за сетевые вызовы/нормализацию; хранение данных остаётся на других слоях.
- **Обработка ошибок:** HTTP ошибки логируются через `loguru`, пробрасываются в роутер, который возвращает 4xx/5xx. Сетевые ошибки превращаются в списки с `error` в выдаче Excel-эндпоинтов.
- **Пример:** `/api/v1/resolve/vri-details-by-excel` — читает сертификаты из загруженного Excel, параллельно ищет `vri_id`, подтягивает `fetch_vri_details`, упаковывает список результатов.

### 3. Registry intake agent
- **Файлы:** `app/api/routes/registry.py`, `app/services/registry_ingest.py`, `app/cli.py`.
- **Роль:** загрузка выгрузок реестра поверок и нормализация их до `VerificationRegistryEntry`.
- **Триггеры:** HTTP POST `/api/v1/registry/import` или CLI-команда `python -m app.cli import-registry <file>`.
- **Алгоритм:** `read_rows_with_required_headers` ищет лист с колонками заводских номеров → `ingest_registry_rows` нормализует поля (владельцы, методики, даты, серийные номера) и вызывает `RegistryRepository.upsert_entry`.
- **Границы:** агент управляет только данными реестра; всё, что связано с контекстом протокола, остаётся в Protocol Assembly.
- **Ошибки:** пустые файлы/неподдерживаемые шапки → HTTP 400/`ValueError`. При успешной обработке репозиторий деактивирует старые записи того же источника.

### 4. Protocol assembly agent
- **Файлы:** `app/api/routes/protocols.py`, `app/services/protocol_builder.py`, `app/services/mappings.py`, `app/services/generators/*`, `app/services/templates.py`, `app/utils/signatures.py`.
- **Роль:** собрать полный контекст протокола на основе Excel-строк, данных Аршина и локальной БД.
- **Пайплайн:**  
  1. Роутеры читают Excel (`read_rows_as_dicts`) и по каждой строке запускают `process_row`.  
  2. Сертификат → `fetch_vri_id_by_certificate` → `fetch_vri_details`.  
  3. `find_etalon_certificates` подбирает эталонные свидетельства.  
  4. `build_protocol_context` объединяет детали, владельцев (`resolve_owner_and_inn`), методики (`resolve_methodology`), расчёт диапазонов, допуска и эталонных строк.  
  5. `TableGenerator` подготавливает строку таблицы (давление или контроллеры).  
  6. Контекст дополняется авто-номером (`make_protocol_number`), сигнатурой (`get_signature_render`), рекомендациями по имени файла (`suggest_filename`).
- **Границы:** агент отвечает за полностью подготовленный контекст (без итогового рендера). Сторонние зависимости: HTTP клиент, `AsyncSession`. Для массовых операций `controllers_pdf_files`/`manometers_pdf_files` создают собственный `async_sessionmaker`, чтобы каждый воркер имел отдельную сессию и не блокировал flush других задач.
- **Ошибки:** `ProtocolContextItem.error` фиксирует проблемы («certificate number is empty», `owner INN not found for "..."`, `http error: ...`). Роутеры агрегируют ошибки и продолжают работу над остальными строками; при пустом `owner_inn` экспорт намеренно прерывается для конкретной строки, чтобы не выпускать протоколы без юридических реквизитов.
- **Триггеры:** `/context-by-excel`, `/html-by-excel`, `/controllers/pdf-files`, `/manometers/pdf-files`.

### 5. Rendering & export agent
- **Файлы:** `app/services/html_renderer.py`, `app/services/pdf.py`, `app/templates/*.html`, `app/utils/paths.py`.
- **Роль:** превращение контекста в HTML/PDF и сохранение на диск.
- **HTML:** Jinja2 (`Jinja2Templates`) с кастомными фильтрами (`fmt2`). Выбор шаблона идёт через `resolve_template_id`.
- **PDF:** `html_to_pdf_bytes` запускает Playwright Chromium; при отсутствии браузера возвращает `None`, а вызывающий код фиксирует ошибку и прекращает генерацию.
- **Файловые операции:** `get_named_exports_dir`, `get_output_dir` и `_unique_output_path` гарантируют уникальные и безопасные пути, `sanitize_filename` защищает от недопустимых символов.
- **Сценарии:** массовые генерации `/controllers/pdf-files` и `/manometers/pdf-files` создают подпапки вида `PDF Манометры 04`, сохраняют PDF и возвращают список путей + ошибки.

### 6. Data steward agent
- **Файлы:** `app/db/*`, `app/services/mappings.py`, `app/api/routes/methodologies.py`, `app/api/routes/owners.py`, `scripts/bootstrap_database.py`, `app/db/seed.py`.
- **Роль:** обслуживание справочников (владельцы, методики, эталоны), обеспечение непротиворечивых алиасов и сидов.
- **Поведение:**  
  - `ensure_owner`/`ensure_methodology` создают записи, попутно вшивая алиасы/точки методик из `data/*.json`. Для владельцев автоматически подтягиваются ИНН и дополнительные алиасы (включая варианты с «ёлочками»), а пустые поля в существующих строках дозаписываются при первом обращении.  
  - `/api/v1/methodologies` и `/api/v1/owners` позволяют CRUD-операции для операторов.  
  - `bootstrap_database.py` проверяет БД, катает миграции (`alembic upgrade head`) и стопит, если не может создать базу.
- **Границы:** этот агент не лезет в сетевые вызовы и генерацию протоколов; он гарантирует, что любое имя/методика приведены к канонической форме.

### 7. Automation & quality agents
- **Файлы:** `scripts/run_quality_checks.py`, `tests/`, `scripts/import_verification_methods.py`.
- **Роль:** поддержка качества и массовых операций.  
  - `run_quality_checks.py` прогоняет Ruff + pytest, при необходимости пытается автофиксить.  
  - `import_verification_methods.py` завозит новые методики из JSON, создавая точки и алиасы.  
  - Тесты используют `pytest-asyncio` и `respx` для моков Аршин.

### 8. Support & observability
- **Файлы:** `app/core/config.py`, `app/core/logging.py`, `app/services/cache.py`, `app/utils/normalization.py`, `app/utils/signatures.py`.
- **Роль:** общесистемные сервисы — настройка, логирование, TTL-кеш, нормализация серийных номеров/имен, отрисовка подписей.
- **Особенности:**  
  - `Settings` подхватывает `.env`, экспортирует таймауты/конкурентность.  
  - `setup_logging` заменяет дефолт Loguru-синк для единообразного формата.  
  - `TTLCache` (15 минут) используется Аршин-агентом для снижения нагрузки.  
  - `normalize_serial`/`normalize_owner_alias` обеспечивают одинаковые ключи в базе; нормализация удаляет типографские кавычки, поэтому «ООО „…“» и `ООО "…"` считаются одним владельцем.

## Типовые сценарии взаимодействия
1. **Excel → контекст:**  
   Пользователь загружает шаблон на `/api/v1/protocols/context-by-excel`. Gateway распараллеливает строки, Arshin-agent ищет `vri_id` и детали, Protocol Assembly строит `ProtocolContextItem`. Ответ — JSON с контекстами и ошибками по строкам.
2. **Контроллеры → PDF:**  
   `/api/v1/protocols/controllers/pdf-files` получает Excel с приборами + (опционально) выгрузку реестра. Registry intake при необходимости обновляет БД, далее Protocol Assembly забирает актуальные записи, Rendering agent генерирует HTML → PDF, сохраняет файлы и возвращает пути + ошибки. При отсутствии Playwright все элементы падают с `pdf generation unavailable`.
3. **Импорт справочников:**  
   `/api/v1/registry/import` или `python -m app.cli import-registry file.xlsx` загружает новые данные. Registry agent деактивирует предыдущие записи того же источника, Data steward гарантирует, что владельцы/методики заведены, что позволяет Protocol Assembly позднее сопоставлять записи по `normalized_serial`.

## Изменения относительно предыдущей версии
- Документ больше не описывает общие правила коммитов/линтов — эта информация уже есть в `README.md` и `scripts/run_quality_checks.py`.
- Добавлены восемь агентных контуров с перечислением модулей, обязанностей и способов обработки ошибок.
- Впервые задокументированы типовые end-to-end сценарии (контекст по Excel, массовое формирование PDF, импорт реестра).
- Добавлена явная связь между поддерживающими сервисами (кеш, сигнатуры, нормализация) и боевыми агентами, чтобы новым разработчикам было понятно, откуда брать зависимости.
- Обновлена схема Protocol Assembly: контексты строятся с ограничением `PROTOCOL_BUILD_CONCURRENCY`, а каждый воркер открывает собственную `AsyncSession`, чтобы не возникало конфликтов flush. Ошибки с отсутствующим ИНН фиксируются на уровне контекста.
- Data Steward теперь описывает автоматическое дозаполнение владельцев из `data/orgs.json` (алиасы, ИНН, нормализация кавычек), что важно для соответствия юридическим требованиям.
