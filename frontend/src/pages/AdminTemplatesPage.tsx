import { FormEvent, useEffect, useMemo, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createTemplateRule,
  deleteTemplateRule,
  fetchTemplateCatalog,
  fetchTemplateRules,
  previewTemplateRule,
  updateTemplateRule,
  type TemplatePreview,
  type TemplateRule,
} from "@/api/templates";
import { DeleteConfirmModal } from "@/components/DeleteConfirmModal";
import { ExpandableItem } from "@/components/ExpandableItem";
import { Modal } from "@/components/Modal";
import { NumberInput } from "@/components/number-input";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useAuthStore } from "@/store/auth";

type RuleModal =
  | { mode: "create" }
  | { mode: "edit"; rule: TemplateRule }
  | null;

const KIND_LABELS: Record<string, string> = {
  manometers: "Манометры",
  controllers: "Контроллеры",
  thermometers: "Термопреобразователи",
  level_meters: "Уровнемеры",
};

const MATCH_FIELD_LABELS: Record<string, string> = {
  mitype_number: "Номер типа (точное совпадение)",
  title_keyword: "Ключевые слова в названии (через запятую, все обязательны)",
  methodology_code: "Код методики (вхождение)",
};

const SOURCE_LABELS: Record<string, string> = {
  override: "Явное указание формы",
  rule: "Правило",
  methodology: "Форма методики",
  fallback: "Встроенная эвристика",
};

function kindLabel(kind: string): string {
  return KIND_LABELS[kind] ?? kind;
}

/**
 * Правила выбора формы протокола.
 *
 * Экран **намеренно не подключён** к роутеру и навигации: раздел ещё не доделан (нужен редактор
 * собственных форм), поэтому в прод он пока не выходит. Backend-часть (таблица правил,
 * `resolve_form`, сид под текущие эвристики) работает и от этого экрана не зависит. Чтобы вернуть:
 * добавить lazy-импорт и роут `/admin/templates` в `app/router.tsx` и пункт в `lib/nav.ts`.
 */
export function AdminTemplatesPage() {
  const token = useAuthStore((state) => state.token);
  const queryClient = useQueryClient();
  const [modal, setModal] = useState<RuleModal>(null);
  const [deleteTarget, setDeleteTarget] = useState<TemplateRule | null>(null);

  const [kind, setKind] = useState("manometers");
  const [matchField, setMatchField] = useState("mitype_number");
  const [matchValue, setMatchValue] = useState("");
  const [templateId, setTemplateId] = useState("");
  const [priority, setPriority] = useState("100");
  const [isActive, setIsActive] = useState(true);

  const [previewKind, setPreviewKind] = useState("manometers");
  const [previewMitype, setPreviewMitype] = useState("");
  const [previewTitle, setPreviewTitle] = useState("");
  const [previewMethod, setPreviewMethod] = useState("");
  const [previewResult, setPreviewResult] = useState<TemplatePreview | null>(null);

  const catalogQuery = useQuery({
    queryKey: ["template-catalog"],
    queryFn: () => fetchTemplateCatalog(token ?? ""),
    enabled: Boolean(token),
  });

  const rulesQuery = useQuery({
    queryKey: ["template-rules"],
    queryFn: () => fetchTemplateRules(token ?? ""),
    enabled: Boolean(token),
  });

  const templateOptions = useMemo(
    () => (catalogQuery.data?.templates ?? []).map((item) => ({ value: item.id, label: item.title })),
    [catalogQuery.data],
  );

  const templateTitles = useMemo(() => {
    const map = new Map<string, string>();
    for (const item of catalogQuery.data?.templates ?? []) {
      map.set(item.id, item.title);
    }
    return map;
  }, [catalogQuery.data]);

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        instrument_kind: kind,
        match_field: matchField,
        match_value: matchValue.trim(),
        template_id: templateId,
        priority: Number.parseInt(priority, 10) || 100,
        is_active: isActive,
      };
      if (modal?.mode === "edit") {
        await updateTemplateRule(token ?? "", modal.rule.id, payload);
        return;
      }
      await createTemplateRule(token ?? "", payload);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["template-rules"] });
      setModal(null);
    },
  });

  const toggleMutation = useMutation({
    mutationFn: (rule: TemplateRule) =>
      updateTemplateRule(token ?? "", rule.id, { is_active: !rule.is_active }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["template-rules"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (ruleId: number) => deleteTemplateRule(token ?? "", ruleId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["template-rules"] });
      setDeleteTarget(null);
    },
  });

  const previewMutation = useMutation({
    mutationFn: () =>
      previewTemplateRule(token ?? "", {
        instrument_kind: previewKind,
        mitype_number: previewMitype.trim() || null,
        mitype_title: previewTitle.trim() || null,
        method_code: previewMethod.trim() || null,
      }),
    onSuccess: (result) => setPreviewResult(result),
  });

  const rules = useMemo(() => rulesQuery.data ?? [], [rulesQuery.data]);

  useEffect(() => {
    if (!modal) {
      return;
    }
    if (modal.mode === "edit") {
      setKind(modal.rule.instrument_kind);
      setMatchField(modal.rule.match_field);
      setMatchValue(modal.rule.match_value);
      setTemplateId(modal.rule.template_id);
      setPriority(String(modal.rule.priority));
      setIsActive(modal.rule.is_active);
      return;
    }
    setKind(catalogQuery.data?.instrument_kinds[0] ?? "manometers");
    setMatchField(catalogQuery.data?.match_fields[0] ?? "mitype_number");
    setMatchValue("");
    setTemplateId(catalogQuery.data?.templates[0]?.id ?? "");
    setPriority("100");
    setIsActive(true);
  }, [modal, catalogQuery.data]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!matchValue.trim() || !templateId) {
      return;
    }
    saveMutation.mutate();
  }

  return (
    <section className="space-y-6">
      <PageHeader
        title="Формы протоколов"
        description="Правила выбора формы протокола: тип прибора и условие (номер типа, ключевые слова или код методики) → шаблон. Порядок — по приоритету."
      />

      <section className="section-card space-y-4">
        <div>
          <h3 className="font-semibold text-ink">Предпросмотр</h3>
          <p className="mt-1 text-sm text-steel">
            Показывает, какая форма развернётся для описанных данных и почему.
          </p>
        </div>
        <div className="grid gap-3 md:grid-cols-4">
          <label className="block text-sm text-steel">
            Тип прибора
            <Select
              className="mt-1"
              onChange={setPreviewKind}
              options={(catalogQuery.data?.instrument_kinds ?? []).map((value) => ({
                value,
                label: kindLabel(value),
              }))}
              value={previewKind}
            />
          </label>
          <label className="block text-sm text-steel">
            Номер типа
            <input className="form-input mt-1" placeholder="86065-22" type="text" value={previewMitype} onChange={(e) => setPreviewMitype(e.target.value)} />
          </label>
          <label className="block text-sm text-steel">
            Название типа
            <input className="form-input mt-1" placeholder="Уровнемер..." type="text" value={previewTitle} onChange={(e) => setPreviewTitle(e.target.value)} />
          </label>
          <label className="block text-sm text-steel">
            Методика
            <input className="form-input mt-1" placeholder="МИ 2124-90" type="text" value={previewMethod} onChange={(e) => setPreviewMethod(e.target.value)} />
          </label>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button className="btn-primary btn-sm" disabled={previewMutation.isPending} type="button" onClick={() => previewMutation.mutate()}>
            {previewMutation.isPending ? "Проверяем..." : "Проверить"}
          </button>
          {previewResult ? (
            <span className="status-chip status-chip--ok">
              {templateTitles.get(previewResult.template_id) ?? previewResult.template_id} ·{" "}
              {SOURCE_LABELS[previewResult.source] ?? previewResult.source}
              {previewResult.rule_id != null ? ` (правило #${previewResult.rule_id})` : ""}
            </span>
          ) : null}
        </div>
        {previewMutation.isError ? (
          <p className="text-sm text-[var(--danger-text)]">
            {previewMutation.error instanceof Error ? previewMutation.error.message : "Не удалось выполнить предпросмотр."}
          </p>
        ) : null}
      </section>

      <div className="section-card space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <button className="btn-primary btn-sm" type="button" onClick={() => setModal({ mode: "create" })}>
            Добавить правило
          </button>
          <span className="status-chip">Всего: {rules.length}</span>
        </div>

        {rulesQuery.isLoading ? <p className="text-sm text-steel">Загрузка...</p> : null}
        {rulesQuery.isError ? (
          <p className="text-sm text-[var(--danger-text)]">Не удалось загрузить список правил.</p>
        ) : null}

        <div className="space-y-3">
          {!rulesQuery.isLoading && !rulesQuery.isError && rules.length === 0 ? (
            <p className="text-sm text-steel">
              Правил нет. Форма выбирается встроенными эвристиками.
            </p>
          ) : null}

          {rules.map((rule) => (
            <ExpandableItem
              key={rule.id}
              actions={
                <>
                  <button
                    className="btn-secondary btn-sm"
                    disabled={toggleMutation.isPending}
                    type="button"
                    onClick={() => toggleMutation.mutate(rule)}
                  >
                    {rule.is_active ? "Выключить" : "Включить"}
                  </button>
                  <button className="btn-secondary btn-sm" type="button" onClick={() => setModal({ mode: "edit", rule })}>
                    Изменить
                  </button>
                  <button className="btn-danger btn-sm" type="button" onClick={() => setDeleteTarget(rule)}>
                    Удалить
                  </button>
                </>
              }
              header={
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="status-chip">#{rule.priority}</span>
                    <span className="font-semibold text-ink">{kindLabel(rule.instrument_kind)}</span>
                    <span className={["status-chip", rule.is_active ? "status-chip--ok" : ""].join(" ")}>
                      {rule.is_active ? "Включено" : "Выключено"}
                    </span>
                  </div>
                  <div className="mt-1 text-sm text-steel">
                    {MATCH_FIELD_LABELS[rule.match_field] ?? rule.match_field}: «{rule.match_value}»
                  </div>
                  <div className="mt-1 text-sm text-ink">
                    → {templateTitles.get(rule.template_id) ?? rule.template_id}
                  </div>
                </div>
              }
            >
              <dl className="grid gap-2 text-sm sm:grid-cols-2">
                <div>
                  <dt className="text-xs uppercase tracking-[0.16em] text-steel">Тип прибора</dt>
                  <dd className="text-ink">{kindLabel(rule.instrument_kind)}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-[0.16em] text-steel">Условие</dt>
                  <dd className="text-ink">{MATCH_FIELD_LABELS[rule.match_field] ?? rule.match_field}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-[0.16em] text-steel">Значение</dt>
                  <dd className="break-all text-ink">{rule.match_value}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-[0.16em] text-steel">Форма</dt>
                  <dd className="text-ink">{templateTitles.get(rule.template_id) ?? rule.template_id}</dd>
                </div>
              </dl>
            </ExpandableItem>
          ))}
        </div>
      </div>

      <Modal
        description={
          modal?.mode === "edit"
            ? "Измените условие, форму или приоритет правила."
            : "Опишите, какой форме соответствует тип прибора."
        }
        footer={
          <div className="flex justify-end gap-3">
            <button className="btn-secondary btn-sm" type="button" onClick={() => setModal(null)}>
              Отмена
            </button>
            <button className="btn-primary btn-sm" disabled={saveMutation.isPending} form="rule-form" type="submit">
              {saveMutation.isPending ? "Сохраняем..." : "Сохранить"}
            </button>
          </div>
        }
        open={modal !== null}
        title={modal?.mode === "edit" ? "Изменить правило" : "Новое правило"}
        onClose={() => setModal(null)}
      >
        <form className="space-y-4" id="rule-form" onSubmit={handleSubmit}>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="block text-sm text-steel">
              Тип прибора
              <Select
                className="mt-1"
                onChange={setKind}
                options={(catalogQuery.data?.instrument_kinds ?? []).map((value) => ({
                  value,
                  label: kindLabel(value),
                }))}
                value={kind}
              />
            </label>
            <label className="block text-sm text-steel">
              Условие
              <Select
                className="mt-1"
                onChange={setMatchField}
                options={(catalogQuery.data?.match_fields ?? []).map((value) => ({
                  value,
                  label: MATCH_FIELD_LABELS[value] ?? value,
                }))}
                value={matchField}
              />
            </label>
            <label className="block text-sm text-steel sm:col-span-2">
              Значение условия
              <input
                className="form-input mt-1"
                placeholder={matchField === "title_keyword" ? "УРОВНЕМЕР" : "86065-22"}
                required
                type="text"
                value={matchValue}
                onChange={(e) => setMatchValue(e.target.value)}
              />
            </label>
            <label className="block text-sm text-steel">
              Форма
              <Select className="mt-1" onChange={setTemplateId} options={templateOptions} value={templateId} />
            </label>
            <label className="block text-sm text-steel">
              Приоритет
              <NumberInput className="form-input mt-1" maxLength={4} value={priority} onValueChange={setPriority} />
            </label>
          </div>
          <label className="flex items-center gap-3 rounded-2xl border border-line px-4 py-3 text-sm text-ink" htmlFor="rule-active">
            <Switch checked={isActive} id="rule-active" onCheckedChange={setIsActive} />
            Правило включено
          </label>
          {saveMutation.isError ? (
            <p className="text-sm text-[var(--danger-text)]">
              {saveMutation.error instanceof Error ? saveMutation.error.message : "Не удалось сохранить правило."}
            </p>
          ) : null}
        </form>
      </Modal>

      <DeleteConfirmModal
        description={
          deleteTarget
            ? `Удаляем правило #${deleteTarget.id} для «${kindLabel(deleteTarget.instrument_kind)}».`
            : undefined
        }
        errorMessage={
          deleteMutation.isError
            ? deleteMutation.error instanceof Error
              ? deleteMutation.error.message
              : "Не удалось удалить правило."
            : null
        }
        isOpen={deleteTarget !== null}
        isPending={deleteMutation.isPending}
        title="Удалить правило"
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
      />
    </section>
  );
}
