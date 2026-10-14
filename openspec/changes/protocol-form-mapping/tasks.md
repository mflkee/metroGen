# Tasks

## 1. Модель и миграция

- [x] 1.1 Модель `TemplateBindingRule` (`app/db/models.py`): `instrument_kind`, `match_field`, `match_value`, `template_id`, `priority`, `is_active`, таймстемпы; индекс по `instrument_kind`.
- [x] 1.2 `Methodology.template_id: str | None`.
- [x] 1.3 Alembic-миграция `20261014_000009_template_binding_rules` (таблица + колонка + индекс).
- [x] 1.4 Сид правил, повторяющих эвристики (приоритеты 10/20/25/28/30/35/36 воспроизводят порядок `resolve_template_id`); идемпотентность обеспечена миграцией.

## 2. Разрешение формы

- [x] 2.1 `app/services/template_rules.py`: `resolve_form(...)` — override → правила (по приоритету, с фильтром по типу прибора, если он известен) → форма методики → эвристики. Реализовано с коротким кэшем (30 с) и `invalidate()` после правок, чтобы не делать по два запроса на строку в массовой генерации.
- [x] 2.2 `app/services/protocol_builder.py`: `build_context` принимает `session` и `_template_override` из строки, вызывает `resolve_form`; в контекст пишутся `template_id`, `template_source`, `template_rule_id`. `build_protocol_context` прокидывает сессию в обоих путях.
- [x] 2.3 `app/services/html_renderer.py`: рендер использует `context["template_id"]` и `TEMPLATES[...]["path"]`; пересчёт эвристиками — только фоллбэк, с логированием.
- [x] 2.4 Тесты разрешения и рендера: `tests/test_template_rules.py` — override, правило важнее эвристики, приоритет, AND по ключевым словам, форма методики, fallback, «рендер рендерит вычисленную форму», фоллбэк без `template_id`. *(прогон — на сервере)*

## 3. Под-формы уровнемеров

- [x] 3.1 В `TEMPLATES` добавлены `level_meter_two_tables` и `level_meter_current_output` (оба рендерятся `level_meter.html`); зарегистрированы в `generators/registry.py`.
- [x] 3.2 `generators/level_meter.py` выбирает набор таблиц по `template_id`; номер типа — только фоллбэк для базовой формы.
- [x] 3.3 Сид-правила `86065-22` → `level_meter_two_tables`, `47249-16` → `level_meter_current_output`; тесты под-форм и фоллбэка по номеру типа.

## 4. API

- [x] 4.1 `GET /api/v1/templates` — каталог форм + допустимые типы приборов и условия; роутер зарегистрирован в `app/main.py`.
- [x] 4.2 CRUD правил: `GET/POST /template-rules`, `PATCH/DELETE /template-rules/{id}` с валидацией `template_id`/`match_field`/`instrument_kind`; после каждой правки `template_rules.invalidate()`.
- [x] 4.3 `POST /template-rules/preview` → форма + источник.
- [x] 4.4 Override формы на запуск: `POST /protocols/jobs` принимает `template_id` (валидируется по каталогу), значение кладётся в строки как `_template_override` и доходит до `resolve_form` через `_run_generation_job`/`_generate_pdf_files`.
- [x] 4.5 Тесты роутеров правил добавлены (`tests/test_reference_crud_routes.py`): каталог, CRUD, предпросмотр (правило и fallback), `400` на неизвестный `template_id`. *(прогон `pytest` — на сервере)*

## 5. Frontend

- [x] 5.1 `src/api/templates.ts`: каталог, правила, предпросмотр.
- [x] 5.2 `src/pages/AdminTemplatesPage.tsx`: раскрывающиеся правила, диалог создания/правки, включение/выключение, удаление с подтверждением, блок предпросмотра.
- [x] 5.3 Роут `/admin/templates` и пункт «Формы протоколов» в навигации (ADMINISTRATOR/DEVELOPER).
- [x] 5.4 `GenerationPage.tsx`: блок «Форма протокола» показывает активные правила для выбранного типа и даёт выбрать форму на запуск (`template_id` уходит в `/protocols/jobs`).

## 6. Проверка

- [x] 6.1 Backend: тесты прогнаны на сервере в одноразовом контейнере против staging-БД — 18/18 (`tests/test_template_rules.py` + роут-тесты правил).
- [x] 6.2 `npx tsc --noEmit`, `npm run check:ui`, `npm run build`, `npm run lint` — зелёные.
- [x] 6.3 Backend: `ruff check`/`ruff format` по затронутым файлам — чисто; `py_compile` — ок.
- [x] 6.4 На stage проверено: миграция `20261014_000009_template_binding_rules` на head; каталог (8 форм), 32 сид-правила, предпросмотр (`86065-22` → `level_meter_two_tables`, `ГОСТ 8.461` → `rtd_platinum`), CRUD правила, `400` на неизвестный `template_id` в `/protocols/jobs`. Полная генерация протоколов и UI-прогон — за владельцем.
