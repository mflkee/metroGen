# Spec Delta

## REMOVED Requirements

### Requirement: The dependency graph is explorable

**Reason**: графа в системе нет — раздел «Формы протоколов» удалён целиком (change
`2026-10-15-remove-protocol-forms-section`), а требование о графе осталось по недосмотру: его должен был
убрать промежуточный change, который был отменён до архивации.

**Migration**: ничего не заменяет. Взаимосвязи форм описаны данными (`parent_code` удалён вместе с
таблицами; правила выбора формы остаются в `template_binding_rules` и спеке `protocol-form-mapping`).
