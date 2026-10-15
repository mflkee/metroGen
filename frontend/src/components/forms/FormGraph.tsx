import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import ForceGraph from "force-graph";
import type { LinkObject, NodeObject } from "force-graph";

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

type GraphNode = NodeObject & FormGraphNode;
type GraphLink = LinkObject<GraphNode> & { type: "inherits" | "binds" };

type FormGraphProps = {
  nodes: FormGraphNode[];
  links: FormGraphLink[];
  /** Free-text search: matching nodes are highlighted, the rest is dimmed. */
  query?: string;
  selectedId?: string | null;
  onSelect?: (id: string) => void;
  height?: number;
};

type ThemeColors = {
  accent: string;
  muted: string;
  surface: string;
  text: string;
  danger: string;
};

/** Colours come from the theme tokens; canvas cannot use Tailwind classes. */
function readThemeColors(): ThemeColors {
  if (typeof document === "undefined") {
    return { accent: "steelblue", muted: "gray", surface: "white", text: "black", danger: "red" };
  }
  const style = getComputedStyle(document.documentElement);
  const read = (name: string, fallback: string) => style.getPropertyValue(name).trim() || fallback;
  return {
    accent: read("--accent", "steelblue"),
    muted: read("--text-muted", "gray"),
    surface: read("--tone-parent-bg", "white"),
    text: read("--text-primary", "black"),
    danger: read("--danger", "red"),
  };
}

/**
 * The dependency graph of the protocol forms, drawn by `force-graph` (Canvas + d3-force inside).
 *
 * Nodes are draggable, zoom happens at the pointer, the background pans, hover highlights a node with
 * its neighbours and clicking a form selects it. Filters are applied by the page (which nodes and
 * edges exist at all); search only highlights.
 */
export function FormGraph({
  nodes,
  links,
  query = "",
  selectedId = null,
  onSelect,
  height = 460,
}: FormGraphProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const graphRef = useRef<ForceGraph<GraphNode, GraphLink> | null>(null);
  const [themeTick, setThemeTick] = useState(0);

  // Read by the canvas callbacks, which are installed once.
  const queryRef = useRef(query);
  const selectedRef = useRef<string | null>(selectedId);
  const hoverRef = useRef<string | null>(null);
  const colors = useMemo(() => readThemeColors(), [themeTick]);

  queryRef.current = query;
  selectedRef.current = selectedId;

  const needle = query.trim().toLowerCase();
  const matches = useCallback(
    (node: FormGraphNode) =>
      needle.length > 0 &&
      (node.id.toLowerCase().includes(needle) ||
        node.label.toLowerCase().includes(needle) ||
        (node.subtitle ?? "").toLowerCase().includes(needle)),
    [needle],
  );

  const isDimmed = useCallback(
    (node: GraphNode) => {
      if (needle.length > 0) {
        return !matches(node);
      }
      const hovered = hoverRef.current;
      if (hovered) {
        return hovered !== node.id && !isNeighbour(hovered, node.id);
      }
      return false;
    },
    [matches, needle],
  );

  const neighbours = useMemo(() => {
    const map = new Map<string, Set<string>>();
    const add = (a: string, b: string) => {
      if (!map.has(a)) map.set(a, new Set());
      map.get(a)!.add(b);
    };
    for (const link of links) {
      add(link.source, link.target);
      add(link.target, link.source);
    }
    return map;
  }, [links]);

  function isNeighbour(a: string, b: string): boolean {
    return neighbours.get(a)?.has(b) ?? false;
  }

  // The graph instance is created once; data and appearance are updated below.
  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return undefined;
    }

    const createGraph = ForceGraph as unknown as (
      element: HTMLElement,
    ) => ForceGraph<GraphNode, GraphLink>;

    const graph = createGraph(container)
      .backgroundColor("transparent")
      .nodeId("id")
      .nodeRelSize(0)
      .nodeCanvasObjectMode(() => "replace")
      .nodeCanvasObject((node, ctx, scale) => {
        const dimmed = isDimmed(node);
        ctx.globalAlpha = dimmed ? 0.2 : 1;

        const radius = node.type === "form" ? (node.isBase ? 7 : 5.5) : 3.5;
        ctx.beginPath();
        if (node.type === "form") {
          ctx.arc(node.x ?? 0, node.y ?? 0, radius, 0, 2 * Math.PI);
        } else {
          ctx.rect((node.x ?? 0) - radius, (node.y ?? 0) - radius, radius * 2, radius * 2);
        }

        ctx.fillStyle =
          node.type === "condition"
            ? colors.muted
            : node.isBase
              ? colors.accent
              : colors.surface;
        ctx.fill();

        const isSelected = selectedRef.current === node.id;
        const isHovered = hoverRef.current === node.id;
        ctx.strokeStyle = isSelected ? colors.danger : matches(node) ? colors.danger : colors.accent;
        ctx.lineWidth = (isSelected || isHovered ? 2.4 : 1.1) / scale;
        if (node.type === "form" && node.renderer === "html") {
          ctx.setLineDash([3 / scale, 2 / scale]);
        }
        ctx.stroke();
        ctx.setLineDash([]);

        const fontSize = Math.max(10 / scale, 2.6);
        ctx.font = `${fontSize}px sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillStyle = node.type === "form" ? colors.text : colors.muted;
        ctx.fillText(node.label, node.x ?? 0, (node.y ?? 0) + radius + 2 / scale);
        ctx.globalAlpha = 1;
      })
      .nodePointerAreaPaint((node, color, ctx) => {
        const radius = node.type === "form" ? 11 : 6;
        ctx.fillStyle = color;
        ctx.beginPath();
        if (node.type === "form") {
          ctx.arc(node.x ?? 0, node.y ?? 0, radius, 0, 2 * Math.PI);
        } else {
          ctx.rect((node.x ?? 0) - radius, (node.y ?? 0) - radius, radius * 2, radius * 2);
        }
        ctx.fill();
      })
      .linkColor((link) => (link.type === "inherits" ? colors.accent : colors.muted))
      .linkWidth((link) => (link.type === "inherits" ? 1.4 : 0.7))
      .linkLineDash((link) => (link.type === "binds" ? [4, 3] : null))
      .linkDirectionalParticles(0)
      .onNodeHover((node) => {
        hoverRef.current = node ? String(node.id) : null;
        if (container) {
          container.style.cursor = node ? "pointer" : "grab";
        }
      })
      .onNodeClick((node) => {
        const id = String(node.id);
        if (!id.startsWith("rule-")) {
          onSelect?.(id);
        }
      })
      .onBackgroundClick(() => onSelect?.(""))
      .warmupTicks(40)
      .cooldownTicks(220)
      .d3AlphaDecay(0.04);

    graph.width(container.clientWidth || 800).height(height);
    graphRef.current = graph;

    const observer = new ResizeObserver(() => {
      if (containerRef.current) {
        graph.width(containerRef.current.clientWidth || 800);
      }
    });
    observer.observe(container);

    return () => {
      observer.disconnect();
      graphRef.current = null;
      // force-graph has no public destructor; dropping the canvas is enough.
      container.replaceChildren();
    };
  }, [colors, height, isDimmed, matches, onSelect]);

  // Data: a fresh copy, so the simulation owns its own node objects.
  useEffect(() => {
    const graph = graphRef.current;
    if (!graph) {
      return;
    }
    graph.graphData({
      nodes: nodes.map((node) => ({ ...node })),
      links: links.map((link) => ({ source: link.source, target: link.target, type: link.type })),
    });
  }, [nodes, links]);

  // Search and selection repaint the canvas (the accessors read the refs).
  useEffect(() => {
    const graph = graphRef.current;
    if (!graph) {
      return;
    }
    graph.nodeCanvasObject(graph.nodeCanvasObject());

    if (!needle) {
      return;
    }
    const first = graph.graphData().nodes.find((node) => matches(node));
    if (first && typeof first.x === "number" && typeof first.y === "number") {
      graph.centerAt(first.x, first.y, 400);
      graph.zoom(2.2, 400);
    }
  }, [needle, selectedId, matches]);

  // Follow the theme: `data-theme` changes the CSS variables the canvas reads.
  useEffect(() => {
    if (typeof document === "undefined") {
      return undefined;
    }
    const observer = new MutationObserver(() => setThemeTick((tick) => tick + 1));
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => observer.disconnect();
  }, []);

  function relayout() {
    const graph = graphRef.current;
    if (!graph) {
      return;
    }
    for (const node of graph.graphData().nodes) {
      node.fx = undefined;
      node.fy = undefined;
    }
    graph.d3ReheatSimulation();
    graph.zoomToFit(400, 60);
  }

  return (
    <div className="relative">
      <div className="absolute right-3 top-3 z-10 flex gap-2">
        <button className="btn-secondary btn-sm" type="button" onClick={relayout}>
          Пересобрать
        </button>
      </div>

      <div
        className="w-full overflow-hidden rounded-2xl border border-line"
        ref={containerRef}
        style={{ height, background: "var(--tone-child-bg)" }}
      />

      <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-steel">
        <span className="inline-flex items-center gap-1">
          <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: "var(--accent)" }} />
          форма (базовая)
        </span>
        <span className="inline-flex items-center gap-1">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full border"
            style={{ borderColor: "var(--accent)" }}
          />
          форма (производная)
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="inline-block h-2 w-2" style={{ background: "var(--text-muted)" }} />
          условие правила
        </span>
        <span>
          <span style={{ color: "var(--accent)" }}>——</span> наследование
        </span>
        <span>
          <span style={{ color: "var(--text-muted)" }}>- - -</span> правило выбирает форму
        </span>
        <span>пунктирная обводка — форма ещё из HTML-шаблона</span>
        <span>перетаскивание — узлы, колесо — масштаб, фон — сдвиг</span>
      </div>
    </div>
  );
}
