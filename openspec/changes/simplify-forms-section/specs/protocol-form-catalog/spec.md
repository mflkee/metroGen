# Spec Delta

## ADDED Requirements

### Requirement: Forms are shown as a plain tree

The system SHALL present the forms of an instrument kind as a plain, readable tree: the base form
first, its derived forms nested under it, together with the rules that resolve to each form.

#### Scenario: See the tree
- **WHEN** the user opens an instrument kind
- **THEN** the base form is listed first and its derived forms are nested under it

#### Scenario: See what selects a form
- **WHEN** the user reads a form in the tree
- **THEN** the rules that resolve to it are listed with their sign, value and priority

#### Scenario: Count the forms
- **WHEN** the user looks at an instrument kind
- **THEN** the number of forms in that kind is visible without opening anything

## REMOVED Requirements

### Requirement: The dependency graph is explorable

**Reason**: the interactive graph was the least understandable part of the section and the hardest to
keep working (its layout, zoom, pan and hover all needed hand-written code that never behaved). The
owner needs the relations to be *readable*, not explorable.

**Migration**: relations are shown as a plain tree (the requirement added above). The data behind the
graph — forms, their parents and the binding rules — is unchanged, so a graph could be revisited later
without touching the model.
