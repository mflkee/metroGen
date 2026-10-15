# Spec Delta

## Purpose

Определяет, как страница «Формы протоколов» объясняет себя: что такое форма, по каким признакам она
выбирается, какие подписи видит пользователь и что означает легенда графа.

## ADDED Requirements

### Requirement: The page explains how a form is chosen

The page SHALL state, in plain language, that a protocol form is chosen from the instrument's
methodology, its type description (registration number and name) and its modification, that rules are
applied by priority, and that the built-in heuristic decides when no rule matches.

#### Scenario: Explanation is visible
- **WHEN** the user opens the page
- **THEN** the explanation is shown without having to open a dialog

#### Scenario: Explanation names the three things
- **WHEN** the explanation is read
- **THEN** methodology, type description and modification are each named as something that can decide the form

### Requirement: No unexplained internal jargon

The labels the user sees SHALL use plain words; an internal term (the rule's match field) SHALL be
presented as «признак» with a human name and an example for every option.

#### Scenario: Filter labels
- **WHEN** the user looks at the filter that narrows the graph by how a rule matches
- **THEN** it is labelled as a sign/attribute, and its options are named after real data (registration number, words in the type name, methodology code, modification)

#### Scenario: Rule table labels
- **WHEN** the user reads the rules of a form
- **THEN** the column that holds the match field is called «признак», not «ось»

#### Scenario: Examples
- **WHEN** the user reads a sign's option
- **THEN** an example of the value is shown (for instance a registration number, a methodology code or a modification)

### Requirement: The graph has a legend

The graph SHALL carry a legend explaining what a circle and a square mean, what a solid line and a
dashed line mean, and what the dashed outline of a node means.

#### Scenario: Legend covers the shapes
- **WHEN** the user looks at the graph
- **THEN** the legend says that circles are forms and squares are rule conditions

#### Scenario: Legend covers the edges
- **WHEN** the user looks at the graph
- **THEN** the legend says that a solid line is inheritance and a dashed line is a rule selecting a form

#### Scenario: Legend covers the outline
- **WHEN** the user looks at the graph
- **THEN** the legend says that a dashed outline marks a form still rendered by an HTML template
