import type { UserRole } from "@/api/auth";
import { hasAdminAccess } from "@/lib/roles";

export type NavigationItem = {
  icon: string;
  label: string;
  description: string;
  to: string;
};

const baseNavigationItems: NavigationItem[] = [
  { icon: "home", label: "Главная", description: "Статус, экспорты и запуск сценариев", to: "/dashboard" },
  { icon: "verification", label: "Генерация", description: "PDF, HTML-превью и режимы протоколов", to: "/generation" },
  { icon: "arshin", label: "Аршин", description: "Диагностика сертификатов и vri_id", to: "/arshin" },
  { icon: "settings", label: "Настройки", description: "Темы, SMTP и параметры интерфейса", to: "/settings" },
];

const developerNavigationItem: NavigationItem = {
  icon: "monitor",
  label: "Мониторинг",
  description: "Состояние приложения и окружения",
  to: "/developer",
};

const adminUsersNavigationItem: NavigationItem = {
  icon: "users",
  label: "Пользователи",
  description: "Роли, доступы и временные пароли",
  to: "/admin/users",
};

export function getNavigationItems(role: UserRole | null | undefined): NavigationItem[] {
  const items = [...baseNavigationItems];
  if (hasAdminAccess(role)) {
    items.push(developerNavigationItem, adminUsersNavigationItem);
  }
  return items;
}
