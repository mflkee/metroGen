# Design

## Context

См. `proposal.md` — Why. Две независимые причины, один корневой инвариант: **профиль — источник
истины при загрузке**, а запись в профиль есть только у экрана настроек.

Текущее состояние (одинаково в metroGen и metroLog):

- `frontend/src/store/auth.ts` — `setSession`/`setUser` вызывают
  `syncThemeFromUser(user.themePreference)` (metroGen `auth.ts:56,65`; metroLog `auth.ts:59,68`).
  Значит при каждом обновлении профиля применённая тема переустанавливается из профиля.
- `src/store/theme.ts:71-73` — `syncThemeFromUser(p) = persistAndApplyTheme(coerceThemePreference(p) ?? getStoredTheme())`,
  то есть `null` в профиле сохраняет локальный выбор, а любое значение — перетирает его.
- Вендоренный `src/components/account-menu.tsx` рендерит `<ThemeSwitcher />` **без** пропсов
  (дважды: в шапке и внутри диалога аккаунта), поэтому выбор из верхней панели не уходит в профиль.
- `theme-switcher.tsx` уже умеет `themes` и `onChange` — не хватает только проброса из `account-menu`.
- metroLog содержит **готовый, но неиспользуемый** `components/layout/ThemeSwitcher.tsx`, который
  сохраняет выбор через `updateProfile`; он не подключён, потому что верхнюю панель собирает
  флитовый `account-menu`.

Экран настроек (metroGen):

```tsx
19:  const [enabledThemes, setEnabledThemes] = useState<ThemeName[]>(user?.enabledThemes ?? defaultVisibleThemes);
45:  useEffect(() => {
46:    setEnabledThemes(user?.enabledThemes ?? defaultVisibleThemes);
47:    setMentionEmailNotificationsEnabled(user?.mentionEmailNotificationsEnabled ?? true);
48:  }, [user]);
84:  setUser(updatedUser);   // ← новая ссылка на user → эффект сбрасывает черновик
```

Эталон — metroLog `SettingsPage.tsx:154,192-210`: гидратация один раз на `user.id`
(`hydratedUserIdRef`) плюс отдельный аддитивный эффект согласования с активной темой.

## Goals / Non-Goals

**Goals:**

- Выбор темы где угодно (верхняя панель или настройки) сохраняется в профиль и переживает
  перезагрузку и вход с другой машины.
- Пикер верхней панели предлагает включённые темы (плюс активную).
- Черновик настроек не откатывается при обновлении профиля тем же пользователем.

**Non-Goals:**

- Не менять контракт `PATCH /auth/me` и модель пользователя.
- Не редактировать сами HTML/CSS-токены тем.
- Не вводить тестовый раннер во фронтенд metroGen (см. Open Questions).

## Decisions

### D1: Проброс темы через флитовый `account-menu` (правка в metro-ui)

`registry/account-menu/account-menu.tsx` получает два сквозных пропса и передаёт их в оба
`<ThemeSwitcher />`:

```tsx
type AccountMenuProps = {
  // …
  /** Themes to offer in the picker; defaults to the whole catalogue. */
  themes?: ThemeName[]
  /** Called after the theme is applied — a service persists it on the profile. */
  onThemeChange?: (theme: ThemeName) => void
}
// …
<ThemeSwitcher onChange={onThemeChange} themes={themes} />
```

`theme-switcher` уже поддерживает обе опции — менять его не нужно.

*Альтернатива A:* сервис рендерит свой пикер рядом с `account-menu`. Отклонено — флитовый
`account-menu` всё равно рендерит встроенный пикер, получится дубль.
*Альтернатива B:* считать localStorage источником истины и не просеивать из профиля. Отклонено —
тема перестанет переноситься между браузерами/машинами, а профиль останется рассинхронизированным.

### D2: Сохранение — на стороне сервиса

`layout/AccountMenu.tsx` (metroGen) и `layout/AccountMenu.tsx` (metroLog) передают:

```tsx
const theme = useThemeStore((s) => s.theme);
const themes = getVisibleThemes(user?.enabledThemes, theme);
async function handleThemeChange(next: ThemeName) {
  if (!token || !user || user.themePreference === next) return;
  try { setUser(await updateProfile(token, { themePreference: next })); } catch { /* тема уже применена локально */ }
}
// <FleetAccountMenu … themes={themes} onThemeChange={(t) => void handleThemeChange(t)} />
```

Тема применяется локально до запроса (это уже делает `theme-switcher`), поэтому неудачное
сохранение не оставляет пользователя без темы.

### D3: Гидратация черновика настроек один раз на пользователя

```tsx
const hydratedUserIdRef = useRef<number | null>(null);

useEffect(() => {
  if (!user) { hydratedUserIdRef.current = null; return; }
  if (hydratedUserIdRef.current === user.id) return; // не перезаписывать черновик
  hydratedUserIdRef.current = user.id;
  setEnabledThemes(getVisibleThemes(user.enabledThemes ?? defaultVisibleThemes, currentTheme));
  setMentionEmailNotificationsEnabled(user.mentionEmailNotificationsEnabled ?? true);
}, [currentTheme, user]);
```

*Альтернатива:* завязать эффект на отдельные поля — хрупко и всё равно сработает после `setUser`.

### D4: Согласование с активной темой — отдельно и аддитивно

```tsx
useEffect(() => {
  setEnabledThemes((current) => getVisibleThemes(current, currentTheme));
}, [currentTheme]);
```

`getVisibleThemes` (`store/theme.ts:44-65`) только добавляет активную тему, если её нет, и
дедуплицирует, поэтому `catppuccin` из верхней панели не отменяет отключение других тем.

### D5: Начальное значение черновика — через `getVisibleThemes`

`useState` тоже перевести на `getVisibleThemes(user?.enabledThemes ?? defaultVisibleThemes, currentTheme)`,
чтобы активная, но не включённая в профиле тема сразу была видна.

### D6: Ревендоринг и манифест

После правки metro-ui: `shadcn build` в metro-ui → обновить
`frontend/src/components/account-menu.tsx` в сервисе → `npm run check:ui -- manifest`. Гард
`fleet-ui` не даст забыть пересчитать хеши.

## Risks / Trade-offs

- [Правка флитового компонента задевает metroCheck/другие сервисы] → изменения аддитивные
  (необязательные пропсы), поведение без них прежнее; metroCheck просто не передаёт колбэк.
- [Guard по `user.id` скроет смену профиля тем же пользователем с другого устройства] → для
  настроек это ожидаемо: черновик — выбор пользователя, применяется по кнопке.
- [Аддитивное согласование не даёт «выключить» активную тему] → так и задумано (нельзя остаться без
  темы); зафиксировано в спеке.
- [Гонка: пользователь меняет тему в шапке, идёт `updateProfile`, параллельно грузится `/auth/me`] →
  оба ответа несут `themePreference`, а `syncThemeFromUser` идемпотентен; последний ответ побеждает,
  и это тот же выбор.

## Verification

- `npx tsc --noEmit`, `npm run check:ui`, `npm run build` в `frontend/` — зелёные.
- Ручной прогон на stage: выбрать тему в верхней панели → перезагрузить → тема сохранилась; войти
  с другой машины → та же тема; в настройках выключить тему → «Сохранить» → тумблеры не откатились;
  выключить активную тему → она осталась в списке.

## Open Questions

- Нужен ли во фронтенде metroGen тестовый раннер (vitest + Testing Library, как в metroLog), чтобы
  покрыть сценарий компонентным тестом? Сейчас его нет; введение — отдельный change.
