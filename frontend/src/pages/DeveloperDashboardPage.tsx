import { useQuery } from "@tanstack/react-query";

import { fetchSystemStatus } from "@/api/system";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAuthStore } from "@/store/auth";

export function DeveloperDashboardPage() {
  const token = useAuthStore((state) => state.token);
  const statusQuery = useQuery({
    queryKey: ["system-status", "developer"],
    queryFn: () => fetchSystemStatus(token ?? ""),
    enabled: Boolean(token),
  });

  const status = statusQuery.data;

  return (
    <section>
      <PageHeader
        title="Мониторинг"
        description="Упрощенный техэкран metroGen: состояние PDF-рендера, SMTP, каталогов и активности пользователей."
      />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <article className="metric-card">
          <div className="metric-card__label">Активные пользователи</div>
          <div className="metric-card__value">{status?.activeUsersCount ?? "..."}</div>
        </article>
        <article className="metric-card">
          <div className="metric-card__label">Всего пользователей</div>
          <div className="metric-card__value">{status?.usersCount ?? "..."}</div>
        </article>
        <article className="metric-card">
          <div className="metric-card__label">Экспортные папки</div>
          <div className="metric-card__value">{status?.exportFoldersCount ?? "..."}</div>
        </article>
        <article className="metric-card">
          <div className="metric-card__label">Файлы в истории</div>
          <div className="metric-card__value">{status?.generatedFilesCount ?? "..."}</div>
        </article>
      </div>

      <div className="section-card mt-6">
        <h3 className="text-lg font-semibold text-ink">Окружение</h3>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-line p-4">
            <div className="text-xs uppercase tracking-[0.16em] text-steel">App</div>
            <div className="mt-1 text-ink">{status?.appName ?? "..."}</div>
            <div className="mt-3 text-xs uppercase tracking-[0.16em] text-steel">Env</div>
            <div className="mt-1 text-ink">{status?.appEnv ?? "..."}</div>
          </div>
          <div className="rounded-2xl border border-line p-4">
            <div className="text-xs uppercase tracking-[0.16em] text-steel">Exports Dir</div>
            <div className="mt-1 break-all text-ink">{status?.exportsDir ?? "..."}</div>
            <div className="mt-3 text-xs uppercase tracking-[0.16em] text-steel">Signatures Dir</div>
            <div className="mt-1 break-all text-ink">{status?.signaturesDir ?? "..."}</div>
          </div>
        </div>
      </div>
    </section>
  );
}
