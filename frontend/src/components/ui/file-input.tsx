import { type ChangeEventHandler, type InputHTMLAttributes } from "react"

type FileInputProps = Omit<
  InputHTMLAttributes<HTMLInputElement>,
  "className" | "onChange" | "type" | "value"
> & {
  /** The chosen file's name — the caller owns the file, the field only shows it. */
  fileName?: string | null
  /** What stands in for the name before anything is chosen. */
  placeholder?: string
  className?: string
  onChange: ChangeEventHandler<HTMLInputElement>
}

/**
 * The fleet file field: a paperclip button and the chosen file's name.
 *
 * A bare `<input type="file">` is drawn by the browser — the button lands wherever the
 * browser puts it (in a narrow grid cell it used to sink to the bottom of the field),
 * and it is the one control whose look we cannot reach. Here the input is hidden and a
 * label stands in for it, so the control is the fleet's own button.
 */
export function FileInput({
  fileName,
  placeholder = "Файл не выбран",
  className,
  onChange,
  ...rest
}: FileInputProps) {
  return (
    <label className={["flex min-w-0 items-center gap-2", className ?? ""].join(" ").trim()}>
      <input {...rest} className="sr-only" type="file" onChange={onChange} />
      <span className="btn-secondary btn-sm shrink-0">
        <svg aria-hidden="true" className="h-4 w-4" fill="none" viewBox="0 0 24 24">
          <path
            d="M16.5 6.75 8.4 14.85a2.25 2.25 0 1 0 3.18 3.18l8.1-8.1a4.5 4.5 0 0 0-6.36-6.36l-8.1 8.1a6.75 6.75 0 0 0 9.54 9.54l6.36-6.36"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.6"
          />
        </svg>
        Выбрать файл
      </span>
      <span className="min-w-0 truncate text-sm text-steel" title={fileName ?? undefined}>
        {fileName || placeholder}
      </span>
    </label>
  )
}
