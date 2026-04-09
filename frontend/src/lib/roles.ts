import type { UserRole } from "@/api/auth";

export const roleLabels: Record<UserRole, string> = {
  DEVELOPER: "Разработчик",
  ADMINISTRATOR: "Администратор",
  MKAIR: "МКАИР",
  CUSTOMER: "Заказчик",
};

export function hasAdminAccess(role: UserRole | null | undefined): boolean {
  return role === "DEVELOPER" || role === "ADMINISTRATOR";
}
