import { useMemo, useState } from "react";

import { useQuery } from "@tanstack/react-query";

import {
  fetchTemplateCatalog,
  fetchTemplateForm,
  fetchTemplateRules,
  previewTemplateRule,
  type TemplatePreview,
} from "@/api/templates";
import { ExpandableItem } from "@/components/ExpandableItem";
import { FormGraph, type FormGraphLink, type FormGraphNode } from "@/components/forms/FormGraph";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
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

export function ProtocolFormsPage() {
  const token = useAuthStore((state) => state.token);

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
    </section>
  );
}
