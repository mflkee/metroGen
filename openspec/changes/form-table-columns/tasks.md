# Tasks

## 1. Структура и сборка таблицы

- [ ] 1.1 `app/services/form_structure.py`: `source` у колонки — валидация (необязательная строка) и показ в предпросмотре.
- [ ] 1.2 `app/services/form_structures.py`: `build_structure_table(structure, rows, context)` — колонки, разрешение значений (строка → контекст → пусто), строки по точкам.
- [ ] 1.3 `app/services/protocol_builder.py`: класть `structure_table` в контекст только когда форма управляет протоколом и в структуре есть таблица.

## 2. Шаблоны

- [ ] 2.1 Новый `app/templates/_structure_table.html` — таблица из `structure_table` в классах прежней вёрстки.
- [ ] 2.2 `pressure.html` и `level_meter.html`: главная таблица обёрнута в `{% if structure_table %}…{% else %}…{% endif %}`; фоллбэк — прежняя разметка без изменений.

## 3. Frontend

- [ ] 3.1 `StructureEditor`: поле «источник» у колонки + подсказка ключей по типу прибора.
- [ ] 3.2 Предпросмотр: показывать источники колонок (значения — при генерации).

## 4. Проверка

- [ ] 4.1 Тесты: `build_structure_table` (значение из строки, из контекста, неизвестный источник → пусто); `validate_structure` с `source`; рендер шаблона **без** `structure_table` не изменился (фоллбэк).
- [ ] 4.2 `npx tsc --noEmit`, `npm run check:ui`, `npm run build`, `npm run lint`; `ruff check` версией проекта; `pytest tests/` на отдельной БД.
- [ ] 4.3 На stage: включить структуру у формы, добавить колонку с источником, опубликовать и убедиться, что таблица собралась из структуры.
