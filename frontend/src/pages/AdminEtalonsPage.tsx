import { FormEvent, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { EtalonOut, EtalonUpsertPayload, fetchEtalons, upsertEtalon } from "@/api/etalons";
import { PageHeader } from "@/components/ui/page-header";
import { DateInput } from "@/components/date-input";
import { NumberInput } from "@/components/number-input";
import { useAuthStore } from "@/store/auth";

type FormState = {
  reg_number: string;
  title: string;
  mitype_number: string;
  notation: string;
  modification: string;
  manufacture_num: string;
  manufacture_year: string;
  rank_code: string;
  rank_title: string;
  schema_title: string;
  certificate_no: string;
  verification_date: string;
  valid_to: string;
};

const emptyForm: FormState = {
  reg_number: "",
  title: "",
  mitype_number: "",
  notation: "",
  modification: "",
  manufacture_num: "",
  manufacture_year: "",
  rank_code: "",
  rank_title: "",
  schema_title: "",
  certificate_no: "",
  verification_date: "",
  valid_to: "",
};

function formatDate(value: string | null): string {
  if (!value) return "—";
  const dt = new Date(value);
  return isNaN(dt.getTime()) ? value : dt.toLocaleDateString("ru-RU");
}

function isExpired(value: string | null): boolean {
  if (!value) return false;
  const dt = new Date(value);
  return !isNaN(dt.getTime()) && dt.getTime() < Date.now();
}

function toPayload(form: FormState): EtalonUpsertPayload {
  const year = form.manufacture_year.trim();
  return {
    reg_number: form.reg_number.trim(),
    title: form.title.trim() || null,
    mitype_number: form.mitype_number.trim() || null,
    notation: form.notation.trim() || null,
    modification: form.modification.trim() || null,
    manufacture_num: form.manufacture_num.trim() || null,
    manufacture_year: year ? Number(year) : null,
    rank_code: form.rank_code.trim() || null,
    rank_title: form.rank_title.trim() || null,
    schema_title: form.schema_title.trim() || null,
    certificate_no: form.certificate_no.trim() || null,
    verification_date: form.verification_date.trim() || null,
    valid_to: form.valid_to.trim() || null,
  };
}

function etalonToForm(etalon: EtalonOut): FormState {
  return {
    reg_number: etalon.reg_number,
    title: etalon.title ?? "",
    mitype_number: etalon.mitype_number ?? "",
    notation: etalon.notation ?? "",
    modification: etalon.modification ?? "",
    manufacture_num: etalon.manufacture_num ?? "",
    manufacture_year: etalon.manufacture_year ? String(etalon.manufacture_year) : "",
    rank_code: etalon.rank_code ?? "",
    rank_title: etalon.rank_title ?? "",
    schema_title: etalon.schema_title ?? "",
    certificate_no: etalon.certificate_no ?? "",
    verification_date: etalon.verification_date ?? "",
    valid_to: etalon.valid_to ?? "",
  };
}

export function AdminEtalonsPage() {
  const token = useAuthStore((state) => state.token);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [saving, setSaving] = useState(false);

  const etalonsQuery = useQuery({
    queryKey: ["etalons"],
    queryFn: () => fetchEtalons(token ?? ""),
    enabled: Boolean(token),
  });

  const saveMutation = useMutation({
    mutationFn: () => upsertEtalon(token ?? "", toPayload(form)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["etalons"] });
      resetForm();
    },
  });

  function resetForm() {
    setShowForm(false);
    setForm(emptyForm);
  }

  function updateField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function startCreate() {
    setForm(emptyForm);
    setShowForm(true);
  }

  function startEdit(etalon: EtalonOut) {
    setForm(etalonToForm(etalon));
    setShowForm(true);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!form.reg_number.trim()) return;
    setSaving(true);
    try {
      await saveMutation.mutateAsync();
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader
        title="Эталоны"
        description="Справочник эталонов (ключ — номер ФИФ) с ленивым обновлением из Аршина."
      />

      <div className="section-card space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <button className="btn-primary btn-sm" type="button" onClick={startCreate}>
            Добавить
          </button>
          <span className="status-chip">Всего: {etalonsQuery.data?.length ?? "..."}</span>
        </div>

        {showForm ? (
          <form className="rounded-2xl border border-line p-4 space-y-4" onSubmit={handleSubmit}>
            <div className="grid gap-3 sm:grid-cols-3">
              <label className="block text-sm text-steel">
                Код эталона (ФИФ) *
                <input
                  className="form-input mt-1"
                  required
                  type="text"
                  placeholder="77090.19.2Р.00761949"
                  value={form.reg_number}
                  onChange={(e) => updateField("reg_number", e.target.value)}
                />
              </label>
              <label className="block text-sm text-steel">
                Название
                <input className="form-input mt-1" type="text" value={form.title} onChange={(e) => updateField("title", e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Тип (рег. номер)
                <input className="form-input mt-1" type="text" placeholder="77090-19" value={form.mitype_number} onChange={(e) => updateField("mitype_number", e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Обозначение
                <input className="form-input mt-1" type="text" placeholder="ЭЛМЕТРО-Паскаль-04" value={form.notation} onChange={(e) => updateField("notation", e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Модификация
                <input className="form-input mt-1" type="text" value={form.modification} onChange={(e) => updateField("modification", e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Зав. номер
                <input className="form-input mt-1" type="text" value={form.manufacture_num} onChange={(e) => updateField("manufacture_num", e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Год выпуска
                <NumberInput
                  className="form-input mt-1"
                  maxLength={4}
                  value={form.manufacture_year}
                  onValueChange={(value) => updateField("manufacture_year", value)}
                />
              </label>
              <label className="block text-sm text-steel">
                Разряд
                <input className="form-input mt-1" type="text" placeholder="2Р" value={form.rank_code} onChange={(e) => updateField("rank_code", e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Разряд (описание)
                <input className="form-input mt-1" type="text" placeholder="Эталон 2-го разряда" value={form.rank_title} onChange={(e) => updateField("rank_title", e.target.value)} />
              </label>
              <label className="block text-sm text-steel sm:col-span-2">
                Приказ / ГПС
                <input className="form-input mt-1" type="text" value={form.schema_title} onChange={(e) => updateField("schema_title", e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Свидетельство
                <input className="form-input mt-1" type="text" value={form.certificate_no} onChange={(e) => updateField("certificate_no", e.target.value)} />
              </label>
              <label className="block text-sm text-steel">
                Дата поверки
                <DateInput className="form-input mt-1" value={form.verification_date} onChange={(value) => updateField("verification_date", value)} />
              </label>
              <label className="block text-sm text-steel">
                Действительно до
                <DateInput className="form-input mt-1" value={form.valid_to} onChange={(value) => updateField("valid_to", value)} />
              </label>
            </div>
            <div className="flex items-center gap-2">
              <button className="btn-primary" disabled={saving} type="submit">
                {saving ? "..." : "Сохранить"}
              </button>
              <button className="btn-secondary" type="button" onClick={resetForm}>
                Отмена
              </button>
            </div>
          </form>
        ) : null}

        <div className="overflow-x-auto rounded-2xl border border-line">
          <table className="data-table">
            <thead>
              <tr>
                <th>Код (ФИФ)</th>
                <th>Название</th>
                <th>Обозначение</th>
                <th>Зав. номер</th>
                <th>Разряд</th>
                <th>Свидетельство</th>
                <th>Действ. до</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {etalonsQuery.isLoading ? (
                <tr>
                  <td className="text-center text-steel" colSpan={8}>
                    Загрузка...
                  </td>
                </tr>
              ) : etalonsQuery.data?.length ? (
                etalonsQuery.data.map((etalon) => (
                  <tr key={etalon.id} >
                    <td className="font-mono text-xs text-ink">{etalon.reg_number}</td>
                    <td className="text-ink">{etalon.title ?? "—"}</td>
                    <td className="text-center text-steel">{etalon.notation ?? "—"}</td>
                    <td className="text-center text-steel">{etalon.manufacture_num ?? "—"}</td>
                    <td className="text-center text-steel">{etalon.rank_code ?? "—"}</td>
                    <td className="text-center text-steel">{etalon.certificate_no ?? "—"}</td>
                    <td >
                      <span className={isExpired(etalon.valid_to) ? "text-signal-danger" : "text-steel"}>
                        {formatDate(etalon.valid_to)}
                        {isExpired(etalon.valid_to) ? " (просрочено)" : ""}
                      </span>
                    </td>
                    <td className="text-right">
                      <button className="btn-secondary btn-sm" type="button" onClick={() => startEdit(etalon)}>
                        Изменить
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td className="text-center text-steel" colSpan={8}>
                    Нет записей.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
