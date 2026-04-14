import { Link } from "react-router-dom";

import { useQuery } from "@tanstack/react-query";

import { fetchSystemStatus } from "@/api/system";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAuthStore } from "@/store/auth";

export function DashboardPage() {
  const token = useAuthStore((state) => state.token);
  const statusQuery = useQuery({
    queryKey: ["system-status"],
    queryFn: () => fetchSystemStatus(token ?? ""),
    enabled: Boolean(token),
  });

  const status = statusQuery.data;

  return (
    <section className="space-y-6">
      <PageHeader
        title="Главная"
        description="Стартовая панель metroGen: состояние приложения, база данных и быстрый переход к рабочим разделам."
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
          <div className="metric-card__label">Активный реестр</div>
          <div className="metric-card__value">{status?.database.activeRegistryEntriesCount ?? "..."}</div>
        </article>
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(320px,0.9fr)]">
        <section className="section-card">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold text-ink">Рабочие разделы</h3>
              <p className="mt-1 text-sm text-steel">
                Основной поток теперь сосредоточен на странице генерации: запуск run, живой статус,
                готовый ZIP и ошибки по строкам в одном месте.
              </p>
            </div>
            {status ? (
              <div className={["status-chip", status.pdfGenerationAvailable ? "status-chip--ok" : "status-chip--danger"].join(" ")}>
                {status.pdfGenerationAvailable ? "PDF-движок готов" : "Нужно установить Chromium"}
              </div>
            ) : null}
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <Link className="rounded-3xl border border-line p-5 transition hover:bg-[color:var(--tone-child-bg)]" to="/generation">
              <div className="text-base font-semibold text-ink">Генерация</div>
              <p className="mt-2 text-sm text-steel">
                Batch-PDF, HTML-превью, живой прогресс и доступ к готовому ZIP после завершения.
              </p>
            </Link>
            <Link className="rounded-3xl border border-line p-5 transition hover:bg-[color:var(--tone-child-bg)]" to="/generation">
              <div className="text-base font-semibold text-ink">База данных</div>
              <p className="mt-2 text-sm text-steel">
                Импорт реестра, проверка состояния справочников и фильтруемая таблица записей.
              </p>
            </Link>
            <Link className="rounded-3xl border border-line p-5 transition hover:bg-[color:var(--tone-child-bg)]" to="/generation">
              <div className="text-base font-semibold text-ink">Готовые генерации</div>
              <p className="mt-2 text-sm text-steel">
                История run-папок, повторное скачивание ZIP и доступ к отдельным PDF.
              </p>
            </Link>
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
              <div className="text-xs uppercase tracking-[0.16em]">Database</div>
              <div className="mt-1 text-ink">
                {status?.database.backend ?? "..."}
                {status?.database.database ? ` · ${status.database.database}` : ""}
              </div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-[0.16em]">Owners / Methodologies</div>
              <div className="mt-1 text-ink">
                {status ? `${status.database.ownersCount} / ${status.database.methodologiesCount}` : "..."}
              </div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-[0.16em]">Signatures Dir</div>
              <div className="mt-1 break-all text-ink">{status?.signaturesDir ?? "..."}</div>
            </div>
            <div className="pt-2">
              <div className="flex flex-wrap gap-3">
                <Link className="btn-secondary" to="/settings">Открыть настройки</Link>
                <Link className="btn-secondary" to="/generation">Рабочая зона генерации</Link>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
