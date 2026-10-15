import { useEffect, useMemo, useState } from "react";

import type { FormStructure, StructureBlock, StructureSection } from "@/api/templates";

type StructureEditorProps = {
  structure: FormStructure;
  onChange: (next: FormStructure) => void;
  /** Paths the form overrides (from the API) — used to mark an edited table. */
  overlayKeys?: string[];
  /** Instrument kind, to suggest the value sources the generator can produce. */
  instrumentKind?: string;
  readOnly?: boolean;
};

/**
 * The value sources the generators produce, per instrument kind. Kept next to the editor on purpose:
 * it is a hint for the operator, and it changes with the generator.
 */
const COLUMN_SOURCES: Record<string, string[]> = {
  manometers: [
    "si_fwd",
    "si_rev",
    "ref_fwd",
    "ref_rev",
    "err_fwd",
    "err_rev",
    "var_pct",
    "allowable_error",
    "allowable_variation",
  ],
  thermometers: ["si_val", "ref_val", "abs_err", "r0_deviation_pct", "r0_allowable_pct"],
  level_meters: ["si_val", "ref_val", "abs_err", "allowable_error"],
  controllers: ["set_value", "measured_value", "error_pct", "allowable_error"],
};

type EditableTable = {
  section: StructureSection;
  block: StructureBlock;
};

function collectTables(structure: FormStructure): EditableTable[] {
  const tables: EditableTable[] = [];
  for (const section of structure.sections ?? []) {
    for (const block of section.blocks ?? []) {
      if (block.type === "table") {
        tables.push({ section, block });
      }
    }
  }
  return tables;
}

function replaceBlock(
  structure: FormStructure,
  sectionId: string,
  blockId: string,
  update: (block: StructureBlock) => StructureBlock,
): FormStructure {
  return {
    ...structure,
    sections: (structure.sections ?? []).map((section) =>
      section.id !== sectionId
        ? section
        : {
            ...section,
            blocks: (section.blocks ?? []).map((block) =>
              block.id === blockId ? update(block) : block,
            ),
          },
    ),
  };
}

/**
 * The table builder of a form: pick a table, then edit its columns and measurement points.
 *
 * It edits the resolved structure; the page decides what to send back (the whole structure for a
 * base form, an overlay for a derived one).
 */
export function StructureEditor({
  structure,
  onChange,
  overlayKeys = [],
  instrumentKind = "manometers",
  readOnly = false,
}: StructureEditorProps) {
  const tables = useMemo(() => collectTables(structure), [structure]);
  const [selected, setSelected] = useState(0);

  useEffect(() => {
    if (selected >= tables.length) {
      setSelected(0);
    }
  }, [tables.length, selected]);

  if (!tables.length) {
    return (
      <p className="text-sm text-steel">
        В структуре этой формы нет ни одной таблицы. Редактор таблиц появится, когда форма будет
        описана структурой.
      </p>
    );
  }

  const current = tables[Math.min(selected, tables.length - 1)];
  const columns = current.block.columns ?? [];
  const rows = current.block.rows ?? [];
  const isOverridden = overlayKeys.some((key) =>
    key.startsWith(`sections/${current.section.id}/blocks/${current.block.id}`),
  );

  const edit = (update: (block: StructureBlock) => StructureBlock) =>
    onChange(replaceBlock(structure, current.section.id, current.block.id, update));

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm text-steel">
          Таблица
          <select
            className="form-input mt-1"
            value={String(Math.min(selected, tables.length - 1))}
            onChange={(event) => setSelected(Number(event.target.value))}
          >
            {tables.map((table, index) => (
              <option key={`${table.section.id}/${table.block.id}`} value={String(index)}>
                {table.section.title ?? table.section.id} · {table.block.id}
              </option>
            ))}
          </select>
        </label>
        {isOverridden ? (
          <span className="status-chip status-chip--warn">переопределяет родителя</span>
        ) : (
          <span className="status-chip">наследуется от родителя</span>
        )}
        <span className="text-xs text-steel">
          точек: {rows.length} · колонок: {columns.length}
        </span>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-steel">Колонки</span>
            <button
              className="btn-secondary btn-sm"
              disabled={readOnly}
              type="button"
              onClick={() =>
                edit((block) => ({
                  ...block,
                  columns: [...(block.columns ?? []), { id: `col${(block.columns ?? []).length + 1}`, title: "Новая колонка" }],
                }))
              }
            >
              + колонка
            </button>
          </div>
          {columns.map((column, index) => (
            <div key={column.id} className="flex items-center gap-2">
              <span className="w-16 shrink-0 font-mono text-xs text-steel">{column.id}</span>
              <input
                className="form-input text-sm"
                disabled={readOnly}
                placeholder="заголовок"
                type="text"
                value={column.title ?? ""}
                onChange={(event) =>
                  edit((block) => ({
                    ...block,
                    columns: (block.columns ?? []).map((item, itemIndex) =>
                      itemIndex === index ? { ...item, title: event.target.value } : item,
                    ),
                  }))
                }
              />
              <input
                className="form-input max-w-[170px] font-mono text-xs"
                disabled={readOnly}
                list={`column-sources-${current.block.id}`}
                placeholder="источник (si_fwd)"
                type="text"
                value={column.source ?? ""}
                onChange={(event) =>
                  edit((block) => ({
                    ...block,
                    columns: (block.columns ?? []).map((item, itemIndex) =>
                      itemIndex === index ? { ...item, source: event.target.value } : item,
                    ),
                  }))
                }
              />
              <button
                className="btn-danger btn-sm"
                disabled={readOnly || columns.length <= 1}
                type="button"
                onClick={() =>
                  edit((block) => ({
                    ...block,
                    columns: (block.columns ?? []).filter((_, itemIndex) => itemIndex !== index),
                  }))
                }
              >
                ×
              </button>
            </div>
          ))}
          <datalist id={`column-sources-${current.block.id}`}>
            {(COLUMN_SOURCES[instrumentKind] ?? []).map((source) => (
              <option key={source} value={source} />
            ))}
          </datalist>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-steel">Точки замера</span>
            <button
              className="btn-secondary btn-sm"
              disabled={readOnly}
              type="button"
              onClick={() =>
                edit((block) => {
                  const existing = block.rows ?? [];
                  const lastAt = existing.length ? Number(existing[existing.length - 1].at ?? 0) : 0;
                  return {
                    ...block,
                    rows: [
                      ...existing,
                      { id: `p${existing.length}`, kind: "point", at: Math.min(1, lastAt + 0.25) },
                    ],
                  };
                })
              }
            >
              + точка
            </button>
          </div>
          {rows.map((row, index) => (
            <div key={row.id} className="flex items-center gap-2">
              <span className="w-16 shrink-0 font-mono text-xs text-steel">{row.id}</span>
              <input
                className="form-input text-sm"
                disabled={readOnly}
                placeholder="подпись (напр. 50 %)"
                type="text"
                value={row.label ?? ""}
                onChange={(event) =>
                  edit((block) => ({
                    ...block,
                    rows: (block.rows ?? []).map((item, itemIndex) =>
                      itemIndex === index ? { ...item, label: event.target.value } : item,
                    ),
                  }))
                }
              />
              <input
                className="form-input w-24 text-sm"
                disabled={readOnly}
                placeholder="доля ВПИ"
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={String(row.at ?? "")}
                onChange={(event) =>
                  edit((block) => ({
                    ...block,
                    rows: (block.rows ?? []).map((item, itemIndex) =>
                      itemIndex === index ? { ...item, at: Number(event.target.value) } : item,
                    ),
                  }))
                }
              />
              <button
                className="btn-danger btn-sm"
                disabled={readOnly}
                type="button"
                onClick={() =>
                  edit((block) => ({
                    ...block,
                    rows: (block.rows ?? []).filter((_, itemIndex) => itemIndex !== index),
                  }))
                }
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
