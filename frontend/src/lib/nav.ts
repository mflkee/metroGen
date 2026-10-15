import type { UserRole } from "@/api/auth";
import { hasAdminAccess } from "@/lib/roles";

export type NavigationItem = {
  icon: string;
  label: string;
  description: string;
  to: string;
};

/** The everyday screens: always visible. */
const baseNavigationItems: NavigationItem[] = [
  { icon: "home", label: "Главная", description: "Статус, экспорты и запуск сценариев", to: "/dashboard" },
  {
    icon: "verification",
    label: "Генерация",
    description: "PDF, БД, готовые run-пакеты и превью",
    to: "/generation",
  },
];

/** The reference books: administrators only, but part of the main list. */
const referenceNavigationItems: NavigationItem[] = [
  {
    icon: "details",
    label: "Владельцы",
    description: "Справочник организаций-владельцев СИ",
    to: "/admin/owners",
  },
  {
    icon: "verification",
    label: "Методики",
    description: "Справочник методик поверки СИ",
    to: "/admin/methodologies",
  },
  {
    icon: "aux",
    label: "Вспом. СИ",
    description: "Вспомогательные средства измерений",
    to: "/admin/aux-instruments",
  },
  {
    icon: "etalon",
    label: "Эталоны",
    description: "Справочник эталонов (ФИФ) с обновлением из Аршина",
    to: "/admin/etalons",
  },
  {
    icon: "form",
    label: "Формы протоколов",
    description: "Каталог форм, наследование и граф зависимостей",
    to: "/admin/templates",
  },
];

/** Pinned to the bottom of the sidebar (with «Документация», added by the shell). */
const adminBottomItems: NavigationItem[] = [
  {
    icon: "monitor",
    label: "Мониторинг",
    description: "Состояние сервиса, БД и активность пользователей",
    to: "/developer",
  },
  {
    icon: "users",
    label: "Пользователи",
    description: "Роли, временные пароли и быстрые действия",
    to: "/admin/users",
  },
];

const settingsNavigationItem: NavigationItem = {
  icon: "settings",
  label: "Настройки",
  description: "Темы, SMTP и параметры интерфейса",
  to: "/settings",
};

/** The main sidebar list. */
export function getNavigationItems(role: UserRole | null | undefined): NavigationItem[] {
  const items = [...baseNavigationItems];
  if (hasAdminAccess(role)) {
    items.push(...referenceNavigationItems);
  }
  return items;
}

/** The block pinned to the bottom: administration and the user's own settings. */
export function getBottomNavigationItems(role: UserRole | null | undefined): NavigationItem[] {
  const items: NavigationItem[] = [];
  if (hasAdminAccess(role)) {
    items.push(...adminBottomItems);
  }
  items.push(settingsNavigationItem);
  return items;
}
