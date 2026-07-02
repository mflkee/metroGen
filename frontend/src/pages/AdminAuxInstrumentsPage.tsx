import { FormEvent, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createAuxInstrument,
  fetchAuxInstruments,
} from "@/api/auxiliary-instruments";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAuthStore } from "@/store/auth";

export function AdminAuxInstrumentsPage() {
  const token = useAuthStore((state) => state.token);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [regNumber, setRegNumber] = useState("");
  const [modification, setModification] = useState("");
  const [manufactureNum, setManufactureNum] = useState("");
  const [certificateNo, setCertificateNo] = useState("");
  const [saving, setSaving] = useState(false);

  const instrumentsQuery = useQuery({
    queryKey: ["aux-instruments"],
    queryFn: () => fetchAuxInstruments(token ?? ""),
    enabled: Boolean(token),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createAuxInstrument(token ?? "", {
        title: title.trim(),
        reg_number: regNumber.trim(),
        modification: modification.trim() || null,
        manufacture_num: manufactureNum.trim(),
        certificate_no: certificateNo.trim() || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["aux-instruments"] });
      resetForm();
    },
  });

  function resetForm() {
    setShowForm(false);
    setTitle("");
    setRegNumber("");
    setModification("");
    setManufactureNum("");
    setCertificateNo("");
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!title.trim() || !regNumber.trim() || !manufactureNum.trim()) return;
    setSaving(true);
    try {
      await createMutation.mutateAsync();
    } finally {
      setSaving(false);
    }
  }

  function formatDate(d: string | null) {
    if (!d) return "—";
    const dt = new Date(d);
    return isNaN(dt.getTime()) ? d : dt.toLocaleDateString("ru-RU");
  }

  return (
    <section className="space-y-6">
      <PageHeader title="Вспомогательные СИ" description="Справочник вспомогательных средств измерений." />

      <div className="section-card space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <button className="btn-primary btn-sm" type="button" onClick={() => { resetForm(); setShowForm(true); }}>
            Добавить
          </button>
          <span className="status-chip">Всего: {instrumentsQuery.data?.length ?? "..."}</span>
        </div>

        {showForm ? (
          <form className="rounded-2xl border border-line p-4 space-y-3" onSubmit={handleSubmit}>
            <div className="grid gap-3 sm:grid-cols-3">
              <label className="block text-sm text-steel">
                Название
                <input className="form-input mt-1" required type="text" value={title} onChange={(e) => setTitle(e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Рег. номер
                <input className="form-input mt-1" required type="text" value={regNumber} onChange={(e) => setRegNumber(e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Модификация
                <input className="form-input mt-1" type="text" value={modification} onChange={(e) => setModification(e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Зав. номер
                <input className="form-input mt-1" required type="text" value={manufactureNum} onChange={(e) => setManufactureNum(e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Свидетельство
                <input className="form-input mt-1" type="text" value={certificateNo} onChange={(e) => setCertificateNo(e.target.value)} />
              </label>
              <div className="flex items-end gap-2">
                <button className="btn-primary" disabled={saving} type="submit">{saving ? "..." : "Создать"}</button>
                <button className="btn-secondary" type="button" onClick={resetForm}>Отмена</button>
              </div>
            </div>
          </form>
        ) : null}

        <div className="overflow-x-auto rounded-2xl border border-line">
          <table className="min-w-full text-sm">
            <thead className="bg-[var(--surface-2)] text-left text-steel">
              <tr>
                <th className="px-4 py-3 font-medium">Название</th>
                <th className="px-4 py-3 font-medium">Рег. номер</th>
                <th className="px-4 py-3 font-medium">Модификация</th>
                <th className="px-4 py-3 font-medium">Зав. номер</th>
                <th className="px-4 py-3 font-medium">Свидетельство</th>
                <th className="px-4 py-3 font-medium">Действ. до</th>
              </tr>
            </thead>
            <tbody>
              {instrumentsQuery.isLoading ? (
                <tr><td className="px-4 py-6 text-steel" colSpan={6}>Загрузка...</td></tr>
              ) : instrumentsQuery.data?.length ? (
                instrumentsQuery.data.map((inst) => (
                  <tr key={inst.id} className="border-t border-line">
                    <td className="px-4 py-3 text-ink">{inst.title}</td>
                    <td className="px-4 py-3 text-steel">{inst.reg_number}</td>
                    <td className="px-4 py-3 text-steel">{inst.modification ?? "—"}</td>
                    <td className="px-4 py-3 text-steel">{inst.manufacture_num}</td>
                    <td className="px-4 py-3 text-steel">{inst.certificate_no ?? "—"}</td>
                    <td className="px-4 py-3 text-steel">{formatDate(inst.valid_to)}</td>
                  </tr>
                ))
              ) : (
                <tr><td className="px-4 py-6 text-steel" colSpan={6}>Нет записей.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
