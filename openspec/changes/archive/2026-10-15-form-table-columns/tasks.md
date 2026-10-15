# Tasks

## 1. Структура и сборка таблицы

- [x] 1.1 `app/services/form_structure.py`: `source` у колонки — валидация (необязательная, непустая строка) и показ в предпросмотре.
- [x] 1.2 `app/services/form_structures.py`: `build_structure_table(structure, rows, context)` — колонки, разрешение значений (строка → контекст → пусто), строки по точкам; пусто, если нет строк или колонок.
- [x] 1.3 `app/services/protocol_builder.py`: `structure_table` в контекст только когда форма управляет протоколом и в структуре есть таблица.

## 2. Шаблоны

- [x] 2.1 `app/templates/_structure_table.html` — таблица из `structure_table` в классах прежней вёрстки.
- [x] 2.2 `pressure.html` и `level_meter.html`: главная таблица обёрнута в `{% if structure_table %}…{% else %}…{% endif %}`; `structure_table` получил явный дефолт `None` в `render_protocol_html` (рендер идёт со `StrictUndefined`).

## 3. Frontend

- [x] 3.1 `StructureEditor`: поле «источник» у колонки + подсказка ключей по типу прибора (`datalist`).
- [x] 3.2 Предпросмотр структуры показывает источники рядом с заголовками.

## 4. Проверка

- [x] 4.1 Тесты: `build_structure_table` (значение из строки, из контекста, неизвестный источник → пусто, без строк/колонок → None); `validate_structure` с пустым `source`; фоллбэк шаблона без `structure_table` и рендер из структуры — на реальном контексте `build_context`.
- [x] 4.2 `npx tsc --noEmit`, `npm run check:ui`, `npm run build`, `npm run lint` — зелёные; `ruff check` (0.12.12) — чисто; `pytest tests/` на отдельной БД — **179 passed, 0 failed**.
- [ ] 4.3 На stage: включить структуру у формы, добавить колонку с источником, опубликовать и убедиться, что таблица собралась из структуры. *(за владельцем)*
