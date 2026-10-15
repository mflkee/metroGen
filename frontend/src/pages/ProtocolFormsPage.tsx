import { useMemo, useState } from "react";

import { useQuery } from "@tanstack/react-query";

import {
  fetchTemplateCatalog,
  fetchTemplateRules,
  previewTemplateRule,
  type TemplateOut,
  type TemplatePreview,
  type TemplateRule,
} from "@/api/templates";
import { ExpandableItem } from "@/components/ExpandableItem";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { useAuthStore } from "@/store/auth";

const KIND_LABELS: Record<string, string> = {
  manometers: "Манометры",
  controllers: "Контроллеры",
  thermometers: "Термопреобразователи",
  level_meters: "Уровнемеры",
};

const MATCH_FIELD_LABELS: Record<string, string> = {
  mitype_number: "рег. номер типа",
  title_keyword: "слова в названии типа",
  methodology_code: "код методики",
  modification: "исполнение (модификация)",
};

const MATCH_FIELD_EXAMPLES: Record<string, string> = {
  mitype_number: "86065-22",
  title_keyword: "УРОВНЕМЕР",
  methodology_code: "МП 1657-7-2024",
  modification: "901.1 / FMP51",
};

const STAGE_LABELS: Record<string, string> = {
  override: "явное указание формы",
  rule: "правило",
  methodology: "форма методики",
  fallback: "встроенная эвристика",
};

function kindLabel(kind: string): string {
  return KIND_LABELS[kind] ?? kind;
}

/**
 * «Формы протоколов» — обзор, а не редактор.
 *
 * Отвечает на три вопроса: сколько форм, какая от какой наследуется и почему конкретная строка
 * поверки получила именно эту форму. Редактирование форм живёт в API (структура, версии, публикация) и
 * в интерфейсе намеренно не предлагается — см. change `simplify-forms-section`.
 */
export function ProtocolFormsPage() {
  const token = useAuthStore((state) => state.token);

  const [kindFilter, setKindFilter] = useState("all");
  const [inspectorKind, setInspectorKind] = useState("level_meters");
  const [inspectorMitype, setInspectorMitype] = useState("");
  const [inspectorTitle, setInspectorTitle] = useState("");
  const [inspectorMethod, setInspectorMethod] = useState("");
  const [inspectorModification, setInspectorModification] = useState("");
  const [preview, setPreview] = useState<TemplatePreview | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [isPreviewing, setIsPreviewing] = useState(false);

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

  const forms = useMemo(() => catalogQuery.data?.templates ?? [], [catalogQuery.data]);
  const rules = useMemo(() => rulesQuery.data ?? [], [rulesQuery.data]);
  const titles = useMemo(() => {
    const map = new Map<string, string>();
    for (const form of forms) {
      map.set(form.id, form.title);
    }
    return map;
  }, [forms]);

  const rulesByForm = useMemo(() => {
    const map = new Map<string, TemplateRule[]>();
    for (const rule of rules) {
      const list = map.get(rule.template_id) ?? [];
      list.push(rule);
      map.set(rule.template_id, list);
    }
    return map;
  }, [rules]);

  /** Базовая форма, под ней — производные; группы по типу прибора. */
  const grouped = useMemo(() => {
    const groups = new Map<string, { base: TemplateOut[]; children: Map<string, TemplateOut[]> }>();
    for (const form of forms) {
      if (kindFilter !== "all" && form.instrument_kind !== kindFilter) {
        continue;
      }
      const entry: { base: TemplateOut[]; children: Map<string, TemplateOut[]> } =
        groups.get(form.instrument_kind) ?? {
          base: [],
          children: new Map<string, TemplateOut[]>(),
        };
      if (form.parent_code) {
        const list = entry.children.get(form.parent_code) ?? [];
        list.push(form);
        entry.children.set(form.parent_code, list);
      } else {
        entry.base.push(form);
      }
      groups.set(form.instrument_kind, entry);
    }
    return [...groups.entries()].sort(([a], [b]) => kindLabel(a).localeCompare(kindLabel(b)));
  }, [forms, kindFilter]);

  const totalForms = forms.length;

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
    } catch (error) {
      setPreviewError(error instanceof Error ? error.message : "Не удалось выполнить предпросмотр.");
    } finally {
      setIsPreviewing(false);
    }
  }

  function renderForm(form: TemplateOut, nested: boolean) {
    const formRules = rulesByForm.get(form.id) ?? [];
    return (
      <div key={form.id} className={nested ? "ml-4 border-l border-line pl-3" : ""}>
        <ExpandableItem
          header={
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-semibold text-ink">{form.title}</span>
                <span className="status-chip">{form.parent_code ? "производная" : "база"}</span>
                <span className={["status-chip", form.drives_protocol ? "status-chip--ok" : ""].join(" ")}>
                  {form.drives_protocol ? "протокол из структуры" : "протокол из шаблона"}
                </span>
              </div>
              <div className="mt-1 text-xs text-steel">
                {form.id}
                {form.parent_code ? ` · наследует от «${titles.get(form.parent_code) ?? form.parent_code}»` : ""}
                {form.children.length
                  ? ` · производные: ${form.children.map((child) => titles.get(child) ?? child).join(", ")}`
                  : ""}
              </div>
            </div>
          }
        >
          {formRules.length ? (
            <div className="overflow-x-auto rounded-xl border border-line">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Приоритет</th>
                    <th>Признак</th>
                    <th>Значение</th>
                    <th>Статус</th>
                  </tr>
                </thead>
                <tbody>
                  {formRules.map((rule) => (
                    <tr key={rule.id}>
                      <td className="text-steel">#{rule.priority}</td>
                      <td className="text-ink">
                        {MATCH_FIELD_LABELS[rule.match_field] ?? rule.match_field}
                      </td>
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
            <p className="text-sm text-steel">
              Правил нет — форма выбирается встроенной эвристикой.
            </p>
          )}
        </ExpandableItem>
      </div>
    );
  }

  return (
    <section className="space-y-6">
      <PageHeader
        title="Формы протоколов"
        description="Сколько форм, какая от какой наследуется и почему строка поверки получает именно эту форму."
      />

      <section className="section-card space-y-2">
        <h3 className="font-semibold text-ink">Как выбирается форма</h3>
        <p className="text-sm text-steel">
          Форма протокола выбирается по трём вещам: <span className="text-ink">методика поверки</span>,{" "}
          <span className="text-ink">описание типа</span> (рег. номер и название) и{" "}
          <span className="text-ink">исполнение</span> — конкретная модификация внутри типа
          (<span className="font-mono">901.1</span>, <span className="font-mono">FMP51</span>). Правила
          применяются по приоритету: меньше число — раньше. Если ни одно правило не подошло, форму
          выбирает встроенная эвристика.
        </p>
        <p className="text-xs text-steel">
          Признаки:{" "}
          {Object.entries(MATCH_FIELD_LABELS).map(([value, label]) => (
            <span key={value} className="mr-3 whitespace-nowrap">
              {label} <span className="font-mono">{MATCH_FIELD_EXAMPLES[value]}</span>
            </span>
          ))}
        </p>
      </section>

      <section className="section-card space-y-4">
        <div>
          <h3 className="font-semibold text-ink">Почему эта форма</h3>
          <p className="mt-1 text-sm text-steel">
            Укажите, что известно о приборе, — ответ покажет ту же цепочку, по которой решает генерация.
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
            Исполнение
            <input className="form-input mt-1" placeholder="901.1 / FMP51" type="text" value={inspectorModification} onChange={(e) => setInspectorModification(e.target.value)} />
          </label>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button className="btn-primary btn-sm" disabled={isPreviewing} type="button" onClick={() => void runPreview()}>
            {isPreviewing ? "Считаем..." : "Показать форму"}
          </button>
          {preview ? (
            <span className="status-chip status-chip--ok">
              {titles.get(preview.template_id) ?? preview.template_id} ·{" "}
              {STAGE_LABELS[preview.source] ?? preview.source}
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
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="font-semibold text-ink">Формы и правила</h3>
            <p className="mt-1 text-sm text-steel">
              Всего форм: {totalForms}. Базовая форма — та, у которой нет родителя.
            </p>
          </div>
          <Select
            className="max-w-[220px]"
            compact
            onChange={setKindFilter}
            options={[
              { value: "all", label: "Все типы приборов" },
              ...(catalogQuery.data?.instrument_kinds ?? []).map((value) => ({
                value,
                label: kindLabel(value),
              })),
            ]}
            value={kindFilter}
          />
        </div>

        {catalogQuery.isLoading || rulesQuery.isLoading ? (
          <p className="text-sm text-steel">Загрузка...</p>
        ) : null}
        {catalogQuery.isError ? (
          <p className="text-sm text-[var(--danger-text)]">Не удалось загрузить каталог форм.</p>
        ) : null}

        {grouped.map(([kind, entry]) => (
          <div key={kind} className="space-y-3">
            <div className="text-xs uppercase tracking-[0.16em] text-steel">
              {kindLabel(kind)} · {entry.base.length + [...entry.children.values()].flat().length} форм
            </div>
            {entry.base.map((base) => (
              <div key={base.id} className="space-y-3">
                {renderForm(base, false)}
                {(entry.children.get(base.id) ?? []).map((child) => renderForm(child, true))}
              </div>
            ))}
            {/* Производные без родителя в этой выборке (фильтр отрезал базу) — показываем как есть. */}
            {[...entry.children.entries()]
              .filter(([parentId]) => !entry.base.some((base) => base.id === parentId))
              .flatMap(([, children]) => children.map((child) => renderForm(child, false)))}
          </div>
        ))}
      </section>
    </section>
  );
}
