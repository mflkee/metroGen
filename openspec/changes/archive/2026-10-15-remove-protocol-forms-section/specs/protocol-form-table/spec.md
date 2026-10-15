# Spec Delta

## REMOVED Requirements

### Requirement: A column is a title and a value source

**Reason**: колонки как данные описывались структурой формы, а редактор форм удаляется вместе с разделом.

**Migration**: не требуется — колонки снова задаются HTML-шаблоном.

### Requirement: The table is rendered from the structure

**Reason**: таблица, собираемая из структуры формы, была частью того же механизма.

**Migration**: таблица протокола снова рендерится шаблоном (`pressure.html`, `level_meter.html`) — как
до появления структуры.

### Requirement: The template remains the fallback

**Reason**: требование описывало соотношение «структура или шаблон»; структуры больше нет, поэтому
фоллбэк стал единственным поведением и отдельного требования не требует.

**Migration**: поведение по умолчанию (рендер шаблоном) остаётся и покрыто тестами рендерера.
