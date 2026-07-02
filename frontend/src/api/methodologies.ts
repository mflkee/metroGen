import { apiRequest } from "@/api/client";

export type MethodologyPointOut = {
  position: number;
  label: string;
  point_type: string;
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
