# Spec Delta

## Purpose

Определяет, как metroGen хранит и восстанавливает пользовательский выбор темы (в том числе
сделанный в верхней панели), как список доступных тем управляется из настроек и как черновик
остальных предпочтений сосуществует с профилем.

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

### Requirement: Theme visibility is saved on toggle

Toggling a theme in «Темы интерфейса» SHALL persist the enabled-theme list on the profile at once,
so the choice survives a reload and appears in the top-bar picker without pressing a separate save
button (which lives in another section and was easy to miss).

#### Scenario: Enable a theme
- **WHEN** a signed-in user enables a theme
- **THEN** the profile's enabled-theme list is updated immediately and the theme appears in the top-bar picker

#### Scenario: Disable a theme
- **WHEN** a signed-in user disables a theme
- **THEN** the profile's enabled-theme list is updated immediately

#### Scenario: State survives a reload
- **WHEN** the user reloads after toggling a theme
- **THEN** the switch keeps the value the user chose

#### Scenario: The last theme cannot be disabled
- **WHEN** only one theme is enabled and the user tries to disable it
- **THEN** the toggle does not change (at least one theme stays available)

#### Scenario: Save failure
- **WHEN** persisting a toggle fails
- **THEN** an error is reported and the next profile load shows the persisted state

### Requirement: The topbar picker offers the enabled themes

The top-bar theme picker SHALL offer the themes enabled on the profile, always including the theme
currently in use.

#### Scenario: Narrowed list
- **WHEN** the profile enables a subset of themes
- **THEN** the top-bar picker offers that subset

#### Scenario: Active theme always offered
- **WHEN** the theme in use is not in the enabled subset
- **THEN** the picker still offers the theme in use

### Requirement: Notification settings are edited as a local draft

The notification flag SHALL be a local draft applied by «Сохранить», seeded once per signed-in user,
and SHALL NOT be reseeded when the profile object is updated for the same user.

#### Scenario: Draft survives a profile update for the same user
- **WHEN** the profile object in the client store is updated for the same user id
- **THEN** the notification draft is not reseeded from the profile and the user's edit remains

#### Scenario: Draft is reseeded per user
- **WHEN** a different user signs in and opens the settings screen
- **THEN** the draft is seeded from that user's profile

### Requirement: The applied theme is never lost

Reconciling the enabled-theme list with the currently applied theme SHALL only add the applied theme
when it is missing; it SHALL NOT remove or overwrite the user's other choices.

#### Scenario: Disabling the active theme
- **WHEN** the user disables the theme that is currently applied
- **THEN** the applied theme stays available and the rest of the draft is preserved

#### Scenario: Switching theme updates the list additively
- **WHEN** the top-bar theme changes
- **THEN** the enabled-theme list gains the new active theme without losing the user's other choices

### Requirement: Saving reports its outcome in place

Saving settings SHALL report success or failure on the settings screen without resetting the draft
on failure.

#### Scenario: Save fails
- **WHEN** the save request fails
- **THEN** an error message is shown and the user's draft is unchanged

#### Scenario: Save succeeds
- **WHEN** the save request succeeds
- **THEN** the profile is updated and a success message is shown
