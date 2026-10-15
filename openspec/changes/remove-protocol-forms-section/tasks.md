# Tasks

## 1. Frontend: убрать раздел

- [ ] 1.1 Удалить `src/pages/ProtocolFormsPage.tsx` и `src/api/templates.ts`.
- [ ] 1.2 `src/app/router.tsx`: убрать lazy-импорт и роут `/admin/templates`.
- [ ] 1.3 `src/lib/nav.ts`: убрать пункт «Формы протоколов»; `src/components/Icon.tsx` — иконку `form`.
- [ ] 1.4 Проверить, что не осталось ссылок на удалённое (`grep -rn "ProtocolFormsPage\|api/templates\|/admin/templates"`).

## 2. Backend: убрать API раздела

- [ ] 2.1 `app/api/routes/templates.py`: оставить только правила (`GET/POST /rules`, `PATCH/DELETE /rules/{id}`) и `POST /rules/preview`; удалить каталог, карточку формы, черновик, публикацию, версии, откат, предпросмотр структуры и сравнение вместе с их хелперами.
- [ ] 2.2 `app/schemas/template.py`: оставить схемы правил и предпросмотра; удалить каталог/форму/структуру/версии/сравнение.
- [ ] 2.3 Удалить `app/services/form_structure.py` и `app/services/form_structures.py`.

## 3. Backend: вернуть рендер таблицы шаблону

- [ ] 3.1 `app/services/protocol_builder.py`: убрать импорт `form_structures`, блок с `structure_table` и передачу `point_fractions`.
- [ ] 3.2 `app/services/html_renderer.py`: убрать дефолт `structure_table`.
- [ ] 3.3 `app/templates/pressure.html`, `app/templates/level_meter.html`: убрать обёртки `{% if structure_table %}`; удалить `app/templates/_structure_table.html`.
- [ ] 3.4 `app/services/generators/base.py`: убрать `point_fractions` и `steps_from_fractions`; вернуть `pressure_common.py` и `level_meter.py` к `_nice_steps`.

## 4. БД

- [ ] 4.1 Alembic-миграция: `DROP TABLE protocol_form_versions`, `DROP TABLE protocol_forms` (downgrade пересоздаёт схему).
- [ ] 4.2 `app/db/models.py`: удалить `ProtocolForm` и `ProtocolFormVersion` (и `overlay`/`structure` вместе с ними). `TemplateBindingRule` и `Methodology.template_id` остаются.

## 5. Тесты

- [ ] 5.1 Удалить `tests/test_form_structure.py`.
- [ ] 5.2 `tests/test_reference_crud_routes.py`: удалить тесты раздела (каталог, карточка формы, CRUD правил, предпросмотр, права на правку формы); оставить CRUD справочников.
- [ ] 5.3 `tests/test_html_renderer.py`: удалить тесты таблицы из структуры.
- [ ] 5.4 Проверить, что тесты маппинга (`test_template_rules.py`) и генераторов остаются и проходят.

## 6. Проверка

- [ ] 6.1 `npx tsc --noEmit`, `npm run check:ui`, `npm run build`, `npm run lint` — зелёные.
- [ ] 6.2 Backend: `ruff check` версией проекта (0.12.12) — чисто.
- [ ] 6.3 `pytest tests/` на отдельной БД — зелёный (генерация и маппинг не задеты).
- [ ] 6.4 На stage: миграция применилась, страница `/admin/templates` больше не существует, генерация протокола работает как раньше.
