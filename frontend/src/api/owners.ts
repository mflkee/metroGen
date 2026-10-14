import { apiRequest } from "@/api/client";

export type OwnerOut = {
  id: number;
  name: string;
  inn: string | null;
  aliases: string[];
};

export type OwnerCreatePayload = {
  name: string;
  inn?: string | null;
  aliases?: string[];
};

export async function fetchOwners(token: string, search?: string): Promise<OwnerOut[]> {
  const params = search ? `?search=${encodeURIComponent(search)}` : "";
  return apiRequest<OwnerOut[]>(`/owners${params}`, { method: "GET", token });
}

export async function createOwner(token: string, payload: OwnerCreatePayload): Promise<OwnerOut> {
  return apiRequest<OwnerOut>("/owners", {
    method: "POST",
    token,
    body: {
      name: payload.name,
      inn: payload.inn ?? null,
      aliases: payload.aliases,
    },
  });
}

export async function updateOwner(
  token: string,
  ownerId: number,
  payload: Partial<OwnerCreatePayload>,
): Promise<OwnerOut> {
  return apiRequest<OwnerOut>(`/owners/${ownerId}`, {
    method: "PATCH",
    token,
    body: {
      name: payload.name,
      inn: payload.inn,
      aliases: payload.aliases,
    },
  });
}

export async function replaceOwnerAliases(
  token: string,
  ownerId: number,
  aliases: string[],
): Promise<OwnerOut> {
  return apiRequest<OwnerOut>(`/owners/${ownerId}/aliases`, {
    method: "PUT",
    token,
    body: { aliases },
  });
}

export async function deleteOwner(token: string, ownerId: number): Promise<void> {
  await apiRequest(`/owners/${ownerId}`, { method: "DELETE", token });
}
