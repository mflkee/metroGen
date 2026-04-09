import { useEffect, useState } from "react";

import { useQuery } from "@tanstack/react-query";

import { sendTestMentionEmail, updateProfile } from "@/api/auth";
import { fetchSystemStatus } from "@/api/system";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAuthStore } from "@/store/auth";
import { defaultVisibleThemes, themeOptions, type ThemeName, useThemeStore } from "@/store/theme";

export function SettingsPage() {
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);
  const setUser = useAuthStore((state) => state.setUser);
  const currentTheme = useThemeStore((state) => state.theme);
  const setTheme = useThemeStore((state) => state.setTheme);
  const [enabledThemes, setEnabledThemes] = useState<ThemeName[]>(
    user?.enabledThemes ?? defaultVisibleThemes,
  );
  const [mentionEmailNotificationsEnabled, setMentionEmailNotificationsEnabled] = useState(
    user?.mentionEmailNotificationsEnabled ?? true,
  );
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSendingTestEmail, setIsSendingTestEmail] = useState(false);

  const statusQuery = useQuery({
    queryKey: ["system-status", "settings"],
    queryFn: () => fetchSystemStatus(token ?? ""),
    enabled: Boolean(token),
  });

  useEffect(() => {
    setEnabledThemes(user?.enabledThemes ?? defaultVisibleThemes);
    setMentionEmailNotificationsEnabled(user?.mentionEmailNotificationsEnabled ?? true);
  }, [user]);

  function toggleTheme(theme: ThemeName) {
    setEnabledThemes((current) => {
      if (current.includes(theme)) {
        if (current.length === 1) {
          return current;
        }
        return current.filter((value) => value !== theme);
      }
      return [...current, theme];
    });
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

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <section className="section-card">
          <h3 className="text-lg font-semibold text-ink">Темы и уведомления</h3>
          <p className="mt-1 text-sm text-steel">
            Доступные темы пользователя хранятся в профиле и синхронизируются между устройствами.
          </p>

          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {themeOptions.map((theme) => (
              <label key={theme.value} className="flex items-start gap-3 rounded-2xl border border-line px-4 py-4 text-sm">
                <input
                  checked={enabledThemes.includes(theme.value)}
                  type="checkbox"
                  onChange={() => toggleTheme(theme.value)}
                />
                <span>
                  <span className="block font-medium text-ink">{theme.label}</span>
                  {theme.source ? <span className="mt-1 block text-xs text-steel">{theme.source}</span> : null}
                </span>
              </label>
            ))}
          </div>

          <label className="mt-5 flex items-center gap-3 rounded-2xl border border-line px-4 py-4 text-sm text-ink">
            <input
              checked={mentionEmailNotificationsEnabled}
              type="checkbox"
              onChange={(event) => setMentionEmailNotificationsEnabled(event.target.checked)}
            />
            Разрешить тестовое SMTP-уведомление на email пользователя
          </label>

          {error ? <p className="mt-4 text-sm text-[#b04c43]">{error}</p> : null}
          {message ? <p className="mt-4 text-sm text-signal-ok">{message}</p> : null}

          <div className="mt-5 flex flex-wrap gap-3">
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
        </section>

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
