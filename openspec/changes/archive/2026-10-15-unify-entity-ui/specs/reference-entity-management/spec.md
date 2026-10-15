# Spec Delta

## Purpose

Определяет единое поведение списков и справочников metroGen: раскрывающиеся элементы, создание и
правка в диалоге, подтверждаемое удаление и полнота CRUD — чтобы добавление новой методики или
другой сущности в БД было предсказуемым и удобным.

## ADDED Requirements

### Requirement: Expandable list items

Every data list (owners, methodologies, etalons, auxiliary instruments, registry entries) SHALL
render each entry as an item with an explicit expand control, so its details can be revealed in place
without leaving the list.

#### Scenario: Expand an entry
- **WHEN** the user activates the expand control of an entry
- **THEN** the entry's details are revealed in place and the control reflects the expanded state

#### Scenario: Collapse an entry
- **WHEN** the user activates the expand control of an already expanded entry
- **THEN** its details are hidden again

#### Scenario: Filters and search are preserved
- **WHEN** the user searches or filters a list and expands an entry
- **THEN** the active search and filters remain applied to the list

### Requirement: Create and edit in a dialog

Creating and editing a reference entity SHALL happen in a modal dialog opened from the list or from
the entry. A form SHALL NOT be pinned to the top of the list for these actions.

#### Scenario: Add an entity
- **WHEN** the user activates "Добавить" on a list
- **THEN** a dialog with the entity's fields opens and the list stays visible behind it

#### Scenario: Edit an entity
- **WHEN** the user activates "Изменить" on an entry or inside its expanded body
- **THEN** the same dialog opens prefilled with that entry

#### Scenario: Validation error
- **WHEN** a save request fails
- **THEN** the error is shown inside the open dialog and the entered values are preserved

#### Scenario: Successful save closes the dialog
- **WHEN** a save request succeeds
- **THEN** the dialog closes and the list reflects the change

### Requirement: Deletion requires confirmation

Removing a reference entity SHALL require confirming in a dialog, and failure SHALL be reported
inside that dialog.

#### Scenario: Confirm deletion
- **WHEN** the user requests deletion of an entity
- **THEN** a confirmation dialog appears and the entity is removed only after the user confirms

#### Scenario: Deletion refused
- **WHEN** the entity is referenced by other data and the API refuses the deletion
- **THEN** the dialog shows the reason and the entity remains

### Requirement: Reference entities are fully manageable

The system SHALL allow creating, updating and deleting owners, methodologies, etalons and auxiliary
instruments through the API, and SHALL expose those operations in the UI.

#### Scenario: Delete an owner
- **WHEN** an administrator deletes an owner that is not referenced
- **THEN** the owner is removed from the list

#### Scenario: Delete a referenced owner
- **WHEN** an administrator deletes an owner referenced by registry or instrument records
- **THEN** the API responds with `409` and the dialog shows that the owner is in use

#### Scenario: Update an etalon
- **WHEN** an administrator edits an etalon's fields and saves
- **THEN** the stored etalon reflects the new values

#### Scenario: Update an auxiliary instrument
- **WHEN** an administrator edits an auxiliary instrument and saves
- **THEN** the stored instrument reflects the new values

### Requirement: Methodology points are edited in the dialog

A methodology's verification points SHALL be editable within its entity dialog: add, remove, reorder,
and edit the label, type and default text of a point.

#### Scenario: Edit points
- **WHEN** an administrator adds, removes or edits points of a methodology and saves
- **THEN** the methodology's points reflect the change in the list and on reload

### Requirement: Aliases are manageable

Owners and methodologies SHALL expose their aliases for viewing and editing from the UI.

#### Scenario: View aliases
- **WHEN** an administrator expands an owner or methodology
- **THEN** its aliases are listed

#### Scenario: Edit aliases
- **WHEN** an administrator adds or removes an alias and saves
- **THEN** the stored aliases reflect the change

### Requirement: Registry entries are inspectable

The generation workspace's registry list SHALL let the user expand an entry to inspect all stored
fields (source file, sheet, instrument kind, dates, protocol number, payload summary) without
changing the existing filters.

#### Scenario: Inspect a registry entry
- **WHEN** the user expands a registry entry
- **THEN** the entry's stored fields are shown and no other entry is modified
