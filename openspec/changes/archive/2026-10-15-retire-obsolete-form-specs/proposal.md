# Proposal

## Why

При удалении раздела «Формы протоколов» в двух спеках остались требования, которые уже не выполняются:
в `protocol-form-catalog` — «The dependency graph is explorable» (графа нет), в `protocol-form-table` —
«The editor edits titles and sources» (редактора нет). Они остались потому, что требования про граф и
про правку колонок убирались двумя другими change'ами, которые были удалены как устаревшие до архивации.

Спека, которая описывает несуществующее поведение, хуже отсутствующей спеки: по ней нельзя проверить
систему.

## What Changes

- Убираются два последних требования этих capability; сами capability выходят из эксплуатации
  (`retire_capabilities: true`), файлы спеков удаляются.
- `protocol-form-mapping` не затрагивается — правила и `resolve_form` остаются.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `protocol-form-catalog`: требование об интерактивном графе удаляется; других требований у capability не
  остаётся, поэтому она выходит из эксплуатации.
- `protocol-form-table`: требование о правке заголовка и источника колонки в интерфейсе удаляется;
  capability выходит из эксплуатации.

## Impact

- Только `openspec/specs/**`. Кода не касается: графа и редактора в системе уже нет.
- Остаются спеки: `protocol-form-mapping` (маппинг), `reference-entity-management`, `user-preferences`.
