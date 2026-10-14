import { FormEvent, useEffect, useMemo, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createMethodology,
  deleteMethodology,
  fetchMethodologies,
  replaceMethodologyAliases,
  updateMethodology,
  type MethodologyOut,
} from "@/api/methodologies";
import { DeleteConfirmModal } from "@/components/DeleteConfirmModal";
import { ExpandableItem } from "@/components/ExpandableItem";
import { Modal } from "@/components/Modal";
import { NumberInput } from "@/components/number-input";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { useAuthStore } from "@/store/auth";

type EditablePoint = {
  label: string;
  point_type: string;
  default_text: string;
};

type MethodologyModal =
  | { mode: "create" }
  | { mode: "edit"; methodology: MethodologyOut }
  | null;

const POINT_TYPE_OPTIONS = [
  { value: "clause", label: "clause" },
  { value: "bool", label: "bool" },
  { value: "custom", label: "custom" },
];

function parseAliases(value: string): string[] {
  return value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

export function AdminMethodologiesPage() {
  const token = useAuthStore((state) => state.token);
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [modal, setModal] = useState<MethodologyModal>(null);
  const [code, setCode] = useState("");
  const [title, setTitle] = useState("");
  const [document, setDocument] = useState("");
  const [notes, setNotes] = useState("");
  const [allowable, setAllowable] = useState("");
  const [aliasesText, setAliasesText] = useState("");
  const [points, setPoints] = useState<EditablePoint[]>([]);
  const [deleteTarget, setDeleteTarget] = useState<MethodologyOut | null>(null);

  const methodologiesQuery = useQuery({
    queryKey: ["methodologies", search],
    queryFn: () => fetchMethodologies(token ?? "", search || undefined),
    enabled: Boolean(token),
  });

  const saveMutation = useMutation({
    mutationFn: async () => {
      const validPoints = points
        .filter((point) => point.label.trim() || point.default_text.trim())
        .map((point, index) => ({
          position: index + 1,
          label: point.label.trim(),
          point_type: point.point_type || "clause",
          default_text: point.default_text.trim() || null,
        }));
      const allowableValue = allowable ? Number.parseFloat(allowable) : null;
      const aliases = parseAliases(aliasesText);

      if (modal?.mode === "edit") {
        await updateMethodology(token ?? "", modal.methodology.id, {
          title: title.trim() || undefined,
          document: document.trim() || null,
          notes: notes.trim() || null,
          allowable_variation_pct: allowableValue,
          points: validPoints,
        });
        await replaceMethodologyAliases(token ?? "", modal.methodology.id, aliases);
        return;
      }

      await createMethodology(token ?? "", {
        code: code.trim(),
        title: title.trim() || null,
        document: document.trim() || null,
        notes: notes.trim() || null,
        allowable_variation_pct: allowableValue,
        aliases,
        points: validPoints,
      });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["methodologies"] });
      setModal(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (methodologyId: number) => deleteMethodology(token ?? "", methodologyId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["methodologies"] });
      setDeleteTarget(null);
    },
  });

  const methodologies = useMemo(() => methodologiesQuery.data ?? [], [methodologiesQuery.data]);

  useEffect(() => {
    if (!modal) {
      return;
    }
    if (modal.mode === "edit") {
      const item = modal.methodology;
      setCode(item.code);
      setTitle(item.title);
      setDocument(item.document ?? "");
      setNotes(item.notes ?? "");
      setAllowable(item.allowable_variation_pct != null ? String(item.allowable_variation_pct) : "");
      setAliasesText(item.aliases.join("\n"));
      setPoints(
        item.points.map((point) => ({
          label: point.label,
          point_type: point.point_type,
          default_text: point.default_text ?? "",
        })),
      );
      return;
    }
    setCode("");
    setTitle("");
    setDocument("");
    setNotes("");
    setAllowable("");
    setAliasesText("");
    setPoints([{ label: "", point_type: "clause", default_text: "" }]);
  }, [modal]);

  function updatePoint(index: number, field: keyof EditablePoint, value: string) {
    setPoints((current) => current.map((point, i) => (i === index ? { ...point, [field]: value } : point)));
  }

  function addPoint() {
    setPoints((current) => [...current, { label: "", point_type: "clause", default_text: "" }]);
  }

  function removePoint(index: number) {
    setPoints((current) => current.filter((_, i) => i !== index));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (modal?.mode === "create" && !code.trim()) {
      return;
    }
    if (!points.some((point) => point.label.trim() || point.default_text.trim())) {
      return;
    }
    saveMutation.mutate();
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
          <button className="btn-primary btn-sm" type="button" onClick={() => setModal({ mode: "create" })}>
            Добавить
          </button>
          <span className="status-chip">Всего: {methodologies.length}</span>
        </div>

        {methodologiesQuery.isLoading ? <p className="text-sm text-steel">Загрузка...</p> : null}
        {methodologiesQuery.isError ? (
          <p className="text-sm text-[var(--danger-text)]">Не удалось загрузить список методик.</p>
        ) : null}

        <div className="space-y-3">
          {!methodologiesQuery.isLoading && !methodologiesQuery.isError && methodologies.length === 0 ? (
            <p className="text-sm text-steel">Нет записей.</p>
          ) : null}

          {methodologies.map((methodology) => (
            <ExpandableItem
              key={methodology.id}
              actions={
                <>
                  <button className="btn-secondary btn-sm" type="button" onClick={() => setModal({ mode: "edit", methodology })}>
                    Изменить
                  </button>
                  <button className="btn-danger btn-sm" type="button" onClick={() => setDeleteTarget(methodology)}>
                    Удалить
                  </button>
                </>
              }
              header={
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-semibold text-ink">{methodology.code}</span>
                    {methodology.allowable_variation_pct != null ? (
                      <span className="status-chip">δ {methodology.allowable_variation_pct}%</span>
                    ) : null}
                  </div>
                  <div className="mt-1 text-sm text-steel">{methodology.title}</div>
                  <div className="mt-1 text-xs text-steel">
                    {methodology.points.length} пунктов · {methodology.aliases.length} алиасов
                  </div>
                </div>
              }
            >
              <div className="overflow-x-auto rounded-xl border border-line">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>№</th>
                      <th>Пункт</th>
                      <th>Тип</th>
                      <th>Название</th>
                    </tr>
                  </thead>
                  <tbody>
                    {methodology.points.map((point, index) => (
                      <tr key={`${point.position}-${index}`}>
                        <td className="text-center text-steel">{index + 1}</td>
                        <td className="text-ink">{point.label || "—"}</td>
                        <td className="text-center text-steel">{point.point_type}</td>
                        <td className="text-steel">{point.default_text ?? "—"}</td>
                      </tr>
                    ))}
                    {methodology.points.length === 0 ? (
                      <tr>
                        <td className="text-center text-steel" colSpan={4}>
                          Пунктов нет.
                        </td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>

              <div className="text-xs uppercase tracking-[0.16em] text-steel">Алиасы</div>
              {methodology.aliases.length ? (
                <div className="flex flex-wrap gap-2">
                  {methodology.aliases.map((alias) => (
                    <span key={alias} className="status-chip">
                      {alias}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-steel">Алиасов нет.</p>
              )}
            </ExpandableItem>
          ))}
        </div>
      </div>

      <Modal
        description={
          modal?.mode === "edit"
            ? "Измените методику, её пункты и алиасы."
            : "Заведите методику: код, пункты и алиасы."
        }
        footer={
          <div className="flex justify-end gap-3">
            <button className="btn-secondary btn-sm" type="button" onClick={() => setModal(null)}>
              Отмена
            </button>
            <button className="btn-primary btn-sm" disabled={saveMutation.isPending} form="methodology-form" type="submit">
              {saveMutation.isPending ? "Сохраняем..." : "Сохранить"}
            </button>
          </div>
        }
        open={modal !== null}
        size="xl"
        title={modal?.mode === "edit" ? "Изменить методику" : "Новая методика"}
        onClose={() => setModal(null)}
      >
        <form className="space-y-4" id="methodology-form" onSubmit={handleSubmit}>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="block text-sm text-steel">
              Код методики
              <input
                className="form-input mt-1"
                disabled={modal?.mode === "edit"}
                required
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
            </label>
            <label className="block text-sm text-steel">
              Название
              <input className="form-input mt-1" type="text" value={title} onChange={(e) => setTitle(e.target.value)} />
            </label>
            <label className="block text-sm text-steel">
              Документ
              <input className="form-input mt-1" type="text" value={document} onChange={(e) => setDocument(e.target.value)} />
            </label>
            <label className="block text-sm text-steel">
              Примечание
              <input className="form-input mt-1" type="text" value={notes} onChange={(e) => setNotes(e.target.value)} />
            </label>
            <label className="block text-sm text-steel">
              Допустимая вариация, %
              <NumberInput allowDecimal className="form-input mt-1" value={allowable} onValueChange={setAllowable} />
            </label>
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <span className="text-sm font-medium text-steel">Пункты методики</span>
              <button className="btn-secondary btn-sm" type="button" onClick={addPoint}>
                + Добавить пункт
              </button>
            </div>
            <div className="space-y-2">
              {points.map((point, index) => (
                <div key={index} className="grid gap-2 rounded-xl border border-line p-2 md:grid-cols-[1fr_140px_1fr_auto]">
                  <input
                    className="form-input text-sm"
                    placeholder="Пункт (напр. 8.1)"
                    type="text"
                    value={point.label}
                    onChange={(e) => updatePoint(index, "label", e.target.value)}
                  />
                  <Select
                    compact
                    onChange={(next) => updatePoint(index, "point_type", next)}
                    options={POINT_TYPE_OPTIONS}
                    value={point.point_type}
                  />
                  <input
                    className="form-input text-sm"
                    placeholder="Название"
                    type="text"
                    value={point.default_text}
                    onChange={(e) => updatePoint(index, "default_text", e.target.value)}
                  />
                  <button className="btn-danger btn-sm" type="button" onClick={() => removePoint(index)}>
                    Удалить
                  </button>
                </div>
              ))}
              {points.length === 0 ? <p className="text-sm text-steel">Добавьте хотя бы один пункт.</p> : null}
            </div>
          </div>

          <label className="block text-sm text-steel">
            Алиасы (по одному в строке)
            <textarea
              className="form-input mt-1 min-h-[80px]"
              value={aliasesText}
              onChange={(e) => setAliasesText(e.target.value)}
            />
          </label>

          {saveMutation.isError ? (
            <p className="text-sm text-[var(--danger-text)]">
              {saveMutation.error instanceof Error ? saveMutation.error.message : "Не удалось сохранить методику."}
            </p>
          ) : null}
        </form>
      </Modal>

      <DeleteConfirmModal
        description={
          deleteTarget
            ? `Удаляем методику ${deleteTarget.code}. Действие необратимо.`
            : undefined
        }
        errorMessage={
          deleteMutation.isError
            ? deleteMutation.error instanceof Error
              ? deleteMutation.error.message
              : "Не удалось удалить методику."
            : null
        }
        isOpen={deleteTarget !== null}
        isPending={deleteMutation.isPending}
        title="Удалить методику"
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
      />
    </section>
  );
}
