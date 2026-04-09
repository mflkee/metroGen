import { useId, useState, type InputHTMLAttributes } from "react";

type PasswordInputProps = Omit<InputHTMLAttributes<HTMLInputElement>, "type"> & {
  label: string;
};

export function PasswordInput({ className, id, label, ...props }: PasswordInputProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;
  const [isVisible, setIsVisible] = useState(false);

  return (
    <label className="block text-sm text-steel" htmlFor={inputId}>
      {label}
      <div className="relative mt-2">
        <input
          {...props}
          id={inputId}
          className={["form-input pr-28", className ?? ""].join(" ").trim()}
          type={isVisible ? "text" : "password"}
        />
        <button
          aria-label={isVisible ? "Скрыть пароль" : "Показать пароль"}
          className="absolute right-3 top-1/2 inline-flex -translate-y-1/2 items-center gap-2 rounded-full border border-line px-3 py-1 text-xs font-medium text-steel transition hover:border-signal-info hover:text-ink"
          type="button"
          onClick={() => setIsVisible((value) => !value)}
        >
          <span>{isVisible ? "Скрыть" : "Показать"}</span>
        </button>
      </div>
    </label>
  );
}
