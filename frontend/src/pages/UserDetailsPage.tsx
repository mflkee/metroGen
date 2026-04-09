import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { useQuery, useQueryClient } from "@tanstack/react-query";

import { deleteUser, fetchUserById, resetUserPassword, updateUser } from "@/api/users";
import { PageHeader } from "@/components/layout/PageHeader";
import { roleLabels } from "@/lib/roles";
import { useAuthStore } from "@/store/auth";

export function UserDetailsPage() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const token = useAuthStore((state) => state.token);
  const parsedUserId = Number(userId);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [patronymic, setPatronymic] = useState("");
  const [role, setRole] = useState<"DEVELOPER" | "ADMINISTRATOR" | "MKAIR" | "CUSTOMER">("CUSTOMER");
  const [isActive, setIsActive] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [temporaryPassword, setTemporaryPassword] = useState<string | null>(null);

  const userQuery = useQuery({
    queryKey: ["users", parsedUserId],
    queryFn: () => fetchUserById(token ?? "", parsedUserId),
    enabled: Boolean(token) && Number.isInteger(parsedUserId) && parsedUserId > 0,
  });

  useEffect(() => {
    if (!userQuery.data) {
      return;
    }
    setFirstName(userQuery.data.firstName);
    setLastName(userQuery.data.lastName);
    setPatronymic(userQuery.data.patronymic ?? "");
    setRole(userQuery.data.role);
    setIsActive(userQuery.data.isActive);
  }, [userQuery.data]);

  async function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }
    setError(null);
    setMessage(null);
    try {
      await updateUser(token, parsedUserId, {
        firstName,
        lastName,
        patronymic,
        role,
        isActive,
      });
      await queryClient.invalidateQueries({ queryKey: ["users"] });
      await queryClient.invalidateQueries({ queryKey: ["users", parsedUserId] });
      setMessage("Изменения сохранены.");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Не удалось сохранить пользователя.");
    }
  }

  async function handleResetPassword() {
    if (!token) {
      return;
    }
    setError(null);
    setMessage(null);
    try {
      const response = await resetUserPassword(token, parsedUserId);
      setTemporaryPassword(response.temporaryPassword);
      setMessage("Временный пароль обновлен.");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Не удалось сбросить пароль.");
    }
  }

  async function handleDelete() {
    if (!token) {
      return;
    }
    setError(null);
    try {
      await deleteUser(token, parsedUserId);
      await queryClient.invalidateQueries({ queryKey: ["users"] });
      navigate("/admin/users");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Не удалось удалить пользователя.");
    }
  }

  const user = userQuery.data;

  return (
    <section>
      <PageHeader
        title="Карточка пользователя"
        description="Редактирование роли, статуса и реквизитов учетной записи."
        action={<Link className="btn-secondary" to="/admin/users">Назад к списку</Link>}
      />

      {temporaryPassword ? (
        <div className="section-card mb-6">
          <div className="text-sm text-steel">Новый временный пароль</div>
          <div className="mt-2 text-2xl font-semibold text-ink">{temporaryPassword}</div>
        </div>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
        <form className="section-card space-y-4" onSubmit={handleSave}>
          <h3 className="text-lg font-semibold text-ink">{user?.fullName ?? "Пользователь"}</h3>
          <label className="block text-sm text-steel">
            Фамилия
            <input className="form-input" type="text" value={lastName} onChange={(event) => setLastName(event.target.value)} />
          </label>
          <label className="block text-sm text-steel">
            Имя
            <input className="form-input" type="text" value={firstName} onChange={(event) => setFirstName(event.target.value)} />
          </label>
          <label className="block text-sm text-steel">
            Отчество
            <input className="form-input" type="text" value={patronymic} onChange={(event) => setPatronymic(event.target.value)} />
          </label>
          <label className="block text-sm text-steel">
            Роль
            <select className="form-input" value={role} onChange={(event) => setRole(event.target.value as typeof role)}>
              <option value="CUSTOMER">Заказчик</option>
              <option value="MKAIR">МКАИР</option>
              <option value="ADMINISTRATOR">Администратор</option>
              <option value="DEVELOPER">Разработчик</option>
            </select>
          </label>
          <label className="flex items-center gap-3 rounded-2xl border border-line px-4 py-3 text-sm text-ink">
            <input checked={isActive} type="checkbox" onChange={(event) => setIsActive(event.target.checked)} />
            Активная учетная запись
          </label>

          {message ? <p className="text-sm text-signal-ok">{message}</p> : null}
          {error ? <p className="text-sm text-[#b04c43]">{error}</p> : null}

          <div className="flex flex-wrap gap-3">
            <button className="btn-primary" type="submit">Сохранить</button>
            <button className="btn-secondary" type="button" onClick={() => void handleResetPassword()}>
              Сбросить пароль
            </button>
            <button className="btn-danger" type="button" onClick={() => void handleDelete()}>
              Удалить пользователя
            </button>
          </div>
        </form>

        <aside className="section-card">
          <h3 className="text-lg font-semibold text-ink">Сводка</h3>
          <div className="mt-4 space-y-3 text-sm">
            <div>
              <div className="text-xs uppercase tracking-[0.16em] text-steel">Email</div>
              <div className="mt-1 text-ink">{user?.email ?? "..."}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-[0.16em] text-steel">Роль</div>
              <div className="mt-1 text-ink">{user ? roleLabels[user.role] : "..."}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-[0.16em] text-steel">Последний вход</div>
              <div className="mt-1 text-ink">{user?.lastLoginAt ? new Date(user.lastLoginAt).toLocaleString("ru-RU") : "не было"}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-[0.16em] text-steel">Создан</div>
              <div className="mt-1 text-ink">{user?.createdAt ? new Date(user.createdAt).toLocaleString("ru-RU") : "..."}</div>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
