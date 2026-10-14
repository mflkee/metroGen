import { useEffect, useRef, useState } from "react";

import { useQuery } from "@tanstack/react-query";

import { sendTestMentionEmail, updateProfile } from "@/api/auth";
import { fetchSystemStatus } from "@/api/system";
import { PageHeader } from "@/components/ui/page-header";
import { SettingsSection } from "@/components/ui/settings-section";
import { Switch } from "@/components/ui/switch";
import { useAuthStore } from "@/store/auth";
import { defaultVisibleThemes, getVisibleThemes, themeOptions, type ThemeName, useThemeStore } from "@/store/theme";

export function SettingsPage() {
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);
  const setUser = useAuthStore((state) => state.setUser);
  const currentTheme = useThemeStore((state) => state.theme);
  const setTheme = useThemeStore((state) => state.setTheme);
  const [enabledThemes, setEnabledThemes] = useState<ThemeName[]>(
    getVisibleThemes(user?.enabledThemes ?? defaultVisibleThemes, currentTheme),
  );
  const [mentionEmailNotificationsEnabled, setMentionEmailNotificationsEnabled] = useState(
    user?.mentionEmailNotificationsEnabled ?? true,
  );
  const [error, setError] = useState<string | null>(null);  const [expandedSections, setExpandedSections] = useState<Record<"themes" | "notifications", boolean>>({
    themes: true,
    notifications: true,
  });

  function toggleSection(section: "themes" | "notifications") {
    setExpandedSections((current) => ({ ...current, [section]: !current[section] }));
  }


  const [message, setMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSendingTestEmail, setIsSendingTestEmail] = useState(false);

  const statusQuery = useQuery({
    queryKey: ["system-status", "settings"],
    queryFn: () => fetchSystemStatus(token ?? ""),
    enabled: Boolean(token),
  });

  // The draft is seeded from the profile once per signed-in user. Keying on `user.id` keeps the
  // user's edits when the store hands back a new object for the same user (e.g. after saving).
  const hydratedUserIdRef = useRef<number | null>(null);

  useEffect(() => {
    if (!user) {
      hydratedUserIdRef.current = null;
      return;
    }
    if (hydratedUserIdRef.current === user.id) {
      return;
    }
    hydratedUserIdRef.current = user.id;
    setEnabledThemes(getVisibleThemes(user.enabledThemes ?? defaultVisibleThemes, currentTheme));
    setMentionEmailNotificationsEnabled(user.mentionEmailNotificationsEnabled ?? true);
  }, [currentTheme, user]);

  // The applied theme is never dropped: reconcile the list additively, so disabling some themes
  // does not undo a switch made in the top bar and vice versa.
  useEffect(() => {
    setEnabledThemes((current) => getVisibleThemes(current, currentTheme));
  }, [currentTheme]);

  /**
   * The theme switches save right away: a theme is a preference, not a draft, and the «Сохранить»
   * button lives in the notifications section — leaving the choice unsaved made it look lost.
   */
  function toggleTheme(theme: ThemeName) {
    if (enabledThemes.includes(theme) && enabledThemes.length === 1) {
      return;
    }
    const next = enabledThemes.includes(theme)
      ? enabledThemes.filter((value) => value !== theme)
      : [...enabledThemes, theme];
    setEnabledThemes(next);
    void persistThemeSelection(next);
  }

  async function persistThemeSelection(themes: ThemeName[]) {
    if (!token) {
      setError("Сессия неактивна. Войди заново.");
      return;
    }
    setError(null);
    try {
      const nextTheme = themes.includes(currentTheme)
        ? currentTheme
        : themes[0] ?? defaultVisibleThemes[0];
      if (nextTheme !== currentTheme) {
        setTheme(nextTheme);
      }
      const updatedUser = await updateProfile(token, {
        enabledThemes: themes,
        themePreference: nextTheme,
      });
      setUser(updatedUser);
      setMessage("Список тем сохранён.");
    } catch (submitError) {
      setError(
        submitError instanceof Error ? submitError.message : "Не удалось сохранить список тем.",
      );
    }
  }

  async function handleSave() {
    if (!token) {
      setError("Сессия неактивна. Войди заново.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setMessage(null);

    try {
      const nextTheme = enabledThemes.includes(currentTheme)
        ? currentTheme
        : enabledThemes[0] ?? defaultVisibleThemes[0];
      if (nextTheme !== currentTheme) {
        setTheme(nextTheme);
      }
      const updatedUser = await updateProfile(token, {
        mentionEmailNotificationsEnabled,
        enabledThemes,
        themePreference: nextTheme,
      });
      setUser(updatedUser);
      setMessage("Настройки сохранены.");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Не удалось сохранить настройки.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleSendTestEmail() {
    if (!token) {
      return;
    }
    setIsSendingTestEmail(true);
    setError(null);
    setMessage(null);
    try {
      const response = await sendTestMentionEmail(token);
      setMessage(response.message);
    } catch (submitError) {
      setError(
        submitError instanceof Error ? submitError.message : "Не удалось отправить тестовое письмо.",
      );
    } finally {
      setIsSendingTestEmail(false);
    }
  }

  return (
    <section>
      <PageHeader
        title="Настройки"
        description="Панель тем и рабочих параметров пользователя. SMTP-часть вынесена сюда же, чтобы metroGen ощущался как полноценное приложение, а не только backend-утилита."
      />

      {error ? <p className="text-sm text-[var(--danger-text)]">{error}</p> : null}
      {message ? <p className="text-sm text-signal-ok">{message}</p> : null}

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-4">
          <SettingsSection
            description="Темы, доступные в верхней панели. Переключатель сохраняется сразу."
            expanded={expandedSections.themes}
            title="Темы интерфейса"
            onToggle={() => toggleSection("themes")}
          >
            <div className="grid gap-3 sm:grid-cols-2">
              {themeOptions.map((theme) => (
                <label
                  key={theme.value}
                  className="flex items-center gap-3 rounded-2xl border border-line px-4 py-4 text-sm"
                  htmlFor={`theme-${theme.value}`}
                >
                  <Switch
                    checked={enabledThemes.includes(theme.value)}
                    id={`theme-${theme.value}`}
                    onCheckedChange={() => toggleTheme(theme.value)}
                  />
                  <span className="block font-medium text-ink">{theme.label}</span>
                </label>
              ))}
            </div>
          </SettingsSection>

          <SettingsSection
            description="Письмо на твой адрес, когда тебя упомянут в обсуждении."
            expanded={expandedSections.notifications}
            title="Уведомления"
            onToggle={() => toggleSection("notifications")}
          >
            <label className="flex items-center gap-3 text-sm text-ink" htmlFor="mention-email">
              <Switch
                checked={mentionEmailNotificationsEnabled}
                id="mention-email"
                onCheckedChange={setMentionEmailNotificationsEnabled}
              />
              Разрешить тестовое SMTP-уведомление на email пользователя
            </label>
            <div className="flex flex-wrap gap-3">
              <button className="btn-primary" disabled={isSubmitting} type="button" onClick={() => void handleSave()}>
                {isSubmitting ? "Сохраняем..." : "Сохранить"}
              </button>
              <button
                className="btn-secondary"
                disabled={!statusQuery.data?.smtpConfigured || isSendingTestEmail}
                type="button"
                onClick={() => void handleSendTestEmail()}
              >
                {isSendingTestEmail ? "Отправляем..." : "Тестовое письмо"}
              </button>
            </div>
          </SettingsSection>
        </div>

        <aside className="section-card">
          <h3 className="text-lg font-semibold text-ink">Статус окружения</h3>
          <div className="mt-4 space-y-4 text-sm">
            <div className={["status-chip", statusQuery.data?.smtpConfigured ? "status-chip--ok" : "status-chip--warn"].join(" ")}>
              SMTP: {statusQuery.data?.smtpConfigured ? "настроен" : "не задан"}
            </div>
            <div className={["status-chip", statusQuery.data?.pdfGenerationAvailable ? "status-chip--ok" : "status-chip--warn"].join(" ")}>
              PDF: {statusQuery.data?.pdfGenerationAvailable ? "готов" : "требует браузер"}
            </div>
            <div>
              <div className="text-xs uppercase tracking-[0.16em] text-steel">Exports Dir</div>
              <div className="mt-1 break-all text-ink">{statusQuery.data?.exportsDir ?? "..."}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-[0.16em] text-steel">Signatures Dir</div>
              <div className="mt-1 break-all text-ink">{statusQuery.data?.signaturesDir ?? "..."}</div>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
