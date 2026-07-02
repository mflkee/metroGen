import { FormEvent, useEffect, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createOwner,
  fetchOwners,
  updateOwner,
  type OwnerOut,
} from "@/api/owners";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAuthStore } from "@/store/auth";

export function AdminOwnersPage() {
  const token = useAuthStore((state) => state.token);
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [inn, setInn] = useState("");
  const [saving, setSaving] = useState(false);

  const ownersQuery = useQuery({
    queryKey: ["owners", search],
    queryFn: () => fetchOwners(token ?? "", search || undefined),
    enabled: Boolean(token),
  });

  const createMutation = useMutation({
    mutationFn: (payload: { name: string; inn?: string }) =>
      createOwner(token ?? "", payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["owners"] });
      resetForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: { name: string; inn?: string } }) =>
      updateOwner(token ?? "", id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["owners"] });
      resetForm();
    },
  });

  function resetForm() {
    setShowForm(false);
    setEditId(null);
    setName("");
    setInn("");
    setSaving(false);
  }

  function startEdit(owner: OwnerOut) {
    setEditId(owner.id);
    setName(owner.name);
    setInn(owner.inn ?? "");
    setShowForm(true);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try {
      if (editId) {
        await updateMutation.mutateAsync({ id: editId, payload: { name: name.trim(), inn: inn.trim() || undefined } });
      } else {
        await createMutation.mutateAsync({ name: name.trim(), inn: inn.trim() || undefined });
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader title="Владельцы" description="Справочник организаций-владельцев СИ." />

      <div className="section-card space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <input
            className="form-input max-w-xs"
            placeholder="Поиск..."
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button className="btn-primary btn-sm" type="button" onClick={() => { resetForm(); setShowForm(true); }}>
            Добавить
          </button>
          <span className="status-chip">Всего: {ownersQuery.data?.length ?? "..."}</span>
        </div>

        {showForm ? (
          <form className="rounded-2xl border border-line p-4 space-y-3" onSubmit={handleSubmit}>
            <div className="grid gap-3 sm:grid-cols-3">
              <label className="block text-sm text-steel">
                Название
                <input className="form-input mt-1" required type="text" value={name} onChange={(e) => setName(e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                ИНН
                <input className="form-input mt-1" type="text" value={inn} onChange={(e) => setInn(e.target.value)} />
              </label>
              <div className="flex items-end gap-2">
                <button className="btn-primary" disabled={saving} type="submit">
                  {saving ? "..." : editId ? "Сохранить" : "Создать"}
                </button>
                <button className="btn-secondary" type="button" onClick={resetForm}>Отмена</button>
              </div>
            </div>
          </form>
        ) : null}

        <div className="overflow-x-auto rounded-2xl border border-line">
          <table className="min-w-full text-sm">
            <thead className="bg-[var(--surface-2)] text-left text-steel">
              <tr>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Название</th>
                <th className="px-4 py-3 font-medium">ИНН</th>
                <th className="px-4 py-3 font-medium" />
              </tr>
            </thead>
            <tbody>
              {ownersQuery.isLoading ? (
                <tr><td className="px-4 py-6 text-steel" colSpan={4}>Загрузка...</td></tr>
              ) : ownersQuery.data?.length ? (
                ownersQuery.data.map((owner) => (
                  <tr key={owner.id} className="border-t border-line">
                    <td className="px-4 py-3 text-steel">{owner.id}</td>
                    <td className="px-4 py-3 text-ink">{owner.name}</td>
                    <td className="px-4 py-3 text-steel">{owner.inn ?? "—"}</td>
                    <td className="px-4 py-3">
                      <button className="btn-secondary btn-sm" type="button" onClick={() => startEdit(owner)}>Редактировать</button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr><td className="px-4 py-6 text-steel" colSpan={4}>Нет записей.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
