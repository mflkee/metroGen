# protocol-form-editor Specification

## Purpose
Определяет конструктор форм протокола: как форма описывается данными, как работает наследование с
переопределением, как формы сравниваются и версионируются, как результат проверяется и публикуется.

## Requirements

### Requirement: A form is a structure

A protocol form SHALL be described as data — sections, tables with columns, and table rows (measurement
points) — and that structure SHALL be editable through the interface, without a code change or deploy.

#### Scenario: Add a measurement point
- **WHEN** the editor adds a measurement point to a table of a form and publishes it
- **THEN** protocols generated with that form contain the extra point

#### Scenario: Add a column
- **WHEN** the editor adds a column to a table and publishes it
- **THEN** the rendered table has that column for every row

#### Scenario: Sections and text blocks
- **WHEN** the editor changes a section title or a text block
- **THEN** the rendered protocol shows the new text

### Requirement: Derived forms inherit and override

A form MAY derive from another form. A derived form SHALL inherit its parent's structure and SHALL be
able to override individual parts. Editing a parent SHALL propagate to derived forms that do not
override the edited part.

#### Scenario: Parent change propagates
- **WHEN** the editor changes a table on the base form and the derived form does not override that table
- **THEN** the derived form reflects the change

#### Scenario: Override wins
- **WHEN** the derived form overrides a part that the parent later changes
- **THEN** the derived form keeps its override and the interface marks that part as overridden

#### Scenario: Overrides are visible
- **WHEN** the user opens a derived form
- **THEN** every part it overrides is listed and marked as an override of its parent

### Requirement: Forms and versions can be compared

The system SHALL compare two forms, and two versions of one form, listing their differences by section,
table, column and point.

#### Scenario: Compare base and derived
- **WHEN** the user compares a base form with a derived one
- **THEN** the differences are listed and the shared parts are shown as inherited

#### Scenario: Compare versions
- **WHEN** the user compares two versions of a form
- **THEN** the differences between them are listed

### Requirement: Publishing is explicit and reversible

Editing SHALL produce a draft; generation SHALL use the published version. Every published version
SHALL be recoverable.

#### Scenario: Draft is not used by generation
- **WHEN** a form is edited but not published
- **THEN** generation still uses the published version

#### Scenario: Rollback
- **WHEN** the user restores a previous published version
- **THEN** generation uses that version again

#### Scenario: History
- **WHEN** the user opens a form's history
- **THEN** the published versions are listed with the differences between them

### Requirement: Preview before publishing

The system SHALL render a protocol for a concrete instrument (registration number and modification)
from the draft, before it is published.

#### Scenario: Preview a draft
- **WHEN** the user previews a draft on a real registration number and modification
- **THEN** the protocol is rendered from the draft and is clearly marked as a preview

### Requirement: Editing is restricted

Only users with the `DEVELOPER` or `ADMINISTRATOR` role SHALL be able to edit or publish forms.

#### Scenario: Other roles read only
- **WHEN** a user without an administrative role opens a form
- **THEN** the structure is shown read-only and no edit or publish action is offered
