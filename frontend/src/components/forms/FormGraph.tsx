import { useMemo, useRef, useState } from "react";

import { forceCenter, forceCollide, forceLink, forceManyBody, forceSimulation } from "d3-force";

export type FormGraphNode = {
  id: string;
  label: string;
  /** `form` — a protocol form; `condition` — a rule condition (methodology / type / modification). */
  type: "form" | "condition";
  /** Base forms are drawn filled; derived ones are outlined. */
  isBase?: boolean;
  /** `html` forms are not editable yet (shown with a dashed ring). */
  renderer?: string;
  subtitle?: string;
};

export type FormGraphLink = {
  source: string;
  target: string;
  /** `inherits` — parent form → derived form; `binds` — condition → form. */
  type: "inherits" | "binds";
};

type FormGraphProps = {
  nodes: FormGraphNode[];
  links: FormGraphLink[];
  /** Free-text search: matching nodes are highlighted, the rest is dimmed. */
  query?: string;
  selectedId?: string | null;
  onSelect?: (id: string) => void;
  height?: number;
};

type SimNode = FormGraphNode & { x: number; y: number };
type SimLink = { source: string | SimNode; target: string | SimNode; type: "inherits" | "binds" };

/**
 * The dependency graph of the protocol forms — an Obsidian-style force layout drawn as plain SVG.
 *
 * The layout is computed once per node/edge set (the simulation is run to completion, not animated),
 * so the picture is stable and cheap: a re-layout button re-runs it. Wheel zooms, dragging the
 * background pans, clicking a node selects it.
 */
export function FormGraph({
  nodes,
  links,
  query = "",
  selectedId = null,
  onSelect,
  height = 460,
}: FormGraphProps) {
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [seed, setSeed] = useState(0);
  const dragRef = useRef<{ x: number; y: number } | null>(null);

  const { simNodes, simLinks, viewBox } = useMemo(() => {
    const plainNodes: SimNode[] = nodes.map((node) => ({ ...node, x: 0, y: 0 }));
    const byId = new Map(plainNodes.map((node) => [node.id, node]));
    const plainLinks: SimLink[] = links
      .filter((link) => byId.has(link.source) && byId.has(link.target))
      .map((link) => ({ source: link.source, target: link.target, type: link.type }));

    if (plainNodes.length) {
      const simulation = forceSimulation<SimNode>(plainNodes)
        .force(
          "link",
          forceLink<SimNode, SimLink>(plainLinks)
            .id((node) => node.id)
            .distance((link) => (link.type === "inherits" ? 96 : 148))
            .strength(0.8),
        )
        .force("charge", forceManyBody<SimNode>().strength(-340))
        .force("center", forceCenter(0, 0))
        .force("collide", forceCollide<SimNode>(38));
      simulation.stop();
      for (let tick = 0; tick < 320; tick += 1) {
        simulation.tick();
      }
    }

    const xs = plainNodes.map((node) => node.x);
    const ys = plainNodes.map((node) => node.y);
    const pad = 90;
    const minX = xs.length ? Math.min(...xs) - pad : -pad;
    const maxX = xs.length ? Math.max(...xs) + pad : pad;
    const minY = ys.length ? Math.min(...ys) - pad : -pad;
    const maxY = ys.length ? Math.max(...ys) + pad : pad;

    return {
      simNodes: plainNodes,
      simLinks: plainLinks.map((link) => ({
        source: link.source as SimNode,
        target: link.target as SimNode,
        type: link.type,
      })),
      viewBox: `${minX} ${minY} ${Math.max(maxX - minX, 1)} ${Math.max(maxY - minY, 1)}`,
    };
  }, [nodes, links, seed]);

  const needle = query.trim().toLowerCase();
  const matches = (node: FormGraphNode) =>
    needle.length > 0 &&
    (node.id.toLowerCase().includes(needle) ||
      node.label.toLowerCase().includes(needle) ||
      (node.subtitle ?? "").toLowerCase().includes(needle));

  const anyMatch = needle.length > 0 && simNodes.some(matches);

  return (
    <div className="relative">
      <div className="absolute right-3 top-3 z-10 flex gap-2">
        <button
          className="btn-secondary btn-sm"
          type="button"
          onClick={() => {
            setScale(1);
            setOffset({ x: 0, y: 0 });
            setSeed((value) => value + 1);
          }}
        >
          Пересобрать
        </button>
      </div>

      <svg
        className="w-full rounded-2xl border border-line"
        height={height}
        style={{ background: "var(--tone-child-bg)", cursor: dragRef.current ? "grabbing" : "grab" }}
        viewBox={viewBox}
        onWheel={(event) => {
          event.preventDefault();
          setScale((current) => Math.min(3, Math.max(0.4, current - event.deltaY * 0.0012)));
        }}
        onPointerDown={(event) => {
          dragRef.current = { x: event.clientX, y: event.clientY };
        }}
        onPointerMove={(event) => {
          if (!dragRef.current) return;
          const dx = event.clientX - dragRef.current.x;
          const dy = event.clientY - dragRef.current.y;
          dragRef.current = { x: event.clientX, y: event.clientY };
          setOffset((current) => ({ x: current.x + dx, y: current.y + dy }));
        }}
        onPointerUp={() => {
          dragRef.current = null;
        }}
        onPointerLeave={() => {
          dragRef.current = null;
        }}
      >
        <g transform={`translate(${offset.x} ${offset.y}) scale(${scale})`}>
          {simLinks.map((link, index) => {
            const isInherits = link.type === "inherits";
            const dimmed = anyMatch && !(matches(link.source) || matches(link.target));
            return (
              <line
                key={`${link.source.id}-${link.target.id}-${index}`}
                opacity={dimmed ? 0.15 : isInherits ? 0.9 : 0.5}
                stroke={isInherits ? "var(--accent)" : "var(--text-muted)"}
                strokeDasharray={isInherits ? undefined : "4 4"}
                strokeWidth={isInherits ? 2 : 1}
                x1={link.source.x}
                x2={link.target.x}
                y1={link.source.y}
                y2={link.target.y}
              />
            );
          })}

          {simNodes.map((node) => {
            const isForm = node.type === "form";
            const highlighted = matches(node);
            const isSelected = selectedId === node.id;
            const dimmed = (anyMatch && !highlighted) || (selectedId !== null && !isSelected);
            const radius = isForm ? (node.isBase ? 20 : 15) : 7;
            const fill = !isForm
              ? "var(--text-muted)"
              : node.isBase
                ? "var(--accent)"
                : "var(--tone-parent-bg)";
            const stroke = isSelected
              ? "var(--success)"
              : highlighted
                ? "var(--danger)"
                : isForm
                  ? "var(--accent)"
                  : "var(--text-muted)";

            return (
              <g
                key={node.id}
                opacity={dimmed ? 0.25 : 1}
                style={{ cursor: onSelect ? "pointer" : "default" }}
                onClick={(event) => {
                  event.stopPropagation();
                  onSelect?.(node.id);
                }}
              >
                {isForm ? (
                  <circle
                    cx={node.x}
                    cy={node.y}
                    fill={fill}
                    r={radius}
                    stroke={stroke}
                    strokeDasharray={node.renderer === "html" ? "3 3" : undefined}
                    strokeWidth={isSelected ? 3 : 2}
                  />
                ) : (
                  <rect
                    fill={fill}
                    height={radius * 2}
                    stroke={stroke}
                    strokeWidth={1.5}
                    width={radius * 2}
                    x={node.x - radius}
                    y={node.y - radius}
                  />
                )}
                <text
                  className={isForm ? "fill-[var(--text-primary)]" : "fill-[var(--text-muted)]"}
                  fontSize={isForm ? 11 : 9}
                  textAnchor="middle"
                  x={node.x}
                  y={node.y + radius + 12}
                >
                  {node.label}
                </text>
              </g>
            );
          })}
        </g>
      </svg>

      <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-steel">
        <span className="inline-flex items-center gap-1">
          <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: "var(--accent)" }} />
          базовая форма
        </span>
        <span className="inline-flex items-center gap-1">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full border"
            style={{ borderColor: "var(--accent)" }}
          />
          производная форма
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="inline-block h-2 w-2" style={{ background: "var(--text-muted)" }} />
          условие (методика / тип / модификация)
        </span>
        <span>пунктирная окружность — форма ещё HTML-шаблон</span>
        <span>клик — выбрать, колесо — масштаб, перетаскивание — сдвиг</span>
      </div>
    </div>
  );
}
