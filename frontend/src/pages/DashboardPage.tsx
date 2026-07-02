import { Link } from "react-router-dom";

import { useQuery } from "@tanstack/react-query";

import { fetchSystemStatus } from "@/api/system";
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
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-ink">metroGen</h1>
          <p className="mt-1 text-sm text-steel">Генерация протоколов поверки</p>
        </div>
        <div className="flex items-center gap-3">
          {status ? (
            <>
              <span className={["status-chip", status.pdfGenerationAvailable ? "status-chip--ok" : "status-chip--warn"].join(" ")}>
                PDF: {status.pdfGenerationAvailable ? "готов" : "нет Chromium"}
              </span>
              <span className={["status-chip", status.smtpConfigured ? "status-chip--ok" : "status-chip--warn"].join(" ")}>
                SMTP: {status.smtpConfigured ? "есть" : "нет"}
              </span>
            </>
          ) : null}
          <Link className="btn-primary" to="/generation">Генерация</Link>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <article className="metric-card">
          <div className="metric-card__label">Папки экспорта</div>
          <div className="metric-card__value">{status?.exportFoldersCount ?? "..."}</div>
        </article>
        <article className="metric-card">
          <div className="metric-card__label">Файлы в выдаче</div>
          <div className="metric-card__value">{status?.generatedFilesCount ?? "..."}</div>
        </article>
        <article className="metric-card">
          <div className="metric-card__label">Активных записей</div>
          <div className="metric-card__value">{status?.database.activeRegistryEntriesCount ?? "..."}</div>
        </article>
        <article className="metric-card">
          <div className="metric-card__label">Владельцы / Методики</div>
          <div className="metric-card__value">
            {status ? `${status.database.ownersCount} / ${status.database.methodologiesCount}` : "..."}
          </div>
        </article>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <QuickLink to="/generation" title="Генерация" description="PDF-пакеты, HTML-превью, импорт реестра" />
        <QuickLink to="/settings" title="Настройки" description="Темы, SMTP, параметры" />
        <QuickLink to="/developer" title="Мониторинг" description="Состояние сервиса и БД" />
      </div>
    </section>
  );
}

function QuickLink({ to, title, description }: { to: string; title: string; description: string }) {
  return (
    <Link className="rounded-3xl border border-line p-5 transition hover:bg-[var(--tone-child-bg)]" to={to}>
      <div className="text-base font-semibold text-ink">{title}</div>
      <p className="mt-1 text-sm text-steel">{description}</p>
    </Link>
  );
}
