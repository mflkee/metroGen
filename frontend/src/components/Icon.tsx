export type IconName =
  | "home"
  | "arshin"
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
    case "arshin":
      return (
        <svg className={baseClassName} viewBox="0 0 399 208" fill="currentColor">
          <path d="M23 23h22v155H23zm332 0h22v155h-22zm-266 111h23v44H89zm67 0h22v44h-22zm66 0h22v44h-22zm67 0h22v44h-22z" />
          <path
            fillRule="evenodd"
            d="M89 23h22v88H89zm22 0h12c18 0 33 15 33 33s-15 33-33 33h-12zm0 21h10c8 0 14 6 14 12s-6 12-14 12h-10z"
          />
          <path d="M235.92 40.08A37 37 0 1 0 235.92 92.92" fill="none" stroke="currentColor" strokeWidth="23" />
          <path d="M267 23h66v26h-22v62h-22V49h-22z" />
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
