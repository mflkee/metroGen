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
  {
    icon: "verification",
    label: "Генерация",
    description: "PDF, БД, готовые run-пакеты и превью",
    to: "/generation",
  },
  { icon: "settings", label: "Настройки", description: "Темы, SMTP и параметры интерфейса", to: "/settings" },
];

const developerNavigationItem: NavigationItem = {
  icon: "monitor",
  label: "Мониторинг",
  description: "Состояние сервиса, БД и активность пользователей",
  to: "/developer",
};

const adminUsersNavigationItem: NavigationItem = {
  icon: "users",
  label: "Пользователи",
  description: "Роли, временные пароли и быстрые действия",
  to: "/admin/users",
};

const adminOwnersNavigationItem: NavigationItem = {
  icon: "details",
  label: "Владельцы",
  description: "Справочник организаций-владельцев СИ",
  to: "/admin/owners",
};

const adminMethodologiesNavigationItem: NavigationItem = {
  icon: "verification",
  label: "Методики",
  description: "Справочник методик поверки СИ",
  to: "/admin/methodologies",
};

const adminAuxInstrumentsNavigationItem: NavigationItem = {
  icon: "settings",
  label: "Вспом. СИ",
  description: "Вспомогательные средства измерений",
  to: "/admin/aux-instruments",
};

export function getNavigationItems(role: UserRole | null | undefined): NavigationItem[] {
  const items = [...baseNavigationItems];
  if (hasAdminAccess(role)) {
    items.push(
      developerNavigationItem,
      adminUsersNavigationItem,
      adminOwnersNavigationItem,
      adminMethodologiesNavigationItem,
      adminAuxInstrumentsNavigationItem,
    );
  }
  return items;
}
