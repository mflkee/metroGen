# Tasks

## 1. Удалить мёртвые страницы и компоненты

- [x] 1.1 Удалён `frontend/src/pages/ArshinPage.tsx`; запись роута `{ path: "/arshin", element: <Navigate to="/generation" replace /> }` сохранена (её импортов `ArshinPage` не было).
- [x] 1.2 Удалён `frontend/src/components/layout/ThemeSwitcher.tsx`.
- [x] 1.3 Удалён `frontend/src/components/BrandMark.tsx`.

## 2. Убрать неиспользуемые API-обёртки

- [x] 2.1 `frontend/src/api/protocols.ts`: удалены `generateProtocolPdf`, `generateFailedManometerPdf` и ставшие мёртвыми помощники `resolvePdfPath`, `buildPdfPayload`.
- [x] 2.2 `frontend/src/api/system.ts`: удалены `fetchExportFolderFiles`, `deleteExportFiles`. Тип `ExportFile` оставлен — он ещё используется в `ExportFolder.files`/`SystemStatus`.
- [x] 2.3 `frontend/src/api/methodologies.ts`: удалён `fetchMethodology`; `MethodologyUpdatePayload` сделан неэкспортируемым (используется в сигнатуре `updateMethodology`).
- [x] 2.4 `frontend/src/api/users.ts`: удалены `fetchMentionUsers`, `updateUserRole`, типы `UserMention` и внутренний `RawUserMention`.
- [x] 2.5 `frontend/src/api/arshin.ts`: удалены `resolveVriId`, `fetchVriDetails`, `ArshinLookupResult`, `ArshinDetails`; `fetchArshinStatus`/`ArshinStatus` оставлены (индикатор шапки).
- [x] 2.6 `frontend/src/api/registry.ts`: `RegistryImportPayload` сделан неэкспортируемым (есть внутренний потребитель — `importRegistryFile`).
- [x] 2.7 `frontend/src/api/client.ts`: `apiBaseUrl` сделан неэкспортируемой константой.

## 3. Проверка

- [x] 3.1 `cd frontend && npx tsc --noEmit` — зелёный.
- [x] 3.2 `cd frontend && npm run check:ui` — зелёный (вендоренные файлы не тронуты).
- [x] 3.3 `cd frontend && npm run build` — зелёный.
- [x] 3.4 `git grep -n "ArshinPage\|BrandMark\|layout/ThemeSwitcher"` — пусто; удалённые API-символы нигде не встречаются (проверено grep).
- [x] 3.5 Статически подтверждено: `/arshin` остаётся редиректом; `ArshinStatusIndicator` использует сохранённый `fetchArshinStatus`.

## 4. Чистка мёртвых импортов (найдено линтером)

- [x] 4.1 Убраны неиспользуемые импорты: `useEffect` в `AdminOwnersPage.tsx` и `AdminMethodologiesPage.tsx`, `MethodologyPointOut` в `AdminMethodologiesPage.tsx`, `ExportFolder` в `GenerationPage.tsx`.
- [x] 4.2 `cd frontend && npm run lint` — 0 ошибок (остались только 5 warning-ов react-refresh/react-hooks в вендоренных файлах metro-ui, которые править нельзя).
