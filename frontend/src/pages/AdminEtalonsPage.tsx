import { FormEvent, useEffect, useMemo, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  addEtalonCertification,
  deleteEtalon,
  deleteEtalonCertification,
  fetchEtalonCertifications,
  fetchEtalons,
  updateEtalon,
  upsertEtalon,
  type EtalonCertificationOut,
  type EtalonOut,
} from "@/api/etalons";
import { DateInput } from "@/components/date-input";
import { DeleteConfirmModal } from "@/components/DeleteConfirmModal";
import { ExpandableItem } from "@/components/ExpandableItem";
import { Modal } from "@/components/Modal";
import { NumberInput } from "@/components/number-input";
import { PageHeader } from "@/components/ui/page-header";
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

type EtalonModal =
  | { mode: "create" }
  | { mode: "edit"; etalon: EtalonOut }
  | null;

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
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString("ru-RU");
}

function isExpired(value: string | null): boolean {
  if (!value) return false;
  const date = new Date(value);
  return !Number.isNaN(date.getTime()) && date.getTime() < Date.now();
}

function toPayload(form: FormState) {
  const year = form.manufacture_year.trim();
  return {
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
    verification_date: form.verification_date || null,
    valid_to: form.valid_to || null,
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
  const [modal, setModal] = useState<EtalonModal>(null);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [deleteTarget, setDeleteTarget] = useState<EtalonOut | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [newCertNo, setNewCertNo] = useState("");
  const [newCertFrom, setNewCertFrom] = useState("");
  const [newCertTo, setNewCertTo] = useState("");
  const [deleteCertTarget, setDeleteCertTarget] = useState<EtalonCertificationOut | null>(null);

  const etalonsQuery = useQuery({
    queryKey: ["etalons"],
    queryFn: () => fetchEtalons(token ?? ""),
    enabled: Boolean(token),
  });

  const certificationsQuery = useQuery({
    queryKey: ["etalon-certifications", expandedId],
    queryFn: () => fetchEtalonCertifications(token ?? "", expandedId as number),
    enabled: Boolean(token) && expandedId !== null,
  });

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = toPayload(form);
      if (modal?.mode === "edit") {
        await updateEtalon(token ?? "", modal.etalon.id, payload);
        return;
      }
      await upsertEtalon(token ?? "", { reg_number: form.reg_number.trim(), ...payload });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["etalons"] });
      if (expandedId !== null) {
        void queryClient.invalidateQueries({ queryKey: ["etalon-certifications", expandedId] });
      }
      setModal(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (etalonId: number) => deleteEtalon(token ?? "", etalonId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["etalons"] });
      setDeleteTarget(null);
    },
  });

  const addCertMutation = useMutation({
    mutationFn: () =>
      addEtalonCertification(token ?? "", expandedId as number, {
        certificate_no: newCertNo.trim(),
        verification_date: newCertFrom || null,
        valid_to: newCertTo || null,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["etalon-certifications", expandedId] });
      void queryClient.invalidateQueries({ queryKey: ["etalons"] });
      setNewCertNo("");
      setNewCertFrom("");
      setNewCertTo("");
    },
  });

  const deleteCertMutation = useMutation({
    mutationFn: (certificationId: number) =>
      deleteEtalonCertification(token ?? "", expandedId as number, certificationId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["etalon-certifications", expandedId] });
      void queryClient.invalidateQueries({ queryKey: ["etalons"] });
      setDeleteCertTarget(null);
    },
  });

  const etalons = useMemo(() => etalonsQuery.data ?? [], [etalonsQuery.data]);

  useEffect(() => {
    if (!modal) {
      return;
    }
    setForm(modal.mode === "edit" ? etalonToForm(modal.etalon) : emptyForm);
  }, [modal]);

  function updateField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!form.reg_number.trim() && modal?.mode !== "edit") {
      return;
    }
    saveMutation.mutate();
  }

  return (
    <section className="space-y-6">
      <PageHeader
        title="Эталоны"
        description="Справочник эталонов (ключ — номер ФИФ) со свидетельствами и обновлением из Аршина."
      />

      <div className="section-card space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <button className="btn-primary btn-sm" type="button" onClick={() => setModal({ mode: "create" })}>
            Добавить
          </button>
          <span className="status-chip">Всего: {etalons.length}</span>
        </div>

        {etalonsQuery.isLoading ? <p className="text-sm text-steel">Загрузка...</p> : null}
        {etalonsQuery.isError ? (
          <p className="text-sm text-[var(--danger-text)]">Не удалось загрузить список эталонов.</p>
        ) : null}

        <div className="space-y-3">
          {!etalonsQuery.isLoading && !etalonsQuery.isError && etalons.length === 0 ? (
            <p className="text-sm text-steel">Нет записей.</p>
          ) : null}

          {etalons.map((etalon) => {
            return (
              <ExpandableItem
                key={etalon.id}
                actions={
                  <>
                    <button className="btn-secondary btn-sm" type="button" onClick={() => setModal({ mode: "edit", etalon })}>
                      Изменить
                    </button>
                    <button className="btn-danger btn-sm" type="button" onClick={() => setDeleteTarget(etalon)}>
                      Удалить
                    </button>
                  </>
                }
                header={
                  <div>
                    <div className="font-mono text-xs text-ink">{etalon.reg_number}</div>
                    <div className="mt-1 text-sm text-steel">{etalon.title ?? "—"}</div>
                    <div className="mt-1 text-xs text-steel">
                      Свид. {etalon.certificate_no ?? "—"} ·{" "}
                      <span className={isExpired(etalon.valid_to) ? "text-signal-danger" : "text-steel"}>
                        до {formatDate(etalon.valid_to)}
                        {isExpired(etalon.valid_to) ? " (просрочено)" : ""}
                      </span>
                    </div>
                  </div>
                }
                onToggle={(open) => setExpandedId(open ? etalon.id : null)}
              >
                <dl className="grid gap-2 text-sm sm:grid-cols-2">
                  <div>
                    <dt className="text-xs uppercase tracking-[0.16em] text-steel">Тип (рег. номер)</dt>
                    <dd className="text-ink">{etalon.mitype_number ?? "—"}</dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-[0.16em] text-steel">Обозначение</dt>
                    <dd className="text-ink">{etalon.notation ?? "—"}</dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-[0.16em] text-steel">Модификация</dt>
                    <dd className="text-ink">{etalon.modification ?? "—"}</dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-[0.16em] text-steel">Зав. номер</dt>
                    <dd className="text-ink">{etalon.manufacture_num ?? "—"}</dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-[0.16em] text-steel">Год выпуска</dt>
                    <dd className="text-ink">{etalon.manufacture_year ?? "—"}</dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-[0.16em] text-steel">Разряд</dt>
                    <dd className="text-ink">{etalon.rank_title ?? etalon.rank_code ?? "—"}</dd>
                  </div>
                  <div className="sm:col-span-2">
                    <dt className="text-xs uppercase tracking-[0.16em] text-steel">Приказ / ГПС</dt>
                    <dd className="text-ink">{etalon.schema_title ?? "—"}</dd>
                  </div>
                </dl>

                <div className="text-xs uppercase tracking-[0.16em] text-steel">Свидетельства</div>
                <div className="overflow-x-auto rounded-xl border border-line">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Номер</th>
                        <th>Дата поверки</th>
                        <th>Действительно до</th>
                        <th>Источник</th>
                        <th />
                      </tr>
                    </thead>
                    <tbody>
                      {certificationsQuery.isLoading ? (
                        <tr>
                          <td className="text-center text-steel" colSpan={5}>
                            Загрузка...
                          </td>
                        </tr>
                      ) : certificationsQuery.data?.length ? (
                        certificationsQuery.data.map((cert) => (
                          <tr key={cert.id}>
                            <td className="text-ink">{cert.certificate_no}</td>
                            <td className="text-steel">{formatDate(cert.verification_date)}</td>
                            <td className={isExpired(cert.valid_to) ? "text-signal-danger" : "text-steel"}>
                              {formatDate(cert.valid_to)}
                            </td>
                            <td className="text-steel">{cert.source ?? "—"}</td>
                            <td className="text-right">
                              <button className="btn-danger btn-sm" type="button" onClick={() => setDeleteCertTarget(cert)}>
                                Удалить
                              </button>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td className="text-center text-steel" colSpan={5}>
                            Свидетельств нет.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>

                <div className="grid gap-2 rounded-xl border border-line p-3 md:grid-cols-[1fr_150px_150px_auto]">
                  <input
                    className="form-input"
                    placeholder="Номер свидетельства"
                    type="text"
                    value={newCertNo}
                    onChange={(e) => setNewCertNo(e.target.value)}
                  />
                  <DateInput className="form-input" value={newCertFrom} onChange={setNewCertFrom} />
                  <DateInput className="form-input" value={newCertTo} onChange={setNewCertTo} />
                  <button
                    className="btn-primary btn-sm"
                    disabled={!newCertNo.trim() || addCertMutation.isPending}
                    type="button"
                    onClick={() => addCertMutation.mutate()}
                  >
                    Добавить свидетельство
                  </button>
                </div>
                {addCertMutation.isError ? (
                  <p className="text-sm text-[var(--danger-text)]">
                    {addCertMutation.error instanceof Error ? addCertMutation.error.message : "Не удалось добавить свидетельство."}
                  </p>
                ) : null}
              </ExpandableItem>
            );
          })}
        </div>
      </div>

      <Modal
        description={modal?.mode === "edit" ? "Измените реквизиты эталона." : "Заведите эталон (ключ — номер ФИФ)."}
        footer={
          <div className="flex justify-end gap-3">
            <button className="btn-secondary btn-sm" type="button" onClick={() => setModal(null)}>
              Отмена
            </button>
            <button className="btn-primary btn-sm" disabled={saveMutation.isPending} form="etalon-form" type="submit">
              {saveMutation.isPending ? "Сохраняем..." : "Сохранить"}
            </button>
          </div>
        }
        open={modal !== null}
        size="xl"
        title={modal?.mode === "edit" ? "Изменить эталон" : "Новый эталон"}
        onClose={() => setModal(null)}
      >
        <form className="space-y-4" id="etalon-form" onSubmit={handleSubmit}>
          <div className="grid gap-3 sm:grid-cols-3">
            <label className="block text-sm text-steel">
              Код эталона (ФИФ) *
              <input
                className="form-input mt-1"
                disabled={modal?.mode === "edit"}
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
              <input className="form-input mt-1" placeholder="77090-19" type="text" value={form.mitype_number} onChange={(e) => updateField("mitype_number", e.target.value)} />
            </label>
            <label className="block text-sm text-steel">
              Обозначение
              <input className="form-input mt-1" placeholder="ЭЛМЕТРО-Паскаль-04" type="text" value={form.notation} onChange={(e) => updateField("notation", e.target.value)} />
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
              <NumberInput className="form-input mt-1" maxLength={4} value={form.manufacture_year} onValueChange={(value) => updateField("manufacture_year", value)} />
            </label>
            <label className="block text-sm text-steel">
              Разряд
              <input className="form-input mt-1" placeholder="2Р" type="text" value={form.rank_code} onChange={(e) => updateField("rank_code", e.target.value)} />
            </label>
            <label className="block text-sm text-steel">
              Разряд (описание)
              <input className="form-input mt-1" placeholder="Эталон 2-го разряда" type="text" value={form.rank_title} onChange={(e) => updateField("rank_title", e.target.value)} />
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
          {saveMutation.isError ? (
            <p className="text-sm text-[var(--danger-text)]">
              {saveMutation.error instanceof Error ? saveMutation.error.message : "Не удалось сохранить эталон."}
            </p>
          ) : null}
        </form>
      </Modal>

      <DeleteConfirmModal
        description={
          deleteTarget
            ? `Удаляем эталон ${deleteTarget.reg_number} вместе со свидетельствами. Действие необратимо.`
            : undefined
        }
        errorMessage={
          deleteMutation.isError
            ? deleteMutation.error instanceof Error
              ? deleteMutation.error.message
              : "Не удалось удалить эталон."
            : null
        }
        isOpen={deleteTarget !== null}
        isPending={deleteMutation.isPending}
        title="Удалить эталон"
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
      />

      <DeleteConfirmModal
        confirmLabel="Удалить свидетельство"
        description={
          deleteCertTarget
            ? `Удаляем свидетельство ${deleteCertTarget.certificate_no}.`
            : undefined
        }
        errorMessage={
          deleteCertMutation.isError
            ? deleteCertMutation.error instanceof Error
              ? deleteCertMutation.error.message
              : "Не удалось удалить свидетельство."
            : null
        }
        isOpen={deleteCertTarget !== null}
        isPending={deleteCertMutation.isPending}
        title="Удалить свидетельство"
        onClose={() => setDeleteCertTarget(null)}
        onConfirm={() => deleteCertTarget && deleteCertMutation.mutate(deleteCertTarget.id)}
      />
    </section>
  );
}
