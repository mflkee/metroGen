# Spec Delta

## Purpose

Определяет, как страница «Формы протоколов» объясняет себя: что такое форма, по каким признакам она
выбирается и какие подписи видит пользователь.

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

#### Scenario: Rule list labels
- **WHEN** the user reads the rules of a form
- **THEN** the column that holds the match field is called «признак», not «ось», and its values are named after real data (registration number, words in the type name, methodology code, modification)

#### Scenario: Examples
- **WHEN** the user reads a sign
- **THEN** an example of its value is shown (for instance a registration number, a methodology code or a modification)
