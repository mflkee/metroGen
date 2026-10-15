# Proposal

## Why

Во фронтенде накопился мёртвый код: страница и компоненты, которые никто не рендерит, и
API-обёртки без вызовов. Он искажает карту проекта (например, `ArshinPage` выглядит рабочей
страницей, хотя роут `/arshin` давно редиректит на `/generation`), тянет ложные зависимости
и мешает оценить реальный объём UI перед рефакторингом списков и CRUD. Это чистый рефакторинг:
поведение системы не меняется, поэтому спеки не затрагиваются.

## What Changes

- Удалить мёртвую страницу `frontend/src/pages/ArshinPage.tsx` (не импортируется нигде).
- Удалить мёртвые локальные компоненты: `frontend/src/components/layout/ThemeSwitcher.tsx`,
  `frontend/src/components/BrandMark.tsx`.
- Удалить неиспользуемые API-обёртки и их типы:
  - `frontend/src/api/protocols.ts`: `generateProtocolPdf`, `generateFailedManometerPdf`;
  - `frontend/src/api/system.ts`: `fetchExportFolderFiles`, `deleteExportFiles`;
  - `frontend/src/api/methodologies.ts`: `fetchMethodology`, `MethodologyUpdatePayload`;
  - `frontend/src/api/users.ts`: `fetchMentionUsers`, `updateUserRole`, `UserMention`;
  - `frontend/src/api/arshin.ts`: `resolveVriId`, `fetchVriDetails`, `ArshinLookupResult`,
    `ArshinDetails` (остаётся `fetchArshinStatus`/`ArshinStatus` — их использует индикатор в шапке);
  - `frontend/src/api/registry.ts`: `RegistryImportPayload` *(если после проверки останется без потребителей)*.
- Сделать `apiBaseUrl` внутренней константой `frontend/src/api/client.ts` (сейчас это мёртвый экспорт).
- Сохранить редирект `/arshin` → `/generation` (глубокие ссылки продолжают работать).

## Capabilities

### New Capabilities

- None — чистое удаление мёртвого кода, spec-level поведение не меняется (`.openspec.yaml`:
  `skip_specs: true`).

### Modified Capabilities

- None.

## Impact

- Только фронтенд (`frontend/src`). Backend, API-контракты, схема БД и вендоренные файлы не меняются.
- Вендоренные файлы из `frontend/fleet-ui.manifest.json` (в т.ч. неиспользуемые
  `mention-text.tsx`, `ui/searchable-select.tsx`, `ui/stat-card.tsx`, `ui/status-badge.tsx`,
  `ui/card.tsx`, `ui/badge.tsx`, `lib/mentions.ts`) НЕ удаляются: их правит только `mflkee/metro-ui`.
- Гейт готовности: `npm run build` (то есть `tsc --noEmit` + `npm run check:ui` + `vite build`).
