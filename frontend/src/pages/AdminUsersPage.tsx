import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { UserRole } from "@/api/auth";
import {
  createUser,
  deleteUser,
  fetchUsers,
  resetUserPassword,
  updateUser,
  type CreateUserPayload,
} from "@/api/users";
import { DeleteConfirmModal } from "@/components/DeleteConfirmModal";
import { PageHeader } from "@/components/layout/PageHeader";
import { isDeveloperRole, roleLabels } from "@/lib/roles";
import { buildUserExtraInfo, matchesUserSearch, userSearchPlaceholder } from "@/lib/userSearch";
import { useAuthStore } from "@/store/auth";

const roleOrder: UserRole[] = ["DEVELOPER", "ADMINISTRATOR", "MKAIR", "CUSTOMER"];
const defaultRole: UserRole = "CUSTOMER";

type CredentialPacket = {
  fullName: string;
  email: string;
  temporaryPassword: string;
  reason: "create" | "reset";
};

export function AdminUsersPage() {
  const token = useAuthStore((state) => state.token);
  const currentUser = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();
  const [form, setForm] = useState<CreateUserPayload>({
    firstName: "",
    lastName: "",
    patronymic: "",
    email: "",
    role: defaultRole,
    isActive: true,
  });
  const [credentialPacket, setCredentialPacket] = useState<CredentialPacket | null>(null);
  const [copyMessage, setCopyMessage] = useState<string | null>(null);
  const [expandedUserId, setExpandedUserId] = useState<number | null>(null);
  const [draftRole, setDraftRole] = useState<UserRole>(defaultRole);
  const [draftIsActive, setDraftIsActive] = useState(true);
  const [usersSearchQuery, setUsersSearchQuery] = useState("");
  const [deleteUserId, setDeleteUserId] = useState<number | null>(null);
  const [deleteMessage, setDeleteMessage] = useState<string | null>(null);
  const canAssignDeveloperRole = isDeveloperRole(currentUser?.role);

  const assignableRoles = useMemo(
    () => (canAssignDeveloperRole ? roleOrder : roleOrder.filter((role) => role !== "DEVELOPER")),
    [canAssignDeveloperRole],
  );

  const usersQuery = useQuery({
    queryKey: ["admin-users"],
    queryFn: () => fetchUsers(token ?? ""),
    enabled: Boolean(token),
  });

  const createUserMutation = useMutation({
    mutationFn: (payload: CreateUserPayload) => createUser(token ?? "", payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-users"] });
    },
  });

  const updateUserMutation = useMutation({
    mutationFn: ({
      userId,
      payload,
    }: {
      userId: number;
      payload: { role?: UserRole; isActive?: boolean };
    }) => updateUser(token ?? "", userId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-users"] });
    },
  });

  const resetPasswordMutation = useMutation({
    mutationFn: ({
      userId,
      fullName,
      email,
    }: {
      userId: number;
      fullName: string;
      email: string;
    }) => resetUserPassword(token ?? "", userId).then((response) => ({ response, fullName, email })),
    onSuccess: ({ response, fullName, email }) => {
      setCredentialPacket({
        fullName,
        email,
        temporaryPassword: response.temporaryPassword,
        reason: "reset",
      });
      void queryClient.invalidateQueries({ queryKey: ["admin-users"] });
    },
  });

  const deleteUserMutation = useMutation({
    mutationFn: (userId: number) => deleteUser(token ?? "", userId),
    onSuccess: () => {
      setDeleteMessage("Пользователь удален.");
      setDeleteUserId(null);
      void queryClient.invalidateQueries({ queryKey: ["admin-users"] });
    },
  });

  const sortedUsers = useMemo(
    () =>
      usersQuery.data
        ? [...usersQuery.data].sort((left, right) => left.fullName.localeCompare(right.fullName))
        : [],
    [usersQuery.data],
  );
  const visibleUsers = useMemo(
    () => sortedUsers.filter((user) => matchesUserSearch(user, usersSearchQuery)),
    [sortedUsers, usersSearchQuery],
  );
  const expandedUser = useMemo(
    () => visibleUsers.find((user) => user.id === expandedUserId) ?? sortedUsers.find((user) => user.id === expandedUserId) ?? null,
    [expandedUserId, sortedUsers, visibleUsers],
  );
  const selectedDeleteUser = useMemo(
    () => sortedUsers.find((user) => user.id === deleteUserId) ?? null,
    [deleteUserId, sortedUsers],
  );

  useEffect(() => {
    if (!expandedUser) {
      return;
    }
    setDraftRole(expandedUser.role);
    setDraftIsActive(expandedUser.isActive);
  }, [expandedUser]);

  useEffect(() => {
    if (!canAssignDeveloperRole && form.role === "DEVELOPER") {
      setForm((current) => ({ ...current, role: defaultRole }));
    }
  }, [canAssignDeveloperRole, form.role]);

  async function handleCreateUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setCredentialPacket(null);
    setCopyMessage(null);
    setDeleteMessage(null);

    try {
      const response = await createUserMutation.mutateAsync(form);
      setCredentialPacket({
        fullName: response.user.fullName,
        email: response.user.email,
        temporaryPassword: response.temporaryPassword,
        reason: "create",
      });
      setForm({
        firstName: "",
        lastName: "",
        patronymic: "",
        email: "",
        role: defaultRole,
        isActive: true,
      });
    } catch {
      // handled by mutation state
    }
  }

  async function handleSaveUser(userId: number) {
    setDeleteMessage(null);
    await updateUserMutation.mutateAsync({
      userId,
      payload: {
        role: draftRole,
        isActive: draftIsActive,
      },
    });
  }

  async function handleCopyTemporaryPassword() {
    if (!credentialPacket) {
      return;
    }

    try {
      await navigator.clipboard.writeText(credentialPacket.temporaryPassword);
      setCopyMessage("Временный пароль скопирован.");
    } catch {
      setCopyMessage("Не удалось скопировать пароль автоматически.");
    }
  }

  async function handleDeleteUser() {
    if (deleteUserId === null) {
      return;
    }
    setDeleteMessage(null);
    await deleteUserMutation.mutateAsync(deleteUserId);
  }

  return (
    <section className="space-y-6">
      <PageHeader
        title="Пользователи"
        description="Управление учетными записями, ролями и временными паролями в логике metroLog, но с фокусом на сценарии metroGen."
      />

      <section className="tone-parent space-y-4 rounded-3xl border border-line p-5 shadow-panel">
        <div>
          <h2 className="text-lg font-semibold text-ink">Добавление пользователя</h2>
          <p className="mt-1 max-w-[72ch] text-sm text-steel">
            Создай новую учетную запись, задай роль и сразу получи временный пароль. Для разработчиков
            роль `DEVELOPER` доступна только разработчику.
          </p>
        </div>

        <form
          className="grid gap-4 lg:grid-cols-2 xl:grid-cols-[1fr_1fr_1fr_1.2fr_220px_1fr]"
          onSubmit={handleCreateUser}
        >
          <label className="block text-sm text-steel">
            Фамилия
            <input
              className="form-input"
              type="text"
              placeholder="Иванов"
              value={form.lastName}
              onChange={(event) => setForm((current) => ({ ...current, lastName: event.target.value }))}
            />
          </label>

          <label className="block text-sm text-steel">
            Имя
            <input
              className="form-input"
              type="text"
              placeholder="Иван"
              value={form.firstName}
              onChange={(event) => setForm((current) => ({ ...current, firstName: event.target.value }))}
            />
          </label>

          <label className="block text-sm text-steel">
            Отчество
            <input
              className="form-input"
              type="text"
              placeholder="Иванович"
              value={form.patronymic ?? ""}
              onChange={(event) => setForm((current) => ({ ...current, patronymic: event.target.value }))}
            />
          </label>

          <label className="block text-sm text-steel">
            Email
            <input
              className="form-input"
              type="email"
              placeholder="user@example.com"
              value={form.email}
              onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
            />
          </label>

          <label className="block text-sm text-steel">
            Роль
            <select
              className="form-input"
              value={form.role}
              onChange={(event) =>
                setForm((current) => ({ ...current, role: event.target.value as CreateUserPayload["role"] }))
              }
            >
              {assignableRoles.map((role) => (
                <option key={role} value={role}>
                  {roleLabels[role]}
                </option>
              ))}
            </select>
          </label>

          <label className="flex items-center gap-3 rounded-2xl border border-line px-4 py-3 text-sm text-ink">
            <input
              checked={form.isActive}
              type="checkbox"
              onChange={(event) => setForm((current) => ({ ...current, isActive: event.target.checked }))}
            />
            Активная учетная запись
          </label>

          <div className="lg:col-span-2 xl:col-span-6">
            {createUserMutation.isError ? (
              <p className="text-sm text-[#b04c43]">
                {createUserMutation.error instanceof Error
                  ? createUserMutation.error.message
                  : "Не удалось создать пользователя."}
              </p>
            ) : null}
          </div>

          <div className="lg:col-span-2 xl:col-span-6">
            <button className="btn-primary" disabled={createUserMutation.isPending} type="submit">
              {createUserMutation.isPending ? "Создаем..." : "Создать пользователя"}
            </button>
          </div>
        </form>
      </section>

      {credentialPacket ? (
        <section className="section-card">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-ink">
                {credentialPacket.reason === "create" ? "Учетная запись создана" : "Пароль сброшен"}
              </h2>
              <p className="mt-1 text-sm text-steel">
                {credentialPacket.fullName} · {credentialPacket.email}
              </p>
            </div>
            <button className="btn-secondary btn-sm" type="button" onClick={() => void handleCopyTemporaryPassword()}>
              Скопировать пароль
            </button>
          </div>

          <div className="mt-4 rounded-3xl border border-line px-4 py-4">
            <div className="text-xs uppercase tracking-[0.16em] text-steel">Временный пароль</div>
            <div className="mt-2 break-all text-2xl font-semibold text-ink">{credentialPacket.temporaryPassword}</div>
            {copyMessage ? <div className="mt-3 text-sm text-steel">{copyMessage}</div> : null}
          </div>
        </section>
      ) : null}

      {deleteMessage ? <p className="text-sm text-signal-ok">{deleteMessage}</p> : null}

      <section className="tone-parent overflow-hidden rounded-3xl border border-line shadow-panel">
        <div className="border-b border-line px-5 py-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-ink">Список пользователей</h2>
              <p className="mt-1 text-sm text-steel">
                Поиск, быстрые действия и переход к полной карточке пользователя.
              </p>
            </div>
            <div className="status-chip status-chip--ok">Всего: {visibleUsers.length}</div>
          </div>

          <label className="mt-4 block text-sm text-steel">
            Поиск по пользователям
            <input
              className="form-input mt-2"
              type="text"
              placeholder={userSearchPlaceholder}
              value={usersSearchQuery}
              onChange={(event) => setUsersSearchQuery(event.target.value)}
            />
          </label>
        </div>

        {usersQuery.isLoading ? <p className="px-5 py-6 text-sm text-steel">Загружаем пользователей...</p> : null}
        {usersQuery.isError ? (
          <p className="px-5 py-6 text-sm text-[#b04c43]">
            {usersQuery.error instanceof Error
              ? usersQuery.error.message
              : "Не удалось загрузить список пользователей."}
          </p>
        ) : null}

        {!usersQuery.isLoading && !usersQuery.isError ? (
          <div className="space-y-0">
            {visibleUsers.length ? (
              visibleUsers.map((user) => {
                const extraInfo = buildUserExtraInfo(user);
                const isExpanded = user.id === expandedUserId;
                const isDeveloperAccount = user.role === "DEVELOPER";
                const canManageUser = canAssignDeveloperRole || !isDeveloperAccount;

                return (
                  <article key={user.id} className="border-t border-line first:border-t-0">
                    <div className="px-5 py-4">
                      <div className="flex flex-wrap items-start justify-between gap-4">
                        <div className="min-w-0">
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="text-base font-semibold text-ink">{user.fullName || user.email}</p>
                            <span
                              className={[
                                "monitor-status-badge rounded-full px-3 py-1 text-xs font-semibold",
                                user.isActive ? "monitor-status-badge--online" : "monitor-status-badge--offline",
                              ].join(" ")}
                            >
                              {user.isActive ? "Активен" : "Отключен"}
                            </span>
                            <span className="status-chip">{roleLabels[user.role]}</span>
                          </div>
                          <p className="mt-1 text-sm text-steel">{user.email}</p>
                          {extraInfo ? <p className="mt-1 text-sm text-steel">{extraInfo}</p> : null}
                        </div>

                        <div className="flex flex-wrap gap-2">
                          <button
                            className="btn-secondary btn-sm"
                            type="button"
                            onClick={() => setExpandedUserId((current) => (current === user.id ? null : user.id))}
                          >
                            {isExpanded ? "Свернуть" : "Управление"}
                          </button>
                          <Link className="btn-secondary btn-sm" to={`/admin/users/${user.id}`}>
                            Карточка
                          </Link>
                        </div>
                      </div>

                      <div className="mt-3 grid gap-2 text-sm text-steel md:grid-cols-3">
                        <div>Последний вход: <span className="text-ink">{formatDateTime(user.lastLoginAt)}</span></div>
                        <div>Последняя активность: <span className="text-ink">{formatDateTime(user.lastSeenAt)}</span></div>
                        <div>Создан: <span className="text-ink">{formatDateTime(user.createdAt)}</span></div>
                      </div>

                      {isExpanded ? (
                        <div className="mt-4 rounded-3xl border border-line p-4">
                          <div className="grid gap-4 lg:grid-cols-[220px_1fr]">
                            <label className="block text-sm text-steel">
                              Роль
                              <select
                                className="form-input"
                                disabled={!canManageUser || updateUserMutation.isPending}
                                value={draftRole}
                                onChange={(event) => setDraftRole(event.target.value as UserRole)}
                              >
                                {assignableRoles.map((role) => (
                                  <option key={role} value={role}>
                                    {roleLabels[role]}
                                  </option>
                                ))}
                              </select>
                            </label>

                            <div className="flex flex-wrap items-center gap-3">
                              <label className="flex items-center gap-3 rounded-2xl border border-line px-4 py-3 text-sm text-ink">
                                <input
                                  checked={draftIsActive}
                                  disabled={!canManageUser || updateUserMutation.isPending}
                                  type="checkbox"
                                  onChange={(event) => setDraftIsActive(event.target.checked)}
                                />
                                Активный пользователь
                              </label>

                              <button
                                className="btn-primary btn-sm"
                                disabled={!canManageUser || updateUserMutation.isPending}
                                type="button"
                                onClick={() => void handleSaveUser(user.id)}
                              >
                                {updateUserMutation.isPending && expandedUserId === user.id ? "Сохраняем..." : "Сохранить"}
                              </button>

                              <button
                                className="btn-secondary btn-sm"
                                disabled={!canManageUser || resetPasswordMutation.isPending}
                                type="button"
                                onClick={() =>
                                  void resetPasswordMutation.mutateAsync({
                                    userId: user.id,
                                    fullName: user.fullName,
                                    email: user.email,
                                  })
                                }
                              >
                                {resetPasswordMutation.isPending ? "Сбрасываем..." : "Сбросить пароль"}
                              </button>

                              <button
                                className="btn-danger btn-sm"
                                disabled={!canManageUser}
                                type="button"
                                onClick={() => setDeleteUserId(user.id)}
                              >
                                Удалить
                              </button>
                            </div>
                          </div>

                          {!canManageUser ? (
                            <p className="mt-3 text-sm text-steel">
                              Администратор не может управлять учетной записью разработчика.
                            </p>
                          ) : null}
                        </div>
                      ) : null}
                    </div>
                  </article>
                );
              })
            ) : (
              <p className="px-5 py-6 text-sm text-steel">По этому запросу пользователи не найдены.</p>
            )}
          </div>
        ) : null}
      </section>

      <DeleteConfirmModal
        description={
          selectedDeleteUser
            ? `Удаляем пользователя ${selectedDeleteUser.fullName || selectedDeleteUser.email}. Действие необратимо.`
            : "Удаляем пользователя. Действие необратимо."
        }
        errorMessage={
          deleteUserMutation.isError
            ? deleteUserMutation.error instanceof Error
              ? deleteUserMutation.error.message
              : "Не удалось удалить пользователя."
            : null
        }
        isOpen={deleteUserId !== null}
        isPending={deleteUserMutation.isPending}
        title="Удалить пользователя"
        onClose={() => setDeleteUserId(null)}
        onConfirm={() => void handleDeleteUser()}
      />
    </section>
  );
}

function formatDateTime(value: string | null) {
  if (!value) {
    return "Еще не было";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "—";
  }
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}
