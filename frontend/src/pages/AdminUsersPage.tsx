import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { useQuery, useQueryClient } from "@tanstack/react-query";

import { createUser, fetchUsers, type CreateUserPayload } from "@/api/users";
import { PageHeader } from "@/components/layout/PageHeader";
import { Modal } from "@/components/Modal";
import { roleLabels } from "@/lib/roles";
import { useAuthStore } from "@/store/auth";

export function AdminUsersPage() {
  const token = useAuthStore((state) => state.token);
  const queryClient = useQueryClient();
  const [createOpen, setCreateOpen] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [temporaryPassword, setTemporaryPassword] = useState<string | null>(null);
  const [form, setForm] = useState<CreateUserPayload>({
    firstName: "",
    lastName: "",
    patronymic: "",
    email: "",
    role: "CUSTOMER",
    isActive: true,
  });

  const usersQuery = useQuery({
    queryKey: ["users"],
    queryFn: () => fetchUsers(token ?? ""),
    enabled: Boolean(token),
  });

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    setCreateError(null);
    try {
      const response = await createUser(token, form);
      setTemporaryPassword(response.temporaryPassword);
      setCreateOpen(false);
      setForm({
        firstName: "",
        lastName: "",
        patronymic: "",
        email: "",
        role: "CUSTOMER",
        isActive: true,
      });
      await queryClient.invalidateQueries({ queryKey: ["users"] });
    } catch (error) {
      setCreateError(error instanceof Error ? error.message : "Не удалось создать пользователя.");
    }
  }

  return (
    <section>
      <PageHeader
        title="Пользователи"
        description="Административная панель пользователей в стиле metroLog, но без лишнего доменного шума. Отсюда можно создавать аккаунты и открывать карточки пользователей."
        action={
          <button className="btn-primary" type="button" onClick={() => setCreateOpen(true)}>
            Новый пользователь
          </button>
        }
      />

      {temporaryPassword ? (
        <div className="section-card mb-6">
          <div className="text-sm text-steel">Временный пароль последнего созданного/сброшенного пользователя</div>
          <div className="mt-2 text-2xl font-semibold text-ink">{temporaryPassword}</div>
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
        {usersQuery.data?.map((user) => (
          <article key={user.id} className="section-card">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-ink">{user.fullName || user.email}</h3>
                <p className="mt-1 text-sm text-steel">{user.email}</p>
              </div>
              <div className={["status-chip", user.isActive ? "status-chip--ok" : "status-chip--danger"].join(" ")}>
                {user.isActive ? "Активен" : "Отключен"}
              </div>
            </div>
            <div className="mt-4 text-sm text-steel">
              <div>Роль: <span className="text-ink">{roleLabels[user.role]}</span></div>
              <div className="mt-1">Последний вход: <span className="text-ink">{user.lastLoginAt ? new Date(user.lastLoginAt).toLocaleString("ru-RU") : "не было"}</span></div>
            </div>
            <div className="mt-5">
              <Link className="btn-secondary" to={`/admin/users/${user.id}`}>Открыть карточку</Link>
            </div>
          </article>
        ))}
      </div>

      <Modal
        description="Создание учетной записи metroGen с выдачей временного пароля."
        open={createOpen}
        size="sm"
        title="Новый пользователь"
        onClose={() => setCreateOpen(false)}
      >
        <form className="space-y-4" onSubmit={handleCreate}>
          <label className="block text-sm text-steel">
            Фамилия
            <input className="form-input" type="text" value={form.lastName} onChange={(event) => setForm((current) => ({ ...current, lastName: event.target.value }))} />
          </label>
          <label className="block text-sm text-steel">
            Имя
            <input className="form-input" type="text" value={form.firstName} onChange={(event) => setForm((current) => ({ ...current, firstName: event.target.value }))} />
          </label>
          <label className="block text-sm text-steel">
            Отчество
            <input className="form-input" type="text" value={form.patronymic ?? ""} onChange={(event) => setForm((current) => ({ ...current, patronymic: event.target.value }))} />
          </label>
          <label className="block text-sm text-steel">
            Email
            <input className="form-input" type="email" value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} />
          </label>
          <label className="block text-sm text-steel">
            Роль
            <select className="form-input" value={form.role} onChange={(event) => setForm((current) => ({ ...current, role: event.target.value as CreateUserPayload["role"] }))}>
              <option value="CUSTOMER">Заказчик</option>
              <option value="MKAIR">МКАИР</option>
              <option value="ADMINISTRATOR">Администратор</option>
              <option value="DEVELOPER">Разработчик</option>
            </select>
          </label>
          <label className="flex items-center gap-3 rounded-2xl border border-line px-4 py-3 text-sm">
            <input checked={form.isActive} type="checkbox" onChange={(event) => setForm((current) => ({ ...current, isActive: event.target.checked }))} />
            Активный пользователь
          </label>
          {createError ? <p className="text-sm text-[#b04c43]">{createError}</p> : null}
          <div className="flex justify-end gap-3">
            <button className="btn-secondary" type="button" onClick={() => setCreateOpen(false)}>Отмена</button>
            <button className="btn-primary" type="submit">Создать</button>
          </div>
        </form>
      </Modal>
    </section>
  );
}
