# Tasks

## 1. metro-ui: проброс темы в `account-menu`

- [x] 1.1 В `~/projects/metro-ui/registry/account-menu/account-menu.tsx` добавить необязательные пропсы `themes?: ThemeName[]` и `onThemeChange?: (theme: ThemeName) => void`; передать их в оба `<ThemeSwitcher />` (шапка и диалог аккаунта).
- [x] 1.2 `cd ~/projects/metro-ui && npm run build` — обновить `public/r/account-menu.json`, проверки `check-registry` зелёные.

## 2. metroGen: ревендор и сохранение темы из шапки

- [x] 2.1 Обновить `frontend/src/components/account-menu.tsx` содержимым из metro-ui (`public/r/account-menu.json`); запустить `npm run check:ui -- manifest` (в манифесте изменился только хеш `account-menu.tsx`).
- [x] 2.2 `frontend/src/components/layout/AccountMenu.tsx`: получить `theme` из `useThemeStore`, вычислить `getVisibleThemes(user?.enabledThemes, theme)` и передать `themes`/`onThemeChange` в флитовый `AccountMenu`; обработчик пишет `themePreference` через `updateProfile` и применяет ответ через `setUser`.
- [x] 2.3 Тема применяется локально даже при ошибке запроса (обработчик не откатывает тему сам).

## 3. metroGen: черновик настроек

- [x] 3.1 `frontend/src/pages/SettingsPage.tsx`: добавлен `hydratedUserIdRef`, эффект гидратации выполняется один раз на `user.id`; импортирован `getVisibleThemes`.
- [x] 3.2 Начальное значение `enabledThemes` — через `getVisibleThemes(..., currentTheme)`.
- [x] 3.3 Согласование с активной темой — отдельный аддитивный эффект по `[currentTheme]`.
- [x] 3.4 `handleSave` при ошибке не сбрасывает черновик, при успехе показывает сообщение (проверено чтением кода; гарантируется guard-ом гидратации).

## 4. metroLog: тот же фикс (смежный сервис)

- [x] 4.1 Обновлены вендоренный `src/components/account-menu.tsx` и `src/components/layout/AccountMenu.tsx` в `~/projects/metroLog/frontend` (та же схема сохранения через `updateProfile`); `npm run check:ui -- manifest` пересчитал только хеш `account-menu.tsx`.
- [ ] 4.2 Ручная проверка на metroLog: выбор темы в шапке переживает перезагрузку. *(build зелёный; ручная проверка — на стенде)*

## 5. Проверка

- [x] 5.1 `cd frontend && npx tsc --noEmit` — зелёный.
- [x] 5.2 `cd frontend && npm run check:ui` — зелёный (28 вендоренных файлов, хеши совпадают, хардкода цветов нет).
- [x] 5.3 `cd frontend && npm run build` — зелёный; `npm run build` в metroLog — тоже зелёный.
- [ ] 5.4 Ручной прогон: тема из шапки → перезагрузка → сохранилась; вход с другой машины → та же тема.
- [ ] 5.5 Ручной прогон: выключить тему → «Сохранить» → тумблеры не откатились; выключить активную тему → она осталась в списке.
