# Tasks

> **Статус:** реализован основной контур (данные + разрешение формы + под-формы уровнемеров +
> админ-API и страница управления правилами). **Отложено:** override формы на конкретный запуск
> генерации (задачи 4.4/5.4) — он требует протяжки параметра через `_generate_pdf_files` в
> `app/api/routes/protocols.py`, это отдельный следующий шаг. Тесты (2.4/3.3/4.5/6.1) — после
> появления возможности прогонять `pytest` на сервере.

## 1. Модель и миграция

- [x] 1.1 Модель `TemplateBindingRule` (`app/db/models.py`): `instrument_kind`, `match_field`, `match_value`, `template_id`, `priority`, `is_active`, таймстемпы; индекс по `instrument_kind`.
- [x] 1.2 `Methodology.template_id: str | None`.
- [x] 1.3 Alembic-миграция `20261014_000009_template_binding_rules` (таблица + колонка + индекс).
- [x] 1.4 Сид правил, повторяющих эвристики (приоритеты 10/20/25/28/30/35/36 воспроизводят порядок `resolve_template_id`), — идемпотентность обеспечена миграцией.

## 2. Разрешение формы

- [x] 2.1 `app/services/template_rules.py`: `resolve_form(...)` с порядком override → правила (по приоритету, с фильтром по типу прибора, если он известен) → форма методики → эвристики. Реализовано с коротким кэшем (30 с) + `invalidate()` после правок, чтобы не делать по два запроса на строку в массовой генерации.
- [x] 2.2 `app/services/protocol_builder.py`: `build_context` принимает `session` и вызывает `resolve_form`; в контекст пишутся `template_id`, `template_source`, `template_rule_id`. `build_protocol_context` прокидывает сессию в обоих путях вызова.
- [x] 2.3 `app/services/html_renderer.py`: рендер использует `context["template_id"]` и `TEMPLATES[...]["path"]`; пересчёт эвристиками остался только фоллбэком и логируется.
- [ ] 2.4 Тесты: правило перекрывает эвристику; приоритет; выключенное правило; форма методики; совпадение вычисленной и отрисованной формы. *(отложено — `pytest` на сервере)*

## 3. Под-формы уровнемеров

- [x] 3.1 В `TEMPLATES` добавлены `level_meter_two_tables` и `level_meter_current_output` (оба рендерятся `level_meter.html`); зарегистрированы в `generators/registry.py`.
- [x] 3.2 `generators/level_meter.py` выбирает набор таблиц по `template_id` (номер типа — только фоллбэк для базовой формы).
- [x] 3.3 Сид-правила: `86065-22` → `level_meter_two_tables`, `47249-16` → `level_meter_current_output`. *(тесты отложены)*

## 4. API

- [x] 4.1 `GET /api/v1/templates` — каталог форм + допустимые типы приборов и условия; роутер зарегистрирован в `app/main.py`.
- [x] 4.2 CRUD правил: `GET/POST /template-rules`, `PATCH/DELETE /template-rules/{id}` с валидацией `template_id`/`match_field`/`instrument_kind`; после каждой правки `template_rules.invalidate()`.
- [x] 4.3 `POST /template-rules/preview` → форма + источник (`rule`/`methodology`/`fallback`/`override`).
- [ ] 4.4 Override формы на запуск генерации (параметр в `/protocols/jobs` и pdf-ручках). *(отложено)*
- [ ] 4.5 Тесты роутеров. *(отложено)*

## 5. Frontend

- [x] 5.1 `src/api/templates.ts`: каталог, правила, предпросмотр.
- [x] 5.2 `src/pages/AdminTemplatesPage.tsx`: раскрывающиеся правила, диалог создания/правки, включение/выключение, удаление с подтверждением, блок предпросмотра.
- [x] 5.3 Роут `/admin/templates` и пункт «Формы протоколов» в навигации (ADMINISTRATOR/DEVELOPER).
- [ ] 5.4 `GenerationPage.tsx`: показ разворачиваемых форм для текущего входа и override на запуск. *(отложено вместе с 4.4)*

## 6. Проверка

- [ ] 6.1 Backend: `pytest` (разрешение формы, под-формы, роутеры). *(на сервере)*
- [x] 6.2 `npx tsc --noEmit`, `npm run check:ui`, `npm run build`, `npm run lint` — зелёные.
- [x] 6.3 Backend: `ruff check`/`ruff format` по затронутым файлам — чисто; `py_compile` — ок.
- [ ] 6.4 На stage: сгенерировать по протоколу на каждый тип и убедиться, что форма совпала с прежней; затем изменить правило и проверить предпросмотр.
