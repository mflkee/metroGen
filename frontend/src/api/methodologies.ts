import { apiRequest } from "@/api/client";

export type MethodologyPointOut = {
  position: number;
  label: string;
  point_type: string;
  default_text: string | null;
};

export type MethodologyPointPayload = {
  position: number;
  label: string;
  point_type?: string | null;
  default_text?: string | null;
};

type MethodologyUpdatePayload = {
  title?: string;
  document?: string | null;
  notes?: string | null;
  allowable_variation_pct?: number | null;
  points?: MethodologyPointPayload[];
};

export type MethodologyCreatePayload = {
  code: string;
  title?: string | null;
  document?: string | null;
  notes?: string | null;
  allowable_variation_pct?: number | null;
  aliases?: string[];
  points: MethodologyPointPayload[];
};

export type MethodologyOut = {
  id: number;
  code: string;
  title: string;
  document: string | null;
  notes: string | null;
  allowable_variation_pct: number | null;
  aliases: string[];
  points: MethodologyPointOut[];
};

export async function fetchMethodologies(token: string, search?: string): Promise<MethodologyOut[]> {
  const params = search ? `?search=${encodeURIComponent(search)}` : "";
  return apiRequest<MethodologyOut[]>(`/methodologies${params}`, { method: "GET", token });
}

export async function createMethodology(
  token: string,
  payload: MethodologyCreatePayload,
): Promise<MethodologyOut> {
  return apiRequest<MethodologyOut>("/methodologies", {
    method: "POST",
    token,
    body: {
      code: payload.code,
      title: payload.title ?? null,
      document: payload.document ?? null,
      notes: payload.notes ?? null,
      allowable_variation_pct: payload.allowable_variation_pct ?? null,
      aliases: payload.aliases ?? [],
      points: payload.points,
    },
  });
}

export async function updateMethodology(
  token: string,
  id: number,
  payload: MethodologyUpdatePayload,
): Promise<MethodologyOut> {
  return apiRequest<MethodologyOut>(`/methodologies/${id}`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export async function replaceMethodologyAliases(
  token: string,
  id: number,
  aliases: string[],
): Promise<MethodologyOut> {
  return apiRequest<MethodologyOut>(`/methodologies/${id}/aliases`, {
    method: "PUT",
    token,
    body: { aliases },
  });
}

export async function deleteMethodology(token: string, id: number): Promise<void> {
  await apiRequest(`/methodologies/${id}`, { method: "DELETE", token });
}
