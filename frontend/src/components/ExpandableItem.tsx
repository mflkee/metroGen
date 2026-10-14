import { type ReactNode, useState } from "react";

type ExpandableItemProps = {
  /** The always-visible summary of the entry (toggled by the whole header). */
  header: ReactNode;
  /** Row-level controls that must not toggle the item (Изменить, Удалить, …). */
  actions?: ReactNode;
  /** The details revealed when the item is open. */
  children: ReactNode;
  defaultOpen?: boolean;
  /** Called when the item is expanded or collapsed (e.g. to lazily load details). */
  onToggle?: (open: boolean) => void;
};

/**
 * A list entry that reveals its details in place — the metroLog accordion pattern
 * (`aria-expanded` on the header button, a chevron that rotates, the body rendered only when open).
 *
 * The header button is the toggle; `actions` sit next to it as ordinary buttons, so a click on
 * «Изменить» never collapses the row.
 */
export function ExpandableItem({
  header,
  actions,
  children,
  defaultOpen = false,
  onToggle,
}: ExpandableItemProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <article className="tone-child overflow-hidden rounded-2xl border border-line">
      <div className="flex items-start justify-between gap-3 px-4 py-3">
        <button
          aria-expanded={isOpen}
          className="flex min-w-0 flex-1 items-start gap-3 text-left"
          type="button"
          onClick={() => {
            const next = !isOpen;
            setIsOpen(next);
            onToggle?.(next);
          }}
        >
          <svg
            aria-hidden="true"
            className={[
              "mt-1 h-5 w-5 shrink-0 text-steel transition-transform",
              isOpen ? "rotate-180" : "",
            ].join(" ")}
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 9-7.5 7.5L4.5 9" />
          </svg>
          <div className="min-w-0 flex-1">{header}</div>
        </button>
        {actions ? <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div> : null}
      </div>
      {isOpen ? <div className="space-y-3 border-t border-line px-4 py-3">{children}</div> : null}
    </article>
  );
}
