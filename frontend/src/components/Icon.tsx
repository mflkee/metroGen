export type IconName =
  | "home"
  | "verification"
  | "settings"
  | "users"
  | "help"
  | "monitor"
  | "details"
  | "delete";

type IconProps = {
  name: IconName;
  className?: string;
};

export function Icon({ name, className }: IconProps) {
  const baseClassName = className ?? "h-5 w-5";

  switch (name) {
    case "home":
      return (
        <svg className={baseClassName} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.9">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 10.5 12 3l9 7.5" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 9.75V21h13.5V9.75" />
        </svg>
      );
    case "verification":
      return (
        <svg className={baseClassName} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 3h6" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 3v5.25L5.25 18a2.25 2.25 0 0 0 1.98 3.3h9.54a2.25 2.25 0 0 0 1.98-3.3L13.5 8.25V3" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 13.5h4.5" />
        </svg>
      );
    case "settings":
      return (
        <svg className={baseClassName} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
          <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317a1.724 1.724 0 0 1 3.35 0 1.724 1.724 0 0 0 2.573 1.066 1.724 1.724 0 0 1 2.36 2.36 1.724 1.724 0 0 0 1.065 2.573 1.724 1.724 0 0 1 0 3.35 1.724 1.724 0 0 0-1.066 2.573 1.724 1.724 0 0 1-2.36 2.36 1.724 1.724 0 0 0-2.573 1.065 1.724 1.724 0 0 1-3.35 0 1.724 1.724 0 0 0-2.573-1.066 1.724 1.724 0 0 1-2.36-2.36 1.724 1.724 0 0 0-1.065-2.573 1.724 1.724 0 0 1 0-3.35 1.724 1.724 0 0 0 1.066-2.573 1.724 1.724 0 0 1 2.36-2.36 1.724 1.724 0 0 0 2.573-1.065Z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 15.75A3.75 3.75 0 1 0 12 8.25a3.75 3.75 0 0 0 0 7.5Z" />
        </svg>
      );
    case "users":
      return (
        <svg className={baseClassName} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 7.5a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5a7.5 7.5 0 0 1 15 0" />
        </svg>
      );
    case "help":
      return (
        <svg className={baseClassName} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.09 9a3 3 0 1 1 5.82 1c0 2-3 2-3 4" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 17.25h.008v.008H12z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg>
      );
    case "monitor":
      return (
        <svg className={baseClassName} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 5.25h16.5v10.5H3.75z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 18.75h6" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 15.75v3" />
        </svg>
      );
    case "details":
      return (
        <svg className={baseClassName} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
          <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12s3.75-6 9.75-6 9.75 6 9.75 6-3.75 6-9.75 6-9.75-6-9.75-6Z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 14.25A2.25 2.25 0 1 0 12 9.75a2.25 2.25 0 0 0 0 4.5Z" />
        </svg>
      );
    case "delete":
      return (
        <svg className={baseClassName} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.9">
          <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 7.5h10.5" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.75h4.5l.75 1.5H18" />
          <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 7.5.75 11.25h6l.75-11.25" />
        </svg>
      );
  }
}
