# Tasks

## 1. Стиль (ruff версии проекта, 0.12.12)

- [x] 1.1 `app/services/form_structure.py`: `UP038` — `isinstance(value, dict | list)` вместо кортежа.
- [x] 1.2 `migrations/versions/20261012_000007_users_constraints.py`: удалён неиспользуемый `import sqlalchemy as sa`.

## 2. Устаревшие тесты

- [x] 2.1 `tests/test_controller_65685_generator.py`: убран импорт несуществующего `CHANNEL_COUNT`; число каналов — из `ctx["channels_count"]`; добавлен тест на дефолт (4 канала).
- [x] 2.2 `tests/test_protocols_routes.py`: `_make_run_id` → `_make_run_time` (4 места).
- [x] 2.3 `tests/test_protocol_helpers.py`: `test_exports_folder_label` приведён к формату `<оборудование> <год-месяц|ММ> <ЧЧ:ММ>`, время замокано (`_make_run_time` → `03:01`).

## 3. Проверка

- [x] 3.1 `ruff check` версией проекта (0.12.12) в контейнере — **All checks passed**.
- [x] 3.2 `pytest tests/ -q` на **отдельной чистой БД** — **174 passed, 0 failed** (было 9 failed + 1 error). Пятое падение (`test_manometers_pdf_files_prefers_matching_month`) оказалось не устаревшим тестом, а следствием прогона против **замусоренной staging-БД**: тесты ingest'ят реестр в ту БД, на которую смотрят, и на staging накопились активные строки, из-за чего `one_or_none()` начал падать. Рецепт чистой БД — в design.md (D5).
