# Tasks

## 1. Модель и миграция

- [ ] 1.1 Добавить модель `TemplateBindingRule` (`app/db/models.py`) с полями `instrument_kind`, `match_field`, `match_value`, `template_id`, `priority`, `is_active`.
- [ ] 1.2 Добавить `Methodology.template_id: str | None` (`app/db/models.py`).
- [ ] 1.3 Alembic-миграция: таблица правил + колонка у методик (+ индекс по `instrument_kind`/`match_field`).
- [ ] 1.4 Идемпотентный сид правил, эквивалентных текущим эвристикам `resolve_template_id` (номера типов, ключевые слова, коды методик); проверка: прогон эвристик и сида даёт одинаковые результаты на выборке.

## 2. Разрешение формы

- [ ] 2.1 Новый сервис `app/services/template_resolution.py`: `resolve_form(session, *, instrument_kind, method_code, mitype_number, mitype_title, override=None) -> str` с порядком override → правила по приоритету → `Methodology.template_id` → эвристики.
- [ ] 2.2 `app/services/protocol_builder.py`: заменить локальный `resolve_template_id` на `resolve_form` (прокинуть `instrument_kind` и сессию); `context["template_id"]` заполняется результатом.
- [ ] 2.3 `app/services/html_renderer.py`: `render_protocol_html` использует `context["template_id"]`; `_template_name_from_context` оставить только фоллбэком и логировать пересчёт.
- [ ] 2.4 Тесты: правило перекрывает эвристику; приоритет правил; отключённое правило игнорируется; форма методики; совпадение вычисленной и отрисованной формы; override.

## 3. Под-формы уровнемеров

- [ ] 3.1 Вынести под-формы в отдельные `template_id`: `level_meter` (дефолт, одна таблица), `level_meter_two_tables`, `level_meter_current_output` — записи в `TEMPLATES` (`app/services/templates.py`) и `generators/registry.py`; HTML-шаблоны (`app/templates/*.html`) при необходимости.
- [ ] 3.2 `app/services/generators/level_meter.py`: выбирать набор таблиц по `template_id`, а не по номеру типа внутри генератора.
- [ ] 3.3 Сид-правила для `86065-22` → `level_meter_two_tables`, `47249-16` → `level_meter_current_output`; тесты на оба варианта и на дефолт.

## 4. API

- [ ] 4.1 Роутер `app/api/routes/templates.py`: `GET /templates` (каталог форм), зарегистрировать в `app/main.py`.
- [ ] 4.2 CRUD правил: `GET/POST /template-rules`, `PATCH/DELETE /template-rules/{id}` (+ проверка, что `template_id` есть в каталоге, а `match_field` — допустимое значение).
- [ ] 4.3 `POST /template-rules/preview` → `{form, source: "rule" | "methodology" | "fallback", rule?}` .
- [ ] 4.4 Проброс override в генерацию: параметр формы в `app/api/routes/protocols.py` (`/jobs` и pdf-ручки).
- [ ] 4.5 Тесты роутеров: каталог, CRUD, предпросмотр (правило/методика/fallback), override.

## 5. Frontend

- [ ] 5.1 `src/api/templates.ts`: типы и вызовы каталога, правил, предпросмотра, override.
- [ ] 5.2 `src/pages/AdminTemplatesPage.tsx`: список правил (раскрывающиеся элементы + диалог CRUD, приоритет, вкл/выкл, удаление), блок предпросмотра (ввод номера типа/описания → форма и источник).
- [ ] 5.3 Роут `/admin/templates` в `src/app/router.tsx` и пункт в `src/lib/nav.ts` (для ADMINISTRATOR/DEVELOPER).
- [ ] 5.4 `GenerationPage.tsx`: показ разворачиваемых форм для текущего входа и выбор явного override на запуск.

## 6. Проверка

- [ ] 6.1 Backend: `pytest` — зелёный, включая новые тесты разрешения, под-форм и роутеров.
- [ ] 6.2 `cd frontend && npx tsc --noEmit && npm run check:ui && npm run build` — зелёные.
- [ ] 6.3 На stage: сгенерировать по протоколу на каждый тип прибора и сравнить форму с прежней (сид-правила должны сохранить поведение).
- [ ] 6.4 На stage: изменить правило и убедиться, что форма сменилась; проверить override на запуск; проверить предпросмотр.
