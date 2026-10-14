import { FormEvent, useEffect, useMemo, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createAuxInstrument,
  deleteAuxInstrument,
  fetchAuxInstruments,
  updateAuxInstrument,
  type AuxInstrumentOut,
} from "@/api/auxiliary-instruments";
import { DateInput } from "@/components/date-input";
import { DeleteConfirmModal } from "@/components/DeleteConfirmModal";
import { ExpandableItem } from "@/components/ExpandableItem";
import { Modal } from "@/components/Modal";
import { PageHeader } from "@/components/ui/page-header";
import { useAuthStore } from "@/store/auth";

type AuxModal =
  | { mode: "create" }
  | { mode: "edit"; instrument: AuxInstrumentOut }
  | null;

function formatDate(value: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString("ru-RU");
}

export function AdminAuxInstrumentsPage() {
  const token = useAuthStore((state) => state.token);
  const queryClient = useQueryClient();
  const [modal, setModal] = useState<AuxModal>(null);
  const [title, setTitle] = useState("");
  const [regNumber, setRegNumber] = useState("");
  const [modification, setModification] = useState("");
  const [manufactureNum, setManufactureNum] = useState("");
  const [certificateNo, setCertificateNo] = useState("");
  const [verificationDate, setVerificationDate] = useState("");
  const [validTo, setValidTo] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<AuxInstrumentOut | null>(null);

  const instrumentsQuery = useQuery({
    queryKey: ["aux-instruments"],
    queryFn: () => fetchAuxInstruments(token ?? ""),
    enabled: Boolean(token),
  });

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        title: title.trim(),
        reg_number: regNumber.trim(),
        modification: modification.trim() || null,
        manufacture_num: manufactureNum.trim(),
        certificate_no: certificateNo.trim() || null,
        verification_date: verificationDate || null,
        valid_to: validTo || null,
      };
      if (modal?.mode === "edit") {
        await updateAuxInstrument(token ?? "", modal.instrument.id, payload);
        return;
      }
      await createAuxInstrument(token ?? "", payload);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["aux-instruments"] });
      setModal(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (instrumentId: number) => deleteAuxInstrument(token ?? "", instrumentId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["aux-instruments"] });
      setDeleteTarget(null);
    },
  });

  const instruments = useMemo(() => instrumentsQuery.data ?? [], [instrumentsQuery.data]);

  useEffect(() => {
    if (!modal) {
      return;
    }
    if (modal.mode === "edit") {
      const item = modal.instrument;
      setTitle(item.title);
      setRegNumber(item.reg_number);
      setModification(item.modification ?? "");
      setManufactureNum(item.manufacture_num);
      setCertificateNo(item.certificate_no ?? "");
      setVerificationDate(item.verification_date ?? "");
      setValidTo(item.valid_to ?? "");
      return;
    }
    setTitle("");
    setRegNumber("");
    setModification("");
    setManufactureNum("");
    setCertificateNo("");
    setVerificationDate("");
    setValidTo("");
  }, [modal]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!title.trim() || !regNumber.trim() || !manufactureNum.trim()) {
      return;
    }
    saveMutation.mutate();
  }

  return (
    <section className="space-y-6">
      <PageHeader title="Вспомогательные СИ" description="Справочник вспомогательных средств измерений." />

      <div className="section-card space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <button className="btn-primary btn-sm" type="button" onClick={() => setModal({ mode: "create" })}>
            Добавить
          </button>
          <span className="status-chip">Всего: {instruments.length}</span>
        </div>

        {instrumentsQuery.isLoading ? <p className="text-sm text-steel">Загрузка...</p> : null}
        {instrumentsQuery.isError ? (
          <p className="text-sm text-[var(--danger-text)]">Не удалось загрузить список вспомогательных СИ.</p>
        ) : null}

        <div className="space-y-3">
          {!instrumentsQuery.isLoading && !instrumentsQuery.isError && instruments.length === 0 ? (
            <p className="text-sm text-steel">Нет записей.</p>
          ) : null}

          {instruments.map((instrument) => (
            <ExpandableItem
              key={instrument.id}
              actions={
                <>
                  <button className="btn-secondary btn-sm" type="button" onClick={() => setModal({ mode: "edit", instrument })}>
                    Изменить
                  </button>
                  <button className="btn-danger btn-sm" type="button" onClick={() => setDeleteTarget(instrument)}>
                    Удалить
                  </button>
                </>
              }
              header={
                <div>
                  <div className="font-semibold text-ink">{instrument.title}</div>
                  <div className="mt-1 text-sm text-steel">
                    Рег. № {instrument.reg_number} · Зав. № {instrument.manufacture_num}
                  </div>
                </div>
              }
            >
              <dl className="grid gap-2 text-sm sm:grid-cols-2">
                <div>
                  <dt className="text-xs uppercase tracking-[0.16em] text-steel">Модификация</dt>
                  <dd className="text-ink">{instrument.modification ?? "—"}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-[0.16em] text-steel">Свидетельство</dt>
                  <dd className="text-ink">{instrument.certificate_no ?? "—"}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-[0.16em] text-steel">Дата поверки</dt>
                  <dd className="text-ink">{formatDate(instrument.verification_date)}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-[0.16em] text-steel">Действительно до</dt>
                  <dd className="text-ink">{formatDate(instrument.valid_to)}</dd>
                </div>
              </dl>
            </ExpandableItem>
          ))}
        </div>
      </div>

      <Modal
        description={modal?.mode === "edit" ? "Измените реквизиты вспомогательного СИ." : "Заведите вспомогательное СИ."}
        footer={
          <div className="flex justify-end gap-3">
            <button className="btn-secondary btn-sm" type="button" onClick={() => setModal(null)}>
              Отмена
            </button>
            <button className="btn-primary btn-sm" disabled={saveMutation.isPending} form="aux-form" type="submit">
              {saveMutation.isPending ? "Сохраняем..." : "Сохранить"}
            </button>
          </div>
        }
        open={modal !== null}
        title={modal?.mode === "edit" ? "Изменить вспомогательное СИ" : "Новое вспомогательное СИ"}
        onClose={() => setModal(null)}
      >
        <form className="space-y-4" id="aux-form" onSubmit={handleSubmit}>
          <div className="grid gap-3 sm:grid-cols-2">
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
            <label className="block text-sm text-steel">
              Дата поверки
              <DateInput className="form-input mt-1" value={verificationDate} onChange={setVerificationDate} />
            </label>
            <label className="block text-sm text-steel">
              Действительно до
              <DateInput className="form-input mt-1" value={validTo} onChange={setValidTo} />
            </label>
          </div>
          {saveMutation.isError ? (
            <p className="text-sm text-[var(--danger-text)]">
              {saveMutation.error instanceof Error ? saveMutation.error.message : "Не удалось сохранить."}
            </p>
          ) : null}
        </form>
      </Modal>

      <DeleteConfirmModal
        description={
          deleteTarget
            ? `Удаляем «${deleteTarget.title}» (рег. № ${deleteTarget.reg_number}). Действие необратимо.`
            : undefined
        }
        errorMessage={
          deleteMutation.isError
            ? deleteMutation.error instanceof Error
              ? deleteMutation.error.message
              : "Не удалось удалить."
            : null
        }
        isOpen={deleteTarget !== null}
        isPending={deleteMutation.isPending}
        title="Удалить вспомогательное СИ"
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
      />
    </section>
  );
}
