# Spec Delta

## MODIFIED Requirements

### Requirement: A form is a structure

A protocol form SHALL be described as data — sections, tables with columns, and table rows (measurement
points) — and that structure SHALL be changeable through the API, without a code change or deploy. The
service SHALL NOT offer a form editor in the interface.

#### Scenario: Add a measurement point
- **WHEN** a structure with an extra measurement point is published for a form
- **THEN** protocols generated with that form contain the extra point

#### Scenario: Add a column
- **WHEN** a structure with an extra column is published
- **THEN** the rendered table has that column for every row

#### Scenario: Sections and text blocks
- **WHEN** a structure changes a section title or a text block
- **THEN** the rendered protocol shows the new text

### Requirement: Derived forms inherit and override

A form MAY derive from another form. A derived form SHALL inherit its parent's structure and SHALL be
able to override individual parts. Changing a parent SHALL propagate to derived forms that do not
override the changed part.

#### Scenario: Parent change propagates
- **WHEN** a table on the base form changes and the derived form does not override that table
- **THEN** the derived form reflects the change

#### Scenario: Override wins
- **WHEN** the derived form overrides a part that the parent later changes
- **THEN** the derived form keeps its override and the override is reported as such

#### Scenario: Overrides are visible
- **WHEN** a derived form is read
- **THEN** every part it overrides is listed as an override of its parent
