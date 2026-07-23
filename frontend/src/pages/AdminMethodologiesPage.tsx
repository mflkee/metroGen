import { FormEvent, useEffect, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchMethodologies,
  updateMethodology,
  type MethodologyOut,
  type MethodologyPointOut,
} from "@/api/methodologies";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAuthStore } from "@/store/auth";

type EditablePoint = {
  position: number;
  label: string;
  point_type: string;
  default_text: string;
};

export function AdminMethodologiesPage() {
  const token = useAuthStore((state) => state.token);
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [editId, setEditId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDocument, setEditDocument] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [editAllowable, setEditAllowable] = useState("");
  const [editPoints, setEditPoints] = useState<EditablePoint[]>([]);
  const [saving, setSaving] = useState(false);

  const methodologiesQuery = useQuery({
    queryKey: ["methodologies", search],
    queryFn: () => fetchMethodologies(token ?? "", search || undefined),
    enabled: Boolean(token),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Record<string, unknown> }) =>
      updateMethodology(token ?? "", id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["methodologies"] });
      setEditId(null);
    },
  });

  function startEdit(m: MethodologyOut) {
    setEditId(m.id);
    setEditTitle(m.title);
    setEditDocument(m.document ?? "");
    setEditNotes(m.notes ?? "");
    setEditAllowable(m.allowable_variation_pct != null ? String(m.allowable_variation_pct) : "");
    setEditPoints(
      m.points.map((p) => ({
        position: p.position,
        label: p.label,
        point_type: p.point_type,
        default_text: p.default_text ?? "",
      })),
    );
  }

  function cancelEdit() {
    setEditId(null);
  }

  function updatePoint(pos: number, field: keyof EditablePoint, value: string) {
    setEditPoints((prev) => prev.map((p) => (p.position === pos ? { ...p, [field]: value } : p)));
  }

  function addPoint() {
    const nextPos = editPoints.length ? Math.max(...editPoints.map((p) => p.position)) + 1 : 1;
    setEditPoints((prev) => [...prev, { position: nextPos, label: "", point_type: "clause", default_text: "" }]);
  }

  function removePoint(pos: number) {
    setEditPoints((prev) => prev.filter((p) => p.position !== pos));
  }

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {
        title: editTitle || null,
        document: editDocument || null,
        notes: editNotes || null,
      };
      if (editAllowable) {
        payload.allowable_variation_pct = parseFloat(editAllowable);
      }
      const validPoints = editPoints.filter((p) => p.label.trim() || p.default_text.trim());
      if (validPoints.length) {
        payload.points = validPoints.map((p) => ({
          position: p.position,
          label: p.label.trim(),
          point_type: p.point_type || "clause",
          default_text: p.default_text.trim() || null,
        }));
      }
      await updateMutation.mutateAsync({ id: editId!, payload });
    } finally {
      setSaving(false);
    }
  }

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

        {editId ? (
          <form className="rounded-2xl border border-line p-4 space-y-4" onSubmit={handleSave}>
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block text-sm text-steel">
                Название
                <input className="form-input mt-1" type="text" value={editTitle} onChange={(e) => setEditTitle(e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Документ
                <input className="form-input mt-1" type="text" value={editDocument} onChange={(e) => setEditDocument(e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Примечание
                <input className="form-input mt-1" type="text" value={editNotes} onChange={(e) => setEditNotes(e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Допустимая вариация, %
                <input className="form-input mt-1" type="number" step="0.01" value={editAllowable} onChange={(e) => setEditAllowable(e.target.value)} />
              </label>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-steel">Пункты методики</span>
                <button className="btn-secondary btn-sm" type="button" onClick={addPoint}>+ Добавить пункт</button>
              </div>
              <div className="overflow-x-auto rounded-xl border border-line">
                <table className="min-w-full text-sm">
                  <thead className="bg-[var(--surface-2)] text-left text-steel">
                    <tr>
                      <th className="px-3 py-2 font-medium">№</th>
                      <th className="px-3 py-2 font-medium">Пункт</th>
                      <th className="px-3 py-2 font-medium">Тип</th>
                      <th className="px-3 py-2 font-medium">Название</th>
                      <th className="px-3 py-2 font-medium" />
                    </tr>
                  </thead>
                  <tbody>
                    {editPoints.map((p) => (
                      <tr key={p.position} className="border-t border-line">
                        <td className="px-3 py-2 text-steel">{p.position}</td>
                        <td className="px-3 py-2">
                          <input className="form-input text-sm py-1" type="text" value={p.label} onChange={(e) => updatePoint(p.position, "label", e.target.value)} />
                        </td>
                        <td className="px-3 py-2">
                          <select className="form-input text-sm py-1" value={p.point_type} onChange={(e) => updatePoint(p.position, "point_type", e.target.value)}>
                            <option value="clause">clause</option>
                            <option value="bool">bool</option>
                            <option value="custom">custom</option>
                          </select>
                        </td>
                        <td className="px-3 py-2">
                          <input className="form-input text-sm py-1" placeholder="Напр. Внешний осмотр" type="text" value={p.default_text} onChange={(e) => updatePoint(p.position, "default_text", e.target.value)} />
                        </td>
                        <td className="px-3 py-2">
                          <button className="btn-secondary btn-sm" type="button" onClick={() => removePoint(p.position)}>×</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="flex gap-2">
              <button className="btn-primary" disabled={saving} type="submit">{saving ? "..." : "Сохранить"}</button>
              <button className="btn-secondary" type="button" onClick={cancelEdit}>Отмена</button>
            </div>
          </form>
        ) : null}

        <div className="space-y-3">
          {methodologiesQuery.isLoading ? (
            <p className="text-sm text-steel">Загрузка...</p>
          ) : methodologiesQuery.data?.length ? (
            methodologiesQuery.data.map((m) => (
              <div key={m.code} className="rounded-2xl border border-line p-4">
                <div className="flex w-full items-center justify-between gap-3 text-left">
                  <div>
                    <div className="font-semibold text-ink">{m.code}</div>
                    <div className="mt-1 text-sm text-steel">{m.title}</div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    {m.allowable_variation_pct != null ? (
                      <span className="status-chip">δ {m.allowable_variation_pct}%</span>
                    ) : null}
                    <span className="text-xs text-steel">{m.points.length} пунктов</span>
                    <button className="btn-secondary btn-sm" type="button" onClick={() => startEdit(m)}>Редактировать</button>
                  </div>
                </div>

                <div className="mt-3 overflow-x-auto rounded-xl border border-line">
                  <table className="min-w-full text-sm">
                    <thead className="bg-[var(--surface-2)] text-left text-steel">
                      <tr>
                        <th className="px-3 py-2 font-medium">№</th>
                        <th className="px-3 py-2 font-medium">Пункт</th>
                        <th className="px-3 py-2 font-medium">Тип</th>
                        <th className="px-3 py-2 font-medium">Название</th>
                      </tr>
                    </thead>
                    <tbody>
                      {m.points.map((p) => (
                        <tr key={p.position} className="border-t border-line">
                          <td className="px-3 py-2 text-steel">{p.position}</td>
                          <td className="px-3 py-2 text-ink">{p.label}</td>
                          <td className="px-3 py-2 text-steel">{p.point_type}</td>
                          <td className="px-3 py-2 text-steel">{p.default_text ?? "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
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
