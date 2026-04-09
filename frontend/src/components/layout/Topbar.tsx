import { Link, useLocation } from "react-router-dom";

import { AccountMenu } from "@/components/layout/AccountMenu";
import { useAuthStore } from "@/store/auth";

const routeLabels: Array<{ match: RegExp; label: string }> = [
  { match: /^\/dashboard$/, label: "Главная" },
  { match: /^\/generation$/, label: "Генерация" },
  { match: /^\/arshin$/, label: "Аршин" },
  { match: /^\/settings$/, label: "Настройки" },
  { match: /^\/profile$/, label: "Профиль" },
  { match: /^\/help$/, label: "Документация" },
  { match: /^\/developer$/, label: "Мониторинг" },
  { match: /^\/admin\/users$/, label: "Пользователи" },
  { match: /^\/admin\/users\/\d+$/, label: "Карточка пользователя" },
];

type TopbarProps = {
  mobileNavigationOpen: boolean;
  onToggleMobileNavigation: () => void;
};

export function Topbar({ mobileNavigationOpen, onToggleMobileNavigation }: TopbarProps) {
  const location = useLocation();
  const mustChangePassword = useAuthStore((state) => state.user?.mustChangePassword);
  const currentSection =
    routeLabels.find((item) => item.match.test(location.pathname))?.label ?? "Рабочая область";

  return (
    <header className="shell-topbar z-20 border-b border-line px-3 py-2 backdrop-blur sm:px-4 sm:py-2.5 lg:sticky lg:top-0 lg:px-8 lg:py-3">
      <div className="grid min-w-0 grid-cols-[minmax(0,1fr)_auto] items-center gap-x-2 sm:gap-x-3">
        <div className="flex min-w-0 items-center gap-2 sm:gap-3">
          <button
            aria-expanded={mobileNavigationOpen}
            aria-label={mobileNavigationOpen ? "Закрыть навигацию" : "Открыть навигацию"}
            className="mobile-nav-toggle lg:hidden"
            type="button"
            onClick={onToggleMobileNavigation}
          >
            {mobileNavigationOpen ? (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 7h16M4 12h16M4 17h16" />
              </svg>
            )}
          </button>
          <div className="hidden min-w-0 truncate text-[11px] uppercase tracking-[0.18em] text-steel sm:block sm:text-xs sm:tracking-[0.22em]">
            {currentSection}
          </div>
          <Link className="shrink-0 text-sm font-semibold text-ink sm:text-base" to="/dashboard">
            metroGen
          </Link>
        </div>
        <div className="justify-self-end">
          <AccountMenu />
        </div>
      </div>
      {mustChangePassword ? (
        <div className="shell-status-banner mt-2 rounded-2xl border border-signal-info px-4 py-2.5 text-sm text-ink">
          Временный пароль еще активен. Продолжение работы доступно только после смены пароля в профиле.
        </div>
      ) : null}
    </header>
  );
}
