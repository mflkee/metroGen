# Spec Delta

## Purpose

Определяет, как таблица протокола собирается из структуры формы: чем задаются колонки, откуда берутся
значения и когда вместо структуры используется прежний HTML-шаблон.

## ADDED Requirements

### Requirement: A column is a title and a value source

A table column in a form's structure SHALL carry a title and a value source. The source SHALL be
resolved against the generator's row first, and against the render context second.

#### Scenario: Value from a generator row
- **WHEN** a column's source names a key present in the generated row
- **THEN** the cell shows that value

#### Scenario: Value from the context
- **WHEN** a column's source names a context value rather than a row key
- **THEN** the cell shows the context value

#### Scenario: Unknown source
- **WHEN** a column's source matches neither a row key nor a context value
- **THEN** the cell is empty and the rest of the table still renders

### Requirement: The table is rendered from the structure

When a form drives the protocol and its structure describes a table, the main table of the protocol
SHALL be rendered from that structure: one header row of the column titles, one row per measurement
point, cells resolved by the columns' sources.

#### Scenario: Table from the structure
- **WHEN** a protocol is generated with a form that drives the protocol and has a table in its structure
- **THEN** the protocol's main table has exactly the columns and measurement points of the structure

#### Scenario: Added point and column appear
- **WHEN** a point and a column are added to the structure and published
- **THEN** the generated protocol contains that point and that column

### Requirement: The template remains the fallback

When no structure table applies, the protocol SHALL be rendered by the existing HTML template exactly
as before.

#### Scenario: Form without a structure table
- **WHEN** a form does not drive the protocol, or its structure has no table
- **THEN** the protocol's table comes from the template, unchanged

#### Scenario: Multi-table level meters
- **WHEN** a level-meter form drives the protocol
- **THEN** only the main table comes from the structure; the additional tables (second table, current output) stay in the template

### Requirement: The editor edits titles and sources

The form editor SHALL let the user edit a column's title and its value source, and SHALL suggest the
sources available for the form.

#### Scenario: Edit a column
- **WHEN** the user changes a column's title and source and saves the draft
- **THEN** the draft holds both, and publishing them changes the generated table

#### Scenario: Suggested sources
- **WHEN** the user edits a column
- **THEN** the sources the form's generator can produce are suggested
