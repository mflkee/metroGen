# Spec Delta

## Purpose

Определяет, как metroGen хранит и восстанавливает пользовательский выбор темы (в том числе сделанный
в верхней панели) и как экран настроек держит черновик предпочтений относительно сохранённого
профиля, чтобы выбор пользователя не терялся после перезагрузки и не откатывался самопроизвольно.

## ADDED Requirements

### Requirement: The topbar theme choice is persisted

A theme chosen in the top bar SHALL be stored on the user's profile and SHALL be restored when the
user loads the app again or signs in from another browser. The theme SHALL be applied locally
immediately, even if saving the choice fails.

#### Scenario: Choice survives a reload
- **WHEN** a signed-in user selects a theme in the top bar and reloads the app
- **THEN** the selected theme is applied again after the profile is loaded

#### Scenario: Choice follows the user
- **WHEN** the user signs in from another browser or machine
- **THEN** the top-bar theme reflects the choice stored on the profile

#### Scenario: Save failure keeps the local choice
- **WHEN** persisting the theme choice fails
- **THEN** the theme stays applied locally and the interface does not revert while the session lasts

### Requirement: The topbar picker offers the enabled themes

The top-bar theme picker SHALL offer the themes enabled on the profile, always including the theme
currently in use.

#### Scenario: Narrowed list
- **WHEN** the profile enables a subset of themes
- **THEN** the top-bar picker offers that subset

#### Scenario: Active theme always offered
- **WHEN** the theme in use is not in the enabled subset
- **THEN** the picker still offers the theme in use

### Requirement: Settings are edited as a local draft

The settings screen SHALL keep the enabled-theme list and the notification flag as a local draft
seeded from the profile, and user edits SHALL remain until the user saves or signs in as another user.

#### Scenario: Toggle a theme before saving
- **WHEN** a signed-in user disables or enables a theme in «Темы интерфейса»
- **THEN** the toggle reflects the user's choice immediately

#### Scenario: Saving keeps the chosen values
- **WHEN** the user saves the settings
- **THEN** the toggles keep the values the user chose and a success message is shown

#### Scenario: Draft survives a profile update for the same user
- **WHEN** the profile object in the client store is updated for the same user id (for example after saving)
- **THEN** the settings draft is not reseeded from the profile and the user's edits remain

### Requirement: Draft is reseeded per user

The draft SHALL be seeded from the profile when the settings screen first becomes usable for a
signed-in user, and re-seeded when a different user signs in.

#### Scenario: First usable render
- **WHEN** the settings screen renders with an available profile
- **THEN** the toggles reflect the values persisted in the profile

#### Scenario: Another user signs in
- **WHEN** a different user signs in and opens the settings screen
- **THEN** the draft is seeded from that user's profile

### Requirement: The applied theme is never lost

Reconciling the enabled-theme list with the currently applied theme SHALL only add the applied theme
when it is missing; it SHALL NOT remove or overwrite the user's other choices.

#### Scenario: Disabling the active theme
- **WHEN** the user disables the theme that is currently applied
- **THEN** the applied theme stays available and the rest of the draft is preserved

#### Scenario: Switching theme updates the draft additively
- **WHEN** the top-bar theme changes
- **THEN** the enabled-theme list gains the new active theme without losing the user's other toggles

### Requirement: Saving reports its outcome in place

Saving settings SHALL report success or failure on the settings screen without resetting the draft
on failure.

#### Scenario: Save fails
- **WHEN** the save request fails
- **THEN** an error message is shown and the user's draft is unchanged

#### Scenario: Save succeeds
- **WHEN** the save request succeeds
- **THEN** the profile is updated and a success message is shown
