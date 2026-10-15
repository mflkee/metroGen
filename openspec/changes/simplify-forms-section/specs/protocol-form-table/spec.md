# Spec Delta

## REMOVED Requirements

### Requirement: The editor edits titles and sources

**Reason**: the form editor leaves the interface — the section becomes a read-only overview, and editing
a column's title or source is no longer offered there.

**Migration**: a column still carries a title and a value source, and the table is still rendered from
the structure (the requirements above); changing them happens through the API, as with the rest of the
structure.
