# Proposal

## Why

Раздел «Формы протоколов» не прижился. Он задумывался как способ понять, какие формы есть и почему
строка получает именно эту, но за несколько итераций превратился в полу-редактор шаблонов (структура,
оверлеи, черновики, версии, сравнение, граф), а затем в обзор, который владельцу всё равно не нужен:
«да давай удаляем, потом что-то просто придумаем новое».

Важно, что удаляется **раздел**, а не маппинг: правила `template_binding_rules` и `resolve_form`
нужны генерации — именно они выбирают форму протокола (манёметры, уровнемеры, контроллеры, термометры).

## What Changes

- **Интерфейс**: страница «Формы протоколов», пункт навигации, роут `/admin/templates` и клиент
  `src/api/templates.ts` удаляются. Иконка `form` тоже.
- **API раздела**: `GET /api/v1/templates`, `GET /api/v1/templates/{code}`,
  `PUT …/draft`, `POST …/publish`, `GET …/versions`, `POST …/versions/{rev}/restore`,
  `POST …/{code}/preview`, `POST …/{code}/compare` — удаляются.
- **Структура формы как механизм**: `app/services/form_structure.py`, `app/services/form_structures.py`,
  рендер таблицы из структуры (`app/templates/_structure_table.html`, обёртки в `pressure.html` и
  `level_meter.html`, `structure_table` в рендерере), точки замера из структуры
  (`GenInput.point_fractions`, `steps_from_fractions`) — удаляются.
- **БД**: таблицы `protocol_forms` и `protocol_form_versions` удаляются миграцией (их никто не читает
  после этого change). `template_binding_rules` и `Methodology.template_id` **остаются** — это маппинг.
- **Остаётся как API маппинга**: CRUD правил (`GET/POST/PATCH/DELETE /api/v1/templates/rules`) и
  `POST /api/v1/templates/rules/preview`, сервис `template_rules.resolve_form` и проброс явной формы на
  запуск (`template_id` в `/protocols/jobs`).

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `protocol-form-catalog`: capability удаляется целиком (каталог, граф/дерево, инспектор, обратный
  поиск, пометки) — раздела нет.
- `protocol-form-editor`: capability удаляется целиком (структура, наследование, версии, сравнение,
  предпросмотр, права на редактирование форм).
- `protocol-form-table`: capability удаляется целиком (колонки как данные, таблица из структуры).
- `form-catalog-guidance`: capability удаляется целиком (объяснение и легенда — объяснять больше нечего).
- `protocol-form-mapping`: **не меняется** — правила и `resolve_form` продолжают работать, включая
  управление правилами через API.

## Impact

- **Frontend**: удаляются страница, роут, пункт меню, API-клиент; зависимостей не добавляется.
- **Backend**: удаляются роуты/схемы/сервисы раздела и рендер таблицы из структуры; генерация
  (`protocol_builder`, генераторы, `html_renderer`) возвращается к шаблонам как единственному источнику
  таблицы. Маппинг не затрагивается.
- **Миграция**: `DROP TABLE protocol_form_versions`, `DROP TABLE protocol_forms` (обратимая — downgrade
  пересоздаёт схему).
- **Тесты**: удаляются `tests/test_form_structure.py` и тесты роутов/рендера, относящиеся к разделу;
  тесты маппинга и генераторов остаются и должны остаться зелёными.
