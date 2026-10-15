# Spec Delta

## MODIFIED Requirements

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
