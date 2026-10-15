# Spec Delta

## REMOVED Requirements

### Requirement: A form is a structure

**Reason**: редактор форм удаляется вместе с разделом; сервис больше не описывает форму данными и не
предлагает менять её структуру.

**Migration**: рендер протокола возвращается к HTML-шаблонам (`app/templates/*`) как единственному
источнику таблицы; структуры форм в БД больше нет (таблицы удаляются миграцией).

### Requirement: Derived forms inherit and override

**Reason**: наследование форм с переопределением существовало только ради редактора.

**Migration**: не требуется — наследование форм больше не выражается в данных.

### Requirement: Forms and versions can be compared

**Reason**: сравнение форм и версий было частью редактора.

**Migration**: не требуется.

### Requirement: Publishing is explicit and reversible

**Reason**: черновик/публикация/история версий существовали только для редактора форм.

**Migration**: не требуется.

### Requirement: Preview before publishing

**Reason**: предпросмотр черновика структуры был частью редактора.

**Migration**: предпросмотр протокола остаётся там, где он нужен генерации —
`POST /api/v1/protocols/manometers/html-preview` и родственные ручки.

### Requirement: Editing is restricted

**Reason**: ограничение касалось правки форм, которой больше нет в продукте.

**Migration**: не требуется.
