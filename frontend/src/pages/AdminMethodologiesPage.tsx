import { useState } from "react";

import { useQuery } from "@tanstack/react-query";

import { fetchMethodologies } from "@/api/methodologies";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAuthStore } from "@/store/auth";

export function AdminMethodologiesPage() {
  const token = useAuthStore((state) => state.token);
  const [search, setSearch] = useState("");
  const [expandedCode, setExpandedCode] = useState<string | null>(null);

  const methodologiesQuery = useQuery({
    queryKey: ["methodologies", search],
    queryFn: () => fetchMethodologies(token ?? "", search || undefined),
    enabled: Boolean(token),
  });

  return (
    <section className="space-y-6">
      <PageHeader title="Методики поверки" description="Справочник методик поверки СИ." />

      <div className="section-card space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <input
            className="form-input max-w-xs"
            placeholder="Поиск по коду..."
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <span className="status-chip">Всего: {methodologiesQuery.data?.length ?? "..."}</span>
        </div>

        <div className="space-y-3">
          {methodologiesQuery.isLoading ? (
            <p className="text-sm text-steel">Загрузка...</p>
          ) : methodologiesQuery.data?.length ? (
            methodologiesQuery.data.map((m) => (
              <div key={m.code} className="rounded-2xl border border-line p-4">
                <button
                  className="flex w-full items-center justify-between gap-3 text-left"
                  type="button"
                  onClick={() => setExpandedCode(expandedCode === m.code ? null : m.code)}
                >
                  <div>
                    <div className="font-semibold text-ink">{m.code}</div>
                    <div className="mt-1 text-sm text-steel">{m.title}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    {m.allowable_variation_pct != null ? (
                      <span className="status-chip">δ {m.allowable_variation_pct}%</span>
                    ) : null}
                    <span className="text-xs text-steel">{m.points.length} пунктов</span>
                  </div>
                </button>

                {expandedCode === m.code ? (
                  <div className="mt-4 space-y-2 border-t border-line pt-4">
                    {m.document ? <p className="text-sm text-steel">Документ: {m.document}</p> : null}
                    {m.notes ? <p className="text-sm text-steel">Примечание: {m.notes}</p> : null}
                    <div className="overflow-x-auto rounded-xl border border-line">
                      <table className="min-w-full text-sm">
                        <thead className="bg-[var(--surface-2)] text-left text-steel">
                          <tr>
                            <th className="px-3 py-2 font-medium">№</th>
                            <th className="px-3 py-2 font-medium">Пункт</th>
                            <th className="px-3 py-2 font-medium">Тип</th>
                          </tr>
                        </thead>
                        <tbody>
                          {m.points.map((p) => (
                            <tr key={p.position} className="border-t border-line">
                              <td className="px-3 py-2 text-steel">{p.position}</td>
                              <td className="px-3 py-2 text-ink">{p.label}</td>
                              <td className="px-3 py-2 text-steel">{p.point_type}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : null}
              </div>
            ))
          ) : (
            <p className="text-sm text-steel">Нет записей.</p>
          )}
        </div>
      </div>
    </section>
  );
}
