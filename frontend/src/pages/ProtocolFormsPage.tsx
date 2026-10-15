import { useEffect, useMemo, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  compareForms,
  fetchFormVersions,
  fetchTemplateCatalog,
  fetchTemplateForm,
  fetchTemplateRules,
  previewForm,
  previewTemplateRule,
  publishForm,
  restoreFormVersion,
  saveFormDraft,
  type FormStructure,
  type StructureBlock,
  type TemplateCompare,
  type TemplatePreview,
} from "@/api/templates";
import { ExpandableItem } from "@/components/ExpandableItem";
import { FormGraph, type FormGraphLink, type FormGraphNode } from "@/components/forms/FormGraph";
import { StructureEditor } from "@/components/forms/StructureEditor";
import { Modal } from "@/components/Modal";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { hasAdminAccess } from "@/lib/roles";
import { useAuthStore } from "@/store/auth";

const KIND_LABELS: Record<string, string> = {
  manometers: "Манометры",
  controllers: "Контроллеры",
  thermometers: "Термопреобразователи",
  level_meters: "Уровнемеры",
};

const MATCH_FIELD_LABELS: Record<string, string> = {
  mitype_number: "номер типа",
  title_keyword: "ключевые слова названия",
  methodology_code: "код методики",
  modification: "модификация",
};

const STAGE_LABELS: Record<string, string> = {
  override: "Явное указание формы",
  rule: "Правило",
  methodology: "Форма методики",
  fallback: "Встроенная эвристика",
};

const SOURCE_LABELS: Record<string, string> = {
  override: "явное указание формы",
  rule: "правило",
  methodology: "форма методики",
  fallback: "встроенная эвристика",
};

function kindLabel(kind: string): string {
  return KIND_LABELS[kind] ?? kind;
}

/**
 * The overlay of a derived form: only the tables that differ from the resolved parent structure.
 * Sending the whole structure would freeze every table and stop base edits from propagating.
 */
function buildOverlay(original: FormStructure, draft: FormStructure): FormStructure {
  const before = new Map<string, StructureBlock>();
  for (const section of original.sections ?? []) {
    for (const block of section.blocks ?? []) {
      if (block.type === "table") {
        before.set(`${section.id}/${block.id}`, block);
      }
    }
  }

  const sections: FormStructure["sections"] = [];
  for (const section of draft.sections ?? []) {
    const blocks = (section.blocks ?? [])
      .filter((block) => block.type === "table")
      .filter((block) => {
        const previous = before.get(`${section.id}/${block.id}`);
        return !previous || JSON.stringify(previous) !== JSON.stringify(block);
      })
      .map((block) => ({
        id: block.id,
        type: "table",
        columns: block.columns,
        rows: block.rows,
      }));
    if (blocks.length) {
      sections?.push({ id: section.id, blocks });
    }
  }
  return { schema: draft.schema ?? 1, sections: sections ?? [] };
}

export function ProtocolFormsPage() {
  const token = useAuthStore((state) => state.token);
  const role = useAuthStore((state) => state.user?.role);
  const queryClient = useQueryClient();
  const isAdmin = hasAdminAccess(role);

  const [kindFilter, setKindFilter] = useState("all");
  const [axisFilter, setAxisFilter] = useState("all");
  const [showDisabled, setShowDisabled] = useState(true);
  const [query, setQuery] = useState("");
  const [selectedCode, setSelectedCode] = useState<string | null>(null);

  const [inspectorKind, setInspectorKind] = useState("level_meters");
  const [inspectorMitype, setInspectorMitype] = useState("");
  const [inspectorTitle, setInspectorTitle] = useState("");
  const [inspectorMethod, setInspectorMethod] = useState("");
  const [inspectorModification, setInspectorModification] = useState("");
  const [preview, setPreview] = useState<TemplatePreview | null>(null);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [draft, setDraft] = useState<FormStructure | null>(null);
  const [publishComment, setPublishComment] = useState("");
  const [previewHtml, setPreviewHtml] = useState<string | null>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [editorError, setEditorError] = useState<string | null>(null);
  const [compareOpen, setCompareOpen] = useState(false);
  const [compareOther, setCompareOther] = useState("");
  const [compareLeft, setCompareLeft] = useState("");
  const [compareRight, setCompareRight] = useState("");
  const [compareResult, setCompareResult] = useState<TemplateCompare | null>(null);

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
  const formQuery = useQuery({
    queryKey: ["template-form", selectedCode],
    queryFn: () => fetchTemplateForm(token ?? "", selectedCode as string),
    enabled: Boolean(token) && selectedCode !== null,
  });

  const versionsQuery = useQuery({
    queryKey: ["template-form-versions", selectedCode],
    queryFn: () => fetchFormVersions(token ?? "", selectedCode as string),
    enabled: Boolean(token) && (historyOpen || compareOpen) && selectedCode !== null,
  });

  const saveDraftMutation = useMutation({
    mutationFn: (options?: { rendererOnly?: "html" | "data" }) => {
      if (options?.rendererOnly) {
        return saveFormDraft(token ?? "", selectedCode as string, {
          renderer: options.rendererOnly,
        });
      }
      const resolved = formQuery.data?.structure ?? {};
      const payload = formQuery.data?.form.parent_code
        ? { overlay: buildOverlay(resolved, draft ?? {}) }
        : { structure: draft ?? {} };
      return saveFormDraft(token ?? "", selectedCode as string, payload);
    },
    onSuccess: (detail) => {
      setDraft(detail.structure);
      setEditorError(null);
      void queryClient.invalidateQueries({ queryKey: ["template-form", selectedCode] });
      void queryClient.invalidateQueries({ queryKey: ["template-catalog"] });
    },
    onError: (error) =>
      setEditorError(error instanceof Error ? error.message : "Не удалось сохранить черновик."),
  });

  const compareMutation = useMutation({
    mutationFn: () =>
      compareForms(
        token ?? "",
        selectedCode as string,
        compareOther
          ? { other_code: compareOther }
          : { left_revision: Number(compareLeft), right_revision: Number(compareRight) },
      ),
    onSuccess: (result) => setCompareResult(result),
    onError: (error) =>
      setEditorError(error instanceof Error ? error.message : "Не удалось сравнить формы."),
  });

  const publishMutation = useMutation({
    mutationFn: () => publishForm(token ?? "", selectedCode as string, publishComment.trim() || null),
    onSuccess: () => {
      setPublishComment("");
      setEditorError(null);
      void queryClient.invalidateQueries({ queryKey: ["template-form-versions", selectedCode] });
    },
    onError: (error) =>
      setEditorError(error instanceof Error ? error.message : "Не удалось опубликовать форму."),
  });

  const previewMutation = useMutation({
    mutationFn: () => previewForm(token ?? "", selectedCode as string),
    onSuccess: (html) => setPreviewHtml(html),
    onError: (error) =>
      setEditorError(error instanceof Error ? error.message : "Не удалось собрать предпросмотр."),
  });

  const restoreMutation = useMutation({
    mutationFn: (revision: number) =>
      restoreFormVersion(token ?? "", selectedCode as string, revision),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["template-form", selectedCode] });
      void queryClient.invalidateQueries({ queryKey: ["template-form-versions", selectedCode] });
    },
    onError: (error) =>
      setEditorError(error instanceof Error ? error.message : "Не удалось восстановить версию."),
  });

  useEffect(() => {
    setDraft(formQuery.data?.structure ?? null);
    setEditorError(null);
    setPreviewHtml(null);
  }, [formQuery.data]);

  const forms = useMemo(() => catalogQuery.data?.templates ?? [], [catalogQuery.data]);
  const rules = useMemo(() => rulesQuery.data ?? [], [rulesQuery.data]);
  const titles = useMemo(() => {
    const map = new Map<string, string>();
    for (const form of forms) {
      map.set(form.id, form.title);
    }
    return map;
  }, [forms]);

  const visibleForms = useMemo(
    () => forms.filter((form) => kindFilter === "all" || form.instrument_kind === kindFilter),
    [forms, kindFilter],
  );

  const visibleRules = useMemo(
    () =>
      rules.filter((rule) => {
        if (!showDisabled && !rule.is_active) return false;
        if (kindFilter !== "all" && rule.instrument_kind !== kindFilter) return false;
        if (axisFilter !== "all" && rule.match_field !== axisFilter) return false;
        return true;
      }),
    [rules, kindFilter, axisFilter, showDisabled],
  );

  const { nodes, links } = useMemo(() => {
    const formNodes: FormGraphNode[] = visibleForms.map((form) => ({
      id: form.id,
      label: form.title.length > 28 ? `${form.title.slice(0, 27)}…` : form.title,
      type: "form",
      isBase: form.parent_code === null,
      renderer: form.renderer,
      subtitle: `${form.id} ${kindLabel(form.instrument_kind)}`,
    }));
    const conditionNodes: FormGraphNode[] = visibleRules.map((rule) => ({
      id: `rule-${rule.id}`,
      label: rule.match_value.length > 20 ? `${rule.match_value.slice(0, 19)}…` : rule.match_value,
      type: "condition",
      subtitle: `${MATCH_FIELD_LABELS[rule.match_field] ?? rule.match_field} · ${kindLabel(rule.instrument_kind)}`,
    }));
    const knownForms = new Set(visibleForms.map((form) => form.id));
    const inheritanceLinks: FormGraphLink[] = visibleForms
      .filter((form) => form.parent_code && knownForms.has(form.parent_code))
      .map((form) => ({ source: form.parent_code as string, target: form.id, type: "inherits" }));
    const bindingLinks: FormGraphLink[] = visibleRules
      .filter((rule) => knownForms.has(rule.template_id))
      .map((rule) => ({ source: `rule-${rule.id}`, target: rule.template_id, type: "binds" }));
    return {
      nodes: [...formNodes, ...conditionNodes],
      links: [...inheritanceLinks, ...bindingLinks],
    };
  }, [visibleForms, visibleRules]);

  async function runPreview() {
    if (!token) return;
    setIsPreviewing(true);
    setPreviewError(null);
    try {
      const result = await previewTemplateRule(token, {
        instrument_kind: inspectorKind,
        mitype_number: inspectorMitype.trim() || null,
        mitype_title: inspectorTitle.trim() || null,
        method_code: inspectorMethod.trim() || null,
        modification: inspectorModification.trim() || null,
      });
      setPreview(result);
      setSelectedCode(result.template_id);
    } catch (error) {
      setPreviewError(error instanceof Error ? error.message : "Не удалось выполнить предпросмотр.");
    } finally {
      setIsPreviewing(false);
    }
  }

  const groupedKinds = useMemo(() => {
    const groups = new Map<string, typeof visibleForms>();
    for (const form of visibleForms) {
      const list = groups.get(form.instrument_kind) ?? [];
      list.push(form);
      groups.set(form.instrument_kind, list);
    }
    return [...groups.entries()];
  }, [visibleForms]);

  const selectedRules = useMemo(
    () => rules.filter((rule) => rule.template_id === selectedCode),
    [rules, selectedCode],
  );

  return (
    <section className="space-y-6">
      <PageHeader
        title="Формы протоколов"
        description="Какие формы бывают, что от чего наследуется и почему конкретная строка поверки получает именно эту форму."
      />

      <section className="section-card space-y-4">
        <div>
          <h3 className="font-semibold text-ink">Почему эта форма</h3>
          <p className="mt-1 text-sm text-steel">
            Укажите, что известно о приборе: рег. номер типа, название, методику и модификацию. Ответ —
            та же цепочка, по которой решает генерация.
          </p>
        </div>
        <div className="grid gap-3 md:grid-cols-5">
          <label className="block text-sm text-steel">
            Тип прибора
            <Select
              className="mt-1"
              onChange={setInspectorKind}
              options={(catalogQuery.data?.instrument_kinds ?? []).map((value) => ({
                value,
                label: kindLabel(value),
              }))}
              value={inspectorKind}
            />
          </label>
          <label className="block text-sm text-steel">
            Номер типа
            <input className="form-input mt-1" placeholder="86065-22" type="text" value={inspectorMitype} onChange={(e) => setInspectorMitype(e.target.value)} />
          </label>
          <label className="block text-sm text-steel">
            Название типа
            <input className="form-input mt-1" placeholder="Уровнемеры многофазные" type="text" value={inspectorTitle} onChange={(e) => setInspectorTitle(e.target.value)} />
          </label>
          <label className="block text-sm text-steel">
            Методика
            <input className="form-input mt-1" placeholder="МП 1657-7-2024" type="text" value={inspectorMethod} onChange={(e) => setInspectorMethod(e.target.value)} />
          </label>
          <label className="block text-sm text-steel">
            Модификация
            <input className="form-input mt-1" placeholder="901.1 / FMP51" type="text" value={inspectorModification} onChange={(e) => setInspectorModification(e.target.value)} />
          </label>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button className="btn-primary btn-sm" disabled={isPreviewing} type="button" onClick={() => void runPreview()}>
            {isPreviewing ? "Считаем..." : "Показать форму"}
          </button>
          {preview ? (
            <span className="status-chip status-chip--ok">
              {titles.get(preview.template_id) ?? preview.template_id} · {SOURCE_LABELS[preview.source] ?? preview.source}
              {preview.rule_id != null ? ` (правило #${preview.rule_id})` : ""}
            </span>
          ) : null}
        </div>
        {previewError ? <p className="text-sm text-[var(--danger-text)]">{previewError}</p> : null}
        {preview ? (
          <ol className="space-y-1 text-sm">
            {preview.steps.map((step, index) => (
              <li key={`${step.stage}-${index}`} className={step.matched ? "text-ink" : "text-steel"}>
                {step.matched ? "●" : "○"} {STAGE_LABELS[step.stage] ?? step.stage}
                {step.matched && step.match_field
                  ? ` — ${MATCH_FIELD_LABELS[step.match_field] ?? step.match_field} «${step.match_value}»`
                  : ""}
                {step.matched && step.methodology_code ? ` — ${step.methodology_code}` : ""}
                {step.matched ? ` → ${titles.get(step.template_id ?? "") ?? step.template_id}` : ""}
              </li>
            ))}
          </ol>
        ) : null}
      </section>

      <section className="section-card space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <Select
            className="max-w-[220px]"
            compact
            onChange={setKindFilter}
            options={[
              { value: "all", label: "Все типы приборов" },
              ...(catalogQuery.data?.instrument_kinds ?? []).map((value) => ({ value, label: kindLabel(value) })),
            ]}
            value={kindFilter}
          />
          <Select
            className="max-w-[240px]"
            compact
            onChange={setAxisFilter}
            options={[
              { value: "all", label: "Все оси" },
              ...(catalogQuery.data?.match_fields ?? []).map((value) => ({
                value,
                label: MATCH_FIELD_LABELS[value] ?? value,
              })),
            ]}
            value={axisFilter}
          />
          <input
            className="form-input max-w-[260px]"
            placeholder="Поиск по графу..."
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <label className="flex items-center gap-2 text-sm text-steel" htmlFor="forms-show-disabled">
            <Switch checked={showDisabled} id="forms-show-disabled" onCheckedChange={setShowDisabled} />
            Показывать выключенные правила
          </label>
        </div>

        {catalogQuery.isLoading || rulesQuery.isLoading ? (
          <p className="text-sm text-steel">Загрузка...</p>
        ) : (
          <FormGraph
            links={links}
            nodes={nodes}
            query={query}
            selectedId={selectedCode}
            onSelect={(id) => {
              if (!id.startsWith("rule-")) setSelectedCode(id);
            }}
          />
        )}
      </section>

      {selectedCode ? (
        <section className="section-card space-y-3">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h3 className="font-semibold text-ink">{titles.get(selectedCode) ?? selectedCode}</h3>
              <p className="mt-1 text-sm text-steel">
                {formQuery.data?.form.parent_code
                  ? `Наследует от «${titles.get(formQuery.data.form.parent_code) ?? formQuery.data.form.parent_code}»`
                  : "Базовая форма для своего типа прибора"}
                {formQuery.data?.form.children.length
                  ? ` · производные: ${formQuery.data.form.children.map((child) => titles.get(child) ?? child).join(", ")}`
                  : ""}
              </p>
            </div>
            <button
              className="btn-secondary btn-sm"
              disabled
              title="Редактор форм появится отдельным шагом: пока формы рендерятся HTML-шаблонами"
              type="button"
            >
              {formQuery.data?.form.is_editable ? "Редактировать" : "Редактирование пока недоступно"}
            </button>
          </div>
          {selectedRules.length ? (
            <div className="overflow-x-auto rounded-xl border border-line">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Приоритет</th>
                    <th>Тип прибора</th>
                    <th>Ось</th>
                    <th>Значение</th>
                    <th>Статус</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedRules.map((rule) => (
                    <tr key={rule.id}>
                      <td className="text-steel">#{rule.priority}</td>
                      <td className="text-ink">{kindLabel(rule.instrument_kind)}</td>
                      <td className="text-ink">{MATCH_FIELD_LABELS[rule.match_field] ?? rule.match_field}</td>
                      <td className="break-all text-ink">{rule.match_value}</td>
                      <td>
                        <span className={["status-chip", rule.is_active ? "status-chip--ok" : ""].join(" ")}>
                          {rule.is_active ? "включено" : "выключено"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-steel">Правил, указывающих на эту форму, нет — она выбирается эвристикой.</p>
          )}

          <div className="space-y-3 border-t border-line pt-4">
            <div className="flex flex-wrap items-center gap-3">
              <h4 className="font-semibold text-ink">Структура формы</h4>
              <span className="text-xs text-steel">
                {formQuery.data?.form.drives_protocol
                  ? "протокол собирается из этой структуры"
                  : "протокол пока рендерится HTML-шаблоном — правки структуры его не меняют"}
              </span>
            </div>

            {draft ? (
              <StructureEditor
                instrumentKind={formQuery.data?.form.instrument_kind}
                overlayKeys={formQuery.data?.overlay_keys ?? []}
                readOnly={!isAdmin}
                structure={draft}
                onChange={setDraft}
              />
            ) : (
              <p className="text-sm text-steel">Структура загружается...</p>
            )}

            {formQuery.data?.problems.length ? (
              <p className="text-sm text-[var(--danger-text)]">
                Проблемы структуры: {formQuery.data.problems.join("; ")}
              </p>
            ) : null}

            {isAdmin ? (
              <div className="flex flex-wrap items-center gap-3">
                <button
                  className="btn-primary btn-sm"
                  disabled={saveDraftMutation.isPending}
                  type="button"
                  onClick={() => saveDraftMutation.mutate({})}
                >
                  {saveDraftMutation.isPending ? "Сохраняем..." : "Сохранить черновик"}
                </button>
                <button
                  className="btn-secondary btn-sm"
                  disabled={previewMutation.isPending}
                  type="button"
                  onClick={() => previewMutation.mutate()}
                >
                  {previewMutation.isPending ? "Собираем..." : "Предпросмотр"}
                </button>
                <input
                  className="form-input max-w-[240px]"
                  placeholder="комментарий к публикации"
                  type="text"
                  value={publishComment}
                  onChange={(event) => setPublishComment(event.target.value)}
                />
                <button
                  className="btn-primary btn-sm"
                  disabled={publishMutation.isPending}
                  type="button"
                  onClick={() => publishMutation.mutate()}
                >
                  {publishMutation.isPending ? "Публикуем..." : "Опубликовать"}
                </button>
                <button className="btn-secondary btn-sm" type="button" onClick={() => setHistoryOpen(true)}>
                  История версий
                </button>
                <button
                  className="btn-secondary btn-sm"
                  type="button"
                  onClick={() => {
                    setCompareResult(null);
                    setCompareOpen(true);
                  }}
                >
                  Сравнить
                </button>
                <label className="flex items-center gap-2 text-sm text-steel" htmlFor="form-drives-protocol">
                  <Switch
                    checked={formQuery.data?.form.drives_protocol ?? false}
                    disabled={saveDraftMutation.isPending}
                    id="form-drives-protocol"
                    onCheckedChange={(checked) =>
                      saveDraftMutation.mutate({ rendererOnly: checked ? "data" : "html" })
                    }
                  />
                  протокол собирается из структуры
                </label>
              </div>
            ) : (
              <p className="text-sm text-steel">
                Редактирование доступно администратору и разработчику.
              </p>
            )}

            {editorError ? <p className="text-sm text-[var(--danger-text)]">{editorError}</p> : null}
          </div>
        </section>
      ) : null}

      <section className="section-card space-y-4">
        <h3 className="font-semibold text-ink">Каталог форм</h3>
        {groupedKinds.map(([kind, kindForms]) => (
          <div key={kind} className="space-y-3">
            <div className="text-xs uppercase tracking-[0.16em] text-steel">{kindLabel(kind)}</div>
            {kindForms.map((form) => (
              <ExpandableItem
                key={form.id}
                actions={
                  <button className="btn-secondary btn-sm" type="button" onClick={() => setSelectedCode(form.id)}>
                    Подробнее
                  </button>
                }
                header={
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-semibold text-ink">{form.title}</span>
                      <span className="status-chip">{form.parent_code ? "производная" : "база"}</span>
                      <span className={["status-chip", form.is_editable ? "status-chip--ok" : ""].join(" ")}>
                        {form.renderer === "html" ? "шаблон (HTML)" : "данные"}
                      </span>
                    </div>
                    <div className="mt-1 text-xs text-steel">{form.id}</div>
                  </div>
                }
              >
                <dl className="grid gap-2 text-sm sm:grid-cols-2">
                  <div>
                    <dt className="text-xs uppercase tracking-[0.16em] text-steel">Родитель</dt>
                    <dd className="text-ink">
                      {form.parent_code ? titles.get(form.parent_code) ?? form.parent_code : "—"}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-[0.16em] text-steel">Производные</dt>
                    <dd className="text-ink">
                      {form.children.length
                        ? form.children.map((child) => titles.get(child) ?? child).join(", ")
                        : "—"}
                    </dd>
                  </div>
                  <div className="sm:col-span-2">
                    <dt className="text-xs uppercase tracking-[0.16em] text-steel">Редактирование</dt>
                    <dd className="text-ink">
                      {form.is_editable
                        ? "доступно"
                        : "пока недоступно: форма рендерится HTML-шаблоном, редактор появится отдельным шагом"}
                    </dd>
                  </div>
                </dl>
              </ExpandableItem>
            ))}
          </div>
        ))}
      </section>

      <Modal
        open={previewHtml !== null}
        size="xl"
        title="Предпросмотр черновика"
        onClose={() => setPreviewHtml(null)}
      >
        {previewHtml ? (
          <iframe
            className="preview-frame w-full rounded-2xl border border-line"
            srcDoc={previewHtml}
            style={{ height: "70vh" }}
            title="Предпросмотр формы"
          />
        ) : null}
      </Modal>

      <Modal open={historyOpen} title="История версий" onClose={() => setHistoryOpen(false)}>
        {versionsQuery.isLoading ? <p className="text-sm text-steel">Загрузка...</p> : null}
        {versionsQuery.data?.length ? (
          <div className="space-y-2">
            {versionsQuery.data.map((version) => (
              <div
                key={version.revision}
                className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-line px-4 py-3"
              >
                <div>
                  <div className="font-semibold text-ink">Версия {version.revision}</div>
                  <div className="text-sm text-steel">
                    {version.comment ?? "без комментария"}
                    {version.published_by ? ` · ${version.published_by}` : ""}
                    {version.published_at
                      ? ` · ${new Date(version.published_at).toLocaleString("ru-RU")}`
                      : ""}
                  </div>
                </div>
                <button
                  className="btn-secondary btn-sm"
                  disabled={restoreMutation.isPending || !isAdmin}
                  type="button"
                  onClick={() => restoreMutation.mutate(version.revision)}
                >
                  Восстановить
                </button>
              </div>
            ))}
          </div>
        ) : versionsQuery.isLoading ? null : (
          <p className="text-sm text-steel">Публикаций ещё не было.</p>
        )}
      </Modal>

      <Modal
        open={compareOpen}
        size="xl"
        title="Сравнение"
        onClose={() => setCompareOpen(false)}
      >
        <div className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <label className="block text-sm text-steel">
              Сравнить с формой
              <Select
                className="mt-1"
                onChange={setCompareOther}
                options={[
                  { value: "", label: "— не выбрано (сравнить версии) —" },
                  ...forms
                    .filter((form) => form.id !== selectedCode)
                    .map((form) => ({ value: form.id, label: form.title })),
                ]}
                value={compareOther}
              />
            </label>
            <label className="block text-sm text-steel">
              Версия слева
              <Select
                className="mt-1"
                onChange={setCompareLeft}
                options={[
                  { value: "", label: "—" },
                  ...(versionsQuery.data ?? []).map((version) => ({
                    value: String(version.revision),
                    label: `Версия ${version.revision}`,
                  })),
                ]}
                value={compareLeft}
              />
            </label>
            <label className="block text-sm text-steel">
              Версия справа
              <Select
                className="mt-1"
                onChange={setCompareRight}
                options={[
                  { value: "", label: "—" },
                  ...(versionsQuery.data ?? []).map((version) => ({
                    value: String(version.revision),
                    label: `Версия ${version.revision}`,
                  })),
                ]}
                value={compareRight}
              />
            </label>
          </div>

          <button
            className="btn-primary btn-sm"
            disabled={
              compareMutation.isPending ||
              (!compareOther && (!compareLeft || !compareRight))
            }
            type="button"
            onClick={() => compareMutation.mutate()}
          >
            {compareMutation.isPending ? "Сравниваем..." : "Сравнить"}
          </button>

          {compareResult ? (
            <div className="space-y-2">
              <p className="text-sm text-steel">
                {compareResult.left_label} → {compareResult.right_label}: различий{" "}
                {compareResult.differences.length}
              </p>
              {compareResult.differences.length ? (
                <div className="overflow-x-auto rounded-xl border border-line">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Что</th>
                        <th>Изменение</th>
                        <th>Было</th>
                        <th>Стало</th>
                      </tr>
                    </thead>
                    <tbody>
                      {compareResult.differences.map((difference) => (
                        <tr key={`${difference.path}-${difference.kind}`}>
                          <td className="break-all font-mono text-xs text-ink">{difference.path}</td>
                          <td className="text-steel">
                            {difference.kind === "added"
                              ? "добавлено"
                              : difference.kind === "removed"
                                ? "удалено"
                                : "изменено"}
                          </td>
                          <td className="text-steel">{String(difference.before ?? "—")}</td>
                          <td className="text-ink">{String(difference.after ?? "—")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-sm text-steel">Различий нет — структуры совпадают.</p>
              )}
            </div>
          ) : null}
        </div>
      </Modal>
    </section>
  );
}
