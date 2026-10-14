# Spec Delta

## Purpose

Определяет, как metroGen выбирает форму (шаблон) протокола для строки поверки, как это соответствие
хранится, отображается и управляется из UI, и как ведут себя под-формы уровнемеров.

## ADDED Requirements

### Requirement: Form resolution is data-driven

The system SHALL resolve a row's protocol form from mapping rules stored in the database, matched by
instrument kind and a condition (type registration number, a keyword of the type description, or a
methodology code), evaluated in priority order. When no rule matches, the system SHALL fall back to
the built-in heuristics.

#### Scenario: A rule decides the form
- **WHEN** a row's instrument kind and match value satisfy an enabled rule
- **THEN** the row is rendered with that rule's form

#### Scenario: Priority order
- **WHEN** more than one enabled rule matches a row
- **THEN** the rule with the highest priority (lowest order value) decides the form

#### Scenario: Fallback when nothing matches
- **WHEN** no enabled rule matches a row
- **THEN** the built-in heuristic decides the form

#### Scenario: Disabled rule is ignored
- **WHEN** a matching rule is disabled
- **THEN** it does not affect the resolved form

### Requirement: A methodology can declare a default form

A methodology SHALL be able to declare a default protocol form, used when no rule matches and before
the built-in heuristics.

#### Scenario: Methodology default applies
- **WHEN** no rule matches a row whose methodology declares a default form
- **THEN** that methodology's form is used

#### Scenario: A rule overrides the methodology default
- **WHEN** both a matching rule and a methodology default exist
- **THEN** the matching rule wins

### Requirement: The rendered form equals the resolved form

The renderer SHALL render exactly the form produced by form resolution and SHALL NOT derive a
different form from other context fields.

#### Scenario: Builder and renderer agree
- **WHEN** a protocol is generated for a row
- **THEN** the rendered HTML is the template the resolution returned for that row

#### Scenario: Explicit override is honored
- **WHEN** a generation run is started with an explicit form override
- **THEN** the override decides the provider for every row of the run

### Requirement: Level-meter sub-forms are explicit

The level-meter protocol SHALL expose its sub-forms (single table, two tables, an additional
current-output table) as explicit, individually selectable forms. The choice SHALL NOT depend solely
on a registration number hardcoded inside the generator.

#### Scenario: Two-table form selected
- **WHEN** the resolution selects the two-table level-meter form
- **THEN** the rendered level-meter protocol contains both tables

#### Scenario: Current-output form selected
- **WHEN** the resolution selects the level-meter form with a current-output table
- **THEN** the rendered protocol contains the current-output table

#### Scenario: Default when unspecified
- **WHEN** neither a rule nor an override selects a level-meter sub-form
- **THEN** a documented default sub-form is used

### Requirement: Form mapping is manageable in the UI

An administrator SHALL be able to list, create, edit, reorder (priority), enable/disable and delete
mapping rules, and SHALL be able to preview which form a given type description or registration
number resolves to.

#### Scenario: Manage rules
- **WHEN** an administrator creates, edits, reorders or deletes a rule
- **THEN** the stored rules reflect the change and subsequent resolutions use them

#### Scenario: Preview a resolution
- **WHEN** an administrator previews a type registration number or description
- **THEN** the UI shows the matching rule (if any) and the resulting form

#### Scenario: Preview shows the fallback
- **WHEN** the previewed input matches no rule
- **THEN** the UI shows that the result comes from the built-in fallback and names the form

### Requirement: The generation workspace shows the resolved form

The generation workspace SHALL show which forms the current input resolves to and SHALL allow an
explicit form override for a run.

#### Scenario: Show resolved forms
- **WHEN** the user selects an instrument kind and provides an input
- **THEN** the workspace shows the form(s) the input resolves to

#### Scenario: Override a run
- **WHEN** the user chooses an explicit form for a run
- **THEN** the run uses that form regardless of matching rules
