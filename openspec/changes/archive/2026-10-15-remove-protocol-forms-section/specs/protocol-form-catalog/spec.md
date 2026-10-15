# Spec Delta

## REMOVED Requirements

### Requirement: Forms are catalogued by instrument kind

**Reason**: раздел «Формы протоколов» удаляется — каталог форм в интерфейсе больше не показывается.

**Migration**: ничего не заменяет; правила выбора формы остаются в API маппинга
(`/api/v1/templates/rules`) и в спеке `protocol-form-mapping`.

### Requirement: The resolution can be inspected

**Reason**: инспектор «почему эта форма» был частью удаляемого раздела.

**Migration**: тот же ответ даёт `POST /api/v1/templates/rules/preview` (остаётся как API маппинга).

### Requirement: Reverse lookup from a form

**Reason**: обратный поиск («какие правила указывают на форму») существовал только в интерфейсе раздела.

**Migration**: правила можно выбрать по `template_id` из `GET /api/v1/templates/rules`.

### Requirement: Editable and HTML-only forms are distinguished

**Reason**: различение «данные / HTML-шаблон» показывалось только в каталоге удаляемого раздела.

**Migration**: не требуется — все формы снова рендерятся шаблонами, различать нечего.

### Requirement: Forms are shown as a plain tree

**Reason**: дерево форм было последней формой того же раздела; владелец решил удалить раздел.

**Migration**: ничего не заменяет.
