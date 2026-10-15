# Design

## Context

См. `proposal.md` — Why. Инвентаризация получена по факту: для каждого кандидата проверено,
что за пределами его собственного файла нет ни одного import/вызова.

Соглашение проекта: вендоренные файлы (`frontend/fleet-ui.manifest.json`) неприкосновенны, а
сборка падает на `npm run check:ui`, если тронуть вендоренный файл или хардкодить цвет.

## Goals / Non-Goals

**Goals:**

- Убрать из `frontend/src` код без потребителей, чтобы он не вводил в заблуждение.
- Не изменить ни одного пользовательского сценария и ни одного API-контракта.
- Зафиксировать способ проверки «мёртвости», чтобы ревизия была воспроизводимой.

**Non-Goals:**

- Не удалять и не править вендоренные файлы metro-ui (даже неиспользуемые).
- Не переписывать `ArshinPage` в рабочую страницу — если диагностическая панель Аршина вернётся,
  она приходит отдельным change со своей capability.
- Не менять backend и не удалять неиспользуемые backend-ручки (`/resolve/vri-id`, `/resolve/vri/{id}`
  остаются доступными по API).

## Decisions

### D1: Удаляем страницу, но сохраняем редирект

`ArshinPage` не импортируется нигде (`router.tsx:81` монтирует только
`<Navigate to="/generation" replace />`). Удаляем `src/pages/ArshinPage.tsx`, но оставляем запись
роута `/arshin` — она сохраняет работу старых ссылок и не требует решения о судьбе раздела.

### D2: `api/arshin.ts` урезаем, а не удаляем

`fetchArshinStatus` используется индикатором шапки (`components/layout/ArshinStatusIndicator.tsx:5`).
Удаляем только `resolveVriId`, `fetchVriDetails` и их типы — они вызывались лишь со страницы Аршина.

### D3: Вендоренные «сироты» вне scope

`mention-text.tsx`, `ui/searchable-select.tsx`, `ui/stat-card.tsx`, `ui/status-badge.tsx`,
`ui/card.tsx`, `ui/badge.tsx`, `lib/mentions.ts` не используются, но перечислены в манифесте
`fleet-ui` — их удаление сломает `npm run check:ui`. Если чистка нужна и там, её делают в
`mflkee/metro-ui` (убрать item из registry), а сервис пересобирает манифест.

### D4: `markAnonymous`/`clearSession` не трогаем

В `store/auth.ts` они совпадают по телу, но оба вызываются (`App.tsx:34`,
`GenerationPage.tsx`, `layout/AccountMenu.tsx`) — это не мёртвый код, переиспользование
оставляем как есть (вне scope).

## Inventory (evidence)

| Что удаляем | Где | Доказательство |
|---|---|---|
| `ArshinPage.tsx` | `src/pages/ArshinPage.tsx` | роут `/arshin` = redirect (`router.tsx:81`), импортов нет |
| `layout/ThemeSwitcher.tsx` | `src/components/layout/` | 0 импортов; шапка рендерит вендоренный `components/account-menu` → `@/components/theme-switcher` |
| `BrandMark.tsx` | `src/components/` | 0 импортов |
| `generateProtocolPdf`, `generateFailedManometerPdf` | `src/api/protocols.ts:103,177` | `GenerationPage` использует только `startGenerationJob`/`fetchHtmlPreview` |
| `fetchExportFolderFiles`, `deleteExportFiles` | `src/api/system.ts:139,151` | 0 импортов |
| `fetchMethodology`, `MethodologyUpdatePayload` | `src/api/methodologies.ts:10,38` | 0 импортов |
| `fetchMentionUsers`, `updateUserRole`, `UserMention` | `src/api/users.ts:23,63,118` | 0 импортов |
| `resolveVriId`, `fetchVriDetails` + типы | `src/api/arshin.ts:3,10,19,29` | единственный потребитель — удаляемый `ArshinPage.tsx` |
| `apiBaseUrl` (экспорт) | `src/api/client.ts:3` | используется только внутри модуля |

## Risks / Trade-offs

- [Удалим что-то, что на самом деле использовалось динамически] → dynamic import в проекте не
  применяется к этим символам; проверка — `tsc --noEmit` падает при любом оставшемся импорте.
- [`RegistryImportPayload` окажется нужен] → решение принимается на шаге проверки: если после
  удаления неиспользуемых вызовов тип ещё кем-то импортируется, он остаётся.
- [Сломаем сборку из-за вендоренного файла] → в задачу входит прогон `npm run check:ui` до и после;
  удаляются только не вендоренные пути.

## Verification

1. `grep -rn "<symbol>" frontend/src` для каждого удаляемого символа — 0 совпадений вне его файла.
2. `npm run build` в `frontend/` — зелёный (включая `check:ui`).
3. `git grep -l "ArshinPage"` — пусто.
