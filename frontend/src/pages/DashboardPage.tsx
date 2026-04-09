import { useState } from "react";
import { Link } from "react-router-dom";

import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "@/components/layout/PageHeader";
import { fetchExportFile, fetchSystemStatus } from "@/api/system";
import { useAuthStore } from "@/store/auth";

export function DashboardPage() {
  const token = useAuthStore((state) => state.token);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const statusQuery = useQuery({
    queryKey: ["system-status"],
    queryFn: () => fetchSystemStatus(token ?? ""),
    enabled: Boolean(token),
  });

  async function openExport(path: string) {
    if (!token) {
      return;
    }
    setDownloadError(null);
    try {
      const blob = await fetchExportFile(token, path);
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank", "noopener,noreferrer");
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (error) {
      setDownloadError(error instanceof Error ? error.message : "Не удалось открыть файл.");
    }
  }

  const status = statusQuery.data;

  return (
    <section>
      <PageHeader
        title="Главная"
        description="Стартовая панель metroGen: быстрый переход к генерации, состояние приложения и последние экспортированные протоколы."
        action={<Link className="btn-primary" to="/generation">Открыть генерацию</Link>}
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <article className="metric-card">
          <div className="metric-card__label">Папки экспорта</div>
          <div className="metric-card__value">{status?.exportFoldersCount ?? "..."}</div>
        </article>
        <article className="metric-card">
          <div className="metric-card__label">Файлы в выдаче</div>
          <div className="metric-card__value">{status?.generatedFilesCount ?? "..."}</div>
        </article>
        <article className="metric-card">
          <div className="metric-card__label">Пользователи</div>
          <div className="metric-card__value">{status?.usersCount ?? "..."}</div>
        </article>
        <article className="metric-card">
          <div className="metric-card__label">PDF-движок</div>
          <div className="metric-card__value">
            {status ? (status.pdfGenerationAvailable ? "Готов" : "Нет") : "..."}
          </div>
        </article>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.9fr)]">
        <section className="section-card">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold text-ink">Последние экспорты</h3>
              <p className="mt-1 text-sm text-steel">
                Последние папки генерации и файлы, которые уже можно открыть из интерфейса.
              </p>
            </div>
            {status ? (
              <div className={["status-chip", status.pdfGenerationAvailable ? "status-chip--ok" : "status-chip--danger"].join(" ")}>
                {status.pdfGenerationAvailable ? "Playwright готов" : "Нужно установить Chromium"}
              </div>
            ) : null}
          </div>
          {downloadError ? <p className="mt-4 text-sm text-[#b04c43]">{downloadError}</p> : null}
          <div className="mt-5 space-y-4">
            {statusQuery.isLoading ? (
              <p className="text-sm text-steel">Загружаем сводку экспортов...</p>
            ) : null}
            {status?.recentExports.length ? (
              status.recentExports.map((folder) => (
                <article key={folder.path} className="tone-child rounded-3xl border border-line p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h4 className="text-base font-semibold text-ink">{folder.name}</h4>
                      <p className="mt-1 text-xs text-steel">
                        {folder.filesCount} файлов · {formatDateTime(folder.modifiedAt)}
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    {folder.files.map((file) => (
                      <div
                        key={file.path}
                        className="flex flex-col gap-2 rounded-2xl border border-line px-3 py-3 sm:flex-row sm:items-center sm:justify-between"
                      >
                        <div className="min-w-0">
                          <div className="truncate text-sm font-medium text-ink">{basename(file.path)}</div>
                          <div className="mt-1 text-xs text-steel">
                            {formatSize(file.sizeBytes)} · {formatDateTime(file.modifiedAt)}
                          </div>
                        </div>
                        <button className="btn-secondary btn-sm shrink-0" type="button" onClick={() => void openExport(file.path)}>
                          Открыть
                        </button>
                      </div>
                    ))}
                  </div>
                </article>
              ))
            ) : statusQuery.isLoading ? null : (
              <p className="text-sm text-steel">Пока нет экспортов. Сгенерируйте первый пакет на странице «Генерация».</p>
            )}
          </div>
        </section>

        <aside className="section-card">
          <h3 className="text-lg font-semibold text-ink">Состояние приложения</h3>
          <div className="mt-4 flex flex-wrap gap-2">
            {status ? (
              <>
                <div className={["status-chip", status.smtpConfigured ? "status-chip--ok" : "status-chip--warn"].join(" ")}>
                  SMTP: {status.smtpConfigured ? "настроен" : "не задан"}
                </div>
                <div className={["status-chip", status.pdfGenerationAvailable ? "status-chip--ok" : "status-chip--warn"].join(" ")}>
                  PDF: {status.pdfGenerationAvailable ? "доступен" : "требует setup"}
                </div>
              </>
            ) : null}
          </div>
          <div className="mt-5 space-y-4 text-sm text-steel">
            <div>
              <div className="text-xs uppercase tracking-[0.16em]">Exports Dir</div>
              <div className="mt-1 break-all text-ink">{status?.exportsDir ?? "..."}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-[0.16em]">Signatures Dir</div>
              <div className="mt-1 break-all text-ink">{status?.signaturesDir ?? "..."}</div>
            </div>
            <div className="pt-2">
              <Link className="btn-secondary" to="/settings">Открыть настройки</Link>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString("ru-RU");
}

function formatSize(value: number): string {
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function basename(value: string): string {
  return value.split(/[\\/]/).pop() ?? value;
}
