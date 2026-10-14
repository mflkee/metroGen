import { FormEvent, useEffect, useMemo, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createOwner,
  deleteOwner,
  fetchOwners,
  replaceOwnerAliases,
  updateOwner,
  type OwnerOut,
} from "@/api/owners";
import { DeleteConfirmModal } from "@/components/DeleteConfirmModal";
import { ExpandableItem } from "@/components/ExpandableItem";
import { Modal } from "@/components/Modal";
import { PageHeader } from "@/components/ui/page-header";
import { useAuthStore } from "@/store/auth";

type OwnerModal =
  | { mode: "create" }
  | { mode: "edit"; owner: OwnerOut }
  | null;

/** Aliases are edited as one-per-line text; blank lines are dropped. */
function parseAliases(value: string): string[] {
  return value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

export function AdminOwnersPage() {
  const token = useAuthStore((state) => state.token);
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [modal, setModal] = useState<OwnerModal>(null);
  const [name, setName] = useState("");
  const [inn, setInn] = useState("");
  const [aliasesText, setAliasesText] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<OwnerOut | null>(null);

  const ownersQuery = useQuery({
    queryKey: ["owners", search],
    queryFn: () => fetchOwners(token ?? "", search || undefined),
    enabled: Boolean(token),
  });

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = { name: name.trim(), inn: inn.trim() || null };
      const aliases = parseAliases(aliasesText);
      if (modal?.mode === "edit") {
        await updateOwner(token ?? "", modal.owner.id, payload);
        await replaceOwnerAliases(token ?? "", modal.owner.id, aliases);
        return;
      }
      await createOwner(token ?? "", { ...payload, aliases });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["owners"] });
      setModal(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (ownerId: number) => deleteOwner(token ?? "", ownerId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["owners"] });
      setDeleteTarget(null);
    },
  });

  const owners = useMemo(() => ownersQuery.data ?? [], [ownersQuery.data]);

  useEffect(() => {
    if (!modal) {
      return;
    }
    if (modal.mode === "edit") {
      setName(modal.owner.name);
      setInn(modal.owner.inn ?? "");
      setAliasesText(modal.owner.aliases.join("\n"));
      return;
    }
    setName("");
    setInn("");
    setAliasesText("");
  }, [modal]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!name.trim()) {
      return;
    }
    saveMutation.mutate();
  }

  return (
    <section className="space-y-6">
      <PageHeader title="Владельцы" description="Справочник организаций-владельцев СИ." />

      <div className="section-card space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <input
            className="form-input max-w-xs"
            placeholder="Поиск..."
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button className="btn-primary btn-sm" type="button" onClick={() => setModal({ mode: "create" })}>
            Добавить
          </button>
          <span className="status-chip">Всего: {owners.length}</span>
        </div>

        {ownersQuery.isLoading ? <p className="text-sm text-steel">Загрузка...</p> : null}
        {ownersQuery.isError ? (
          <p className="text-sm text-[var(--danger-text)]">Не удалось загрузить список владельцев.</p>
        ) : null}

        <div className="space-y-3">
          {!ownersQuery.isLoading && !ownersQuery.isError && owners.length === 0 ? (
            <p className="text-sm text-steel">Нет записей.</p>
          ) : null}

          {owners.map((owner) => (
            <ExpandableItem
              key={owner.id}
              actions={
                <>
                  <button className="btn-secondary btn-sm" type="button" onClick={() => setModal({ mode: "edit", owner })}>
                    Изменить
                  </button>
                  <button className="btn-danger btn-sm" type="button" onClick={() => setDeleteTarget(owner)}>
                    Удалить
                  </button>
                </>
              }
              header={
                <div>
                  <div className="font-semibold text-ink">{owner.name}</div>
                  <div className="mt-1 text-sm text-steel">ИНН: {owner.inn ?? "—"}</div>
                </div>
              }
            >
              <div className="text-xs uppercase tracking-[0.16em] text-steel">Алиасы</div>
              {owner.aliases.length ? (
                <div className="flex flex-wrap gap-2">
                  {owner.aliases.map((alias) => (
                    <span key={alias} className="status-chip">
                      {alias}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-steel">Алиасов нет.</p>
              )}
            </ExpandableItem>
          ))}
        </div>
      </div>

      <Modal
        description={modal?.mode === "edit" ? "Измените реквизиты владельца и его алиасы." : "Добавьте организацию-владельца СИ."}
        footer={
          <div className="flex justify-end gap-3">
            <button className="btn-secondary btn-sm" type="button" onClick={() => setModal(null)}>
              Отмена
            </button>
            <button className="btn-primary btn-sm" disabled={saveMutation.isPending} form="owner-form" type="submit">
              {saveMutation.isPending ? "Сохраняем..." : "Сохранить"}
            </button>
          </div>
        }
        open={modal !== null}
        title={modal?.mode === "edit" ? "Изменить владельца" : "Новый владелец"}
        onClose={() => setModal(null)}
      >
        <form className="space-y-4" id="owner-form" onSubmit={handleSubmit}>
          <label className="block text-sm text-steel">
            Название
            <input className="form-input mt-1" required type="text" value={name} onChange={(e) => setName(e.target.value)} />
          </label>
          <label className="block text-sm text-steel">
            ИНН
            <input className="form-input mt-1" type="text" value={inn} onChange={(e) => setInn(e.target.value)} />
          </label>
          <label className="block text-sm text-steel">
            Алиасы (по одному в строке)
            <textarea
              className="form-input mt-1 min-h-[96px]"
              value={aliasesText}
              onChange={(e) => setAliasesText(e.target.value)}
            />
          </label>
          {saveMutation.isError ? (
            <p className="text-sm text-[var(--danger-text)]">
              {saveMutation.error instanceof Error ? saveMutation.error.message : "Не удалось сохранить владельца."}
            </p>
          ) : null}
        </form>
      </Modal>

      <DeleteConfirmModal
        description={
          deleteTarget
            ? `Удаляем владельца «${deleteTarget.name}». Действие необратимо.`
            : undefined
        }
        errorMessage={
          deleteMutation.isError
            ? deleteMutation.error instanceof Error
              ? deleteMutation.error.message
              : "Не удалось удалить владельца."
            : null
        }
        isOpen={deleteTarget !== null}
        isPending={deleteMutation.isPending}
        title="Удалить владельца"
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
      />
    </section>
  );
}
