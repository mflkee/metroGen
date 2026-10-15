# Design

## Context

См. `proposal.md` — Why. Все падения — расхождение тестов с продуктом, а не дефекты продукта:
проверено по истории (`git log -S`) и по текущему коду.

Отдельная находка: **локальный ruff новее контейнерного**. В контейнере стоит `ruff 0.12.12` (из
`pyproject.toml`, `ruff>=0.12.12`), и он ещё содержит правило `UP038`; мой локальный ruff это правило
удалил и потому молчал. Вывод: стилевые проверки надо гонять версией из проекта, иначе «локально
чисто» ничего не значит.

## Goals / Non-Goals

**Goals:**

- `pytest tests/` зелёный целиком в среде проекта.
- Тесты описывают текущее поведение, включая нетривиальные форматы (имя папки экспорта).

**Non-Goals:**

- Менять продуктовый код ради старых тестов.
- Добавлять новые тесты (кроме приведения существующих в порядок).

## Decisions

### D1: Тесты следуют продукту

Каждое расхождение разобрано и решено в пользу текущего поведения:

| Тест | Было | Стало |
|---|---|---|
| `test_controller_65685_generator` | импорт `CHANNEL_COUNT` | число каналов из `ctx["channels_count"]` (по умолчанию 4), импорт `SET_VALUES_MA` |
| `test_protocols_routes` (5) | `_make_run_id` | `_make_run_time` |
| `test_protocol_helpers::test_exports_folder_label` | `PDF <оборудование> <ММ>` | `<оборудование> <YYYY-MM> <HH:MM>`, `_make_run_time` замокан |

*Альтернатива:* вернуть продукт к старому поведению. Отклонено — формат имени папки изменён осознанно
(коммит «new export folder naming»), а `CHANNEL_COUNT` заменён контекстом строки.

### D2: Время в тестах — детерминированное

`_make_run_time()` возвращает текущее время, поэтому тест подменяет её (`monkeypatch.setattr`) на
фиксированное `"03:01"` — иначе проверка была бы флаки.

### D3: Стиль — версией из проекта

`UP038` в `app/services/form_structure.py` исправляется по существу (`isinstance(value, dict | list)`),
мёртвый импорт в старой миграции удаляется. Проверка — `ruff check` в контейнере (0.12.12).

### D4: Имя run-папки — решено владельцем (вариант B)

Пять тестов `test_*_pdf_files_*` ждали папку `Generation rtd 10 - run-rtd`, а код создаёт
`rtd 2025-10 run-rtd`. Владелец подтвердил, что новый формат `<оборудование> <YYYY-MM|ММ> <ЧЧ:ММ>`
осознан: тесты и `AGENTS.md` приведены к нему, а не наоборот. Заодно удалены мёртвые параметры
`prefix="PDF"` и `run_id` у `_exports_folder_label` — след того же рефакторинга.

### D5: Тесты гоняются на отдельной БД, а не на staging

Прогон против staging-БД ломается не из-за кода: тесты ingest'ят реестр в ту БД, на которую смотрят
(в логе видно `deactivated 6195 previous rows`), и на staging за много прогонов накапливаются
активные строки — после чего `one_or_none()` в поиске записи реестра падает с `MultipleResultsFound`.
Это и было пятое падение, выглядевшее как «устаревший тест».

Рецепт чистой БД (одноразово, ничего в репозитории не меняя):

```bash
# 1. создать отдельную БД (через контейнер БД, без пароля по TCP)
docker exec metroGen_db_stg sh -lc 'psql -U $POSTGRES_USER -d postgres -c "CREATE DATABASE metrogen_test"'
# 2. миграции + сид + прогон — в одноразовом контейнере
docker run --rm -e DATABASE_URL=postgresql+asyncpg://metrologenerator:metrologenerator@172.17.0.1:5437/metrogen_test \
  -v /home/mflkee/apps/metroGen:/app -w /app --entrypoint sh ghcr.io/mflkee/metrogen-api:staging -lc '
    export PATH=/app/.venv/bin:$PATH
    uv pip install --python /app/.venv/bin/python -q pytest pytest-asyncio aiosqlite respx
    alembic upgrade head && /app/.venv/bin/python -c "import asyncio; from app.db.seed import seed_from_config; asyncio.run(seed_from_config())"
    /app/.venv/bin/python -m pytest tests/ -q'
# 3. убрать
docker exec metroGen_db_stg sh -lc 'psql -U $POSTGRES_USER -d postgres -c "DROP DATABASE metrogen_test"'
```

## Risks / Trade-offs

- [Обновляя тесты, можно «закрепить» настоящий дефект] → по каждому пункту сверялся смысл; там где
  смысл был неясен (D4), вопрос вынесен владельцу, а не решён молча.
- [Версии ruff разойдутся снова] → зафиксировано здесь: стилевые проверки гоняются версией из проекта
  (0.12.12); локальный ruff новее и правила UP038 уже не содержит.
- [Прогон против staging-БД портит её] → D5: отдельная БД.

## Verification

`ruff check` (0.12.12) — All checks passed; `pytest tests/ -q` на отдельной чистой БД —
**174 passed, 0 failed**.
