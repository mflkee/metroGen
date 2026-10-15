# protocol-form-catalog Specification

## Purpose
Определяет, как в metroGen можно **увидеть и понять** формы протоколов: какие они бывают по типам
приборов, как наследуются, почему конкретная строка поверки получает именно эту форму и что на это
влияет (методика, описание типа, модификация).

## Requirements

### Requirement: Forms are catalogued by instrument kind

The system SHALL present the protocol forms grouped by instrument kind, and SHALL mark each form as
a base form or as derived from another form, naming its parent.

#### Scenario: Open an instrument kind
- **WHEN** the user opens «Уровнемеры» in the catalog
- **THEN** every form of that kind is listed, the base form is marked as «база», and derived forms name the form they inherit from

#### Scenario: A form with no parent is a base form
- **WHEN** a form has no parent
- **THEN** it is presented as a base form for its instrument kind

### Requirement: The dependency graph is explorable

The system SHALL render the forms and their dependencies as an interactive graph with search and
filters. Inheritance SHALL be an edge from parent to derived form, and every binding rule SHALL be
an edge from its condition (methodology, type registration number or modification) to the form it
selects.

#### Scenario: See inheritance
- **WHEN** the user opens the graph
- **THEN** each derived form is connected to its parent, so a base form and its branches are visible as one tree

#### Scenario: Filter by axis
- **WHEN** the user filters by one of the axes (methodology, type description, modification)
- **THEN** only the forms and bindings of that axis remain visible

#### Scenario: Search
- **WHEN** the user types a registration number, a type name or a methodology code into the graph search
- **THEN** the matching nodes are highlighted and the graph is focused on them

#### Scenario: Toggle a rule's visibility
- **WHEN** the user hides disabled rules
- **THEN** their edges disappear from the graph

### Requirement: The resolution can be inspected

The system SHALL let the user ask why a given input resolves to a form and SHALL answer with the
decision path — explicit override, matching rule, methodology default or built-in fallback — naming
the step that decided.

#### Scenario: Rule decides
- **WHEN** the user inspects a registration number that matches an enabled rule
- **THEN** the answer names that rule and its form, and the path is highlighted on the graph

#### Scenario: Fallback decides
- **WHEN** no rule matches the input
- **THEN** the answer says the built-in fallback decided and names the resulting form

#### Scenario: All three axes accepted
- **WHEN** the user provides a methodology code, a type registration number and a modification together
- **THEN** the resolution uses all three, exactly as a generation run would

### Requirement: Reverse lookup from a form

For a form, the system SHALL show which conditions currently select it (its binding rules), so the
consequences of editing that form are visible before anything is edited.

#### Scenario: Which inputs lead here
- **WHEN** the user opens a form
- **THEN** the conditions that resolve to it (by methodology, type registration number or modification) are listed

### Requirement: Editable and HTML-only forms are distinguished

The system SHALL distinguish forms whose protocol is rendered from the structure from those still
rendered by a static HTML template. Every form's structure SHALL be editable; a form SHALL be marked
as driving the protocol only once its renderer is data.

#### Scenario: HTML-only form
- **WHEN** a form is rendered by a file under `app/templates/`
- **THEN** the interface says the protocol is not yet produced from the structure, and structure edits do not change generated protocols

#### Scenario: Data-driven form
- **WHEN** a form's renderer is data
- **THEN** the interface says the protocol is produced from the structure and the editor is offered for it
