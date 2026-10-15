# Tasks

## 1. Frontend: убрать раздел

- [x] 1.1 Удалены `src/pages/ProtocolFormsPage.tsx` и `src/api/templates.ts`.
- [x] 1.2 `src/app/router.tsx`: убраны lazy-импорт и роут `/admin/templates`.
- [x] 1.3 `src/lib/nav.ts`: убран пункт «Формы протоколов»; `src/components/Icon.tsx` — иконка `form`.
- [x] 1.4 Проверено: ссылок на удалённое не осталось (`grep` пуст).

## 2. Backend: убрать API раздела

- [x] 2.1 `app/api/routes/templates.py`: остались только правила (`GET/POST /rules`, `PATCH/DELETE /rules/{id}`) и `POST /rules/preview`; каталог, карточка формы, черновик, публикация, версии, откат, предпросмотр структуры и сравнение удалены вместе с хелперами.
- [x] 2.2 `app/schemas/template.py`: остались схемы правил и предпросмотра.
- [x] 2.3 Удалены `app/services/form_structure.py` и `app/services/form_structures.py`.

## 3. Backend: рендер таблицы снова у шаблона

- [x] 3.1 `app/services/protocol_builder.py`: убраны импорт `form_structures`, блок `structure_table` и передача `point_fractions`.
- [x] 3.2 `app/services/html_renderer.py`: убран дефолт `structure_table`.
- [x] 3.3 `pressure.html` и `level_meter.html`: убраны обёртки `{% if structure_table %}`; `_structure_table.html` удалён.
- [x] 3.4 `generators/base.py`: убраны `point_fractions` и `steps_from_fractions`; `pressure_common.py` и `level_meter.py` вернулись к `_nice_steps`.

## 4. БД

- [x] 4.1 Миграция `20261015_000012_drop_protocol_forms`: удаляет `protocol_form_versions` и `protocol_forms` (downgrade пересоздаёт схему).
- [x] 4.2 `app/db/models.py`: `ProtocolForm` и `ProtocolFormVersion` удалены; `TemplateBindingRule` и `Methodology.template_id` остались.

## 5. Тесты

- [x] 5.1 Удалён `tests/test_form_structure.py`.
- [x] 5.2 `tests/test_reference_crud_routes.py`: удалены тесты раздела; вместо теста каталога — тест списка правил; CRUD справочников остался.
- [x] 5.3 `tests/test_html_renderer.py`: удалены тесты таблицы из структуры (исходные тесты рендерера на месте).
- [x] 5.4 Тесты маппинга (`test_template_rules.py`) и генераторов остались и проходят.

## 6. Проверка

- [x] 6.1 `npx tsc --noEmit`, `npm run check:ui`, `npm run build`, `npm run lint` — зелёные.
- [x] 6.2 `ruff check` версией проекта (0.12.12) — чисто.
- [x] 6.3 `pytest tests/` на отдельной чистой БД — **160 passed, 0 failed** (было 179: минус тесты удалённого раздела).
- [x] 6.4 На stage: миграция `20261015_000012` на head, api перезапущен, в собранном фронтенде «Формы протоколов» больше нет. Ручная проверка генерации протокола — за владельцем.
