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
- [ ] 3.2 `pytest tests/ -q` целиком: **169 passed, 5 failed** (было 9 failed + 1 error). Остались 5 тестов `tests/test_protocols_routes.py::test_*_pdf_files_*` — **они не устарели, а фиксируют расхождение продукта с документацией** (см. design.md, D4): тест ждёт папку `Generation <label> <ММ> - <run_id>` (как написано в `AGENTS.md`), а код создаёт `<оборудование> <YYYY-MM> <ЧЧ:ММ>`. Нужно решение владельца: это регрессия кода или устаревшие тесты и документация.
