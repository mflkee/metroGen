# Spec Delta

## Purpose

Определяет, как пользователь взаимодействует с графом зависимостей форм: перетаскивание узлов, зум и
пан, наведение, поиск и фильтры, выбор формы — и какие побочные эффекты недопустимы.

## ADDED Requirements

### Requirement: Nodes can be dragged

The graph SHALL let the user drag a node to a new position, so a dense cluster can be pulled apart by
hand.

#### Scenario: Drag a node
- **WHEN** the user drags a node
- **THEN** that node follows the pointer while the rest of the graph reacts

#### Scenario: Re-layout
- **WHEN** the user asks to re-layout the graph
- **THEN** the nodes return to a freshly computed arrangement

### Requirement: Zoom and pan are predictable

Zoom SHALL happen around the pointer, and panning SHALL move the graph with the pointer. The graph
SHALL NOT swallow the page's own scrolling.

#### Scenario: Zoom at the pointer
- **WHEN** the user scrolls over the graph
- **THEN** the graph zooms around the pointer position

#### Scenario: Pan
- **WHEN** the user drags the background
- **THEN** the whole graph moves with the pointer

#### Scenario: Page scrolling is not hijacked
- **WHEN** the user scrolls the page with the pointer outside the graph
- **THEN** the page scrolls normally

### Requirement: Hover and selection are visible

Hovering a node SHALL highlight it together with its immediate neighbours and dim the rest; clicking a
node SHALL select the form and open its card.

#### Scenario: Hover
- **WHEN** the pointer is over a node
- **THEN** that node, its links and its neighbours stand out and unrelated nodes are dimmed

#### Scenario: Click
- **WHEN** the user clicks a form node
- **THEN** that form becomes selected and its card is shown

#### Scenario: Click a condition
- **WHEN** the user clicks a condition node (a rule)
- **THEN** the graph does not change the selected form

### Requirement: Search and filters still apply

The graph SHALL keep the existing search and filters: matches are highlighted, hidden rules remove
their edges, and the instrument-kind filter narrows the graph.

#### Scenario: Search highlights
- **WHEN** the user types into the search box
- **THEN** matching nodes are highlighted and the graph is focused on them

#### Scenario: Filters
- **WHEN** the user filters by instrument kind or by axis, or hides disabled rules
- **THEN** only the matching forms and conditions remain in the graph

### Requirement: Forms and conditions stay distinguishable

A form node SHALL be distinguishable from a condition node, and a base form from a derived one; a form
that is still rendered by an HTML template SHALL be marked as such.

#### Scenario: Visual distinction
- **WHEN** the graph renders
- **THEN** base forms, derived forms and conditions are visually distinct

#### Scenario: Template-rendered form
- **WHEN** a form is still rendered by an HTML template
- **THEN** its node carries a visible marker (for example a dashed outline)
