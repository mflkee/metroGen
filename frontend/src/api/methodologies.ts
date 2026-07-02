import { apiRequest } from "@/api/client";

export type MethodologyPointOut = {
  position: number;
  label: string;
  point_type: string;
  default_text: string | null;
};

export type MethodologyUpdatePayload = {
  title?: string;
  document?: string | null;
  notes?: string | null;
  allowable_variation_pct?: number | null;
  points?: Array<{
    position: number;
    label: string;
    point_type?: string | null;
    default_text?: string | null;
  }>;
};

export type MethodologyOut = {
  id: number;
  code: string;
  title: string;
  document: string | null;
  notes: string | null;
  allowable_variation_pct: number | null;
  points: MethodologyPointOut[];
};

export async function fetchMethodologies(token: string, search?: string): Promise<MethodologyOut[]> {
  const params = search ? `?search=${encodeURIComponent(search)}` : "";
  return apiRequest<MethodologyOut[]>(`/methodologies${params}`, { method: "GET", token });
}

export async function fetchMethodology(token: string, id: number): Promise<MethodologyOut> {
  return apiRequest<MethodologyOut>(`/methodologies/${id}`, { method: "GET", token });
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
