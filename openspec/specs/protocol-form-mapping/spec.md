# protocol-form-mapping Specification

## Purpose
Определяет, как metroGen выбирает форму (шаблон) протокола для строки поверки, как это соответствие
хранится, отображается и управляется из UI, и как ведут себя под-формы уровнемеров.

## Requirements

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

### Requirement: Form mapping is manageable

The system SHALL expose the mapping rules (list, create, update, reorder by priority, enable/disable,
delete) and a resolver preview through the API, so the mapping can be changed without touching the
code.

#### Scenario: Manage rules through the API
- **WHEN** an administrator creates, edits, reorders, disables or deletes a rule through the API
- **THEN** the stored rules reflect the change and subsequent resolutions use them

#### Scenario: Preview a resolution
- **WHEN** a resolution is previewed for a type registration number or description
- **THEN** the response names the matching rule (if any) and the resulting form

#### Scenario: Preview shows the fallback
- **WHEN** the previewed input matches no rule
- **THEN** the response says the result comes from the built-in fallback and names the form

### Requirement: The form is resolved without asking the operator

The generation workspace SHALL keep a single instrument-kind choice per run and SHALL NOT ask the
operator to pick a protocol form. The form SHALL be resolved per row from the mapping rules (by
registration number, type description or methodology code) and the built-in fallback.

#### Scenario: A single level-meter option
- **WHEN** the operator selects «Уровнемеры» and starts a run with mixed modifications
- **THEN** the run uses one instrument kind and each row is rendered with the form its own data resolves to

#### Scenario: No form picker in the workspace
- **WHEN** the operator starts a run
- **THEN** the workspace offers no form picker; the resolution stays automatic
