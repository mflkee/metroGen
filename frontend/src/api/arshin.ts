import { apiRequest } from "@/api/client";

export type ArshinLookupResult = {
  vriId: string | null;
};

export type ArshinDetails = {
  vriId: string;
  etalonLine: string;
  fields: Record<string, unknown>;
  result: Record<string, unknown>;
};

export type ArshinStatus = {
  available: boolean;
  message: string | null;
};

export async function resolveVriId(certificate: string): Promise<ArshinLookupResult> {
  const response = await apiRequest<{ vri_id: string | null }>(
    `/resolve/vri-id?cert=${encodeURIComponent(certificate)}`,
    {
      method: "GET",
    },
  );
  return { vriId: response.vri_id };
}

export async function fetchVriDetails(vriId: string): Promise<ArshinDetails> {
  const response = await apiRequest<{
    vri_id: string;
    etalon_line: string;
    fields: Record<string, unknown>;
    result: Record<string, unknown>;
  }>(`/resolve/vri/${encodeURIComponent(vriId)}`, {
    method: "GET",
  });
  return {
    vriId: response.vri_id,
    etalonLine: response.etalon_line,
    fields: response.fields,
    result: response.result,
  };
}

export async function fetchArshinStatus(token: string): Promise<ArshinStatus> {
  const response = await apiRequest<{ available: boolean; message: string | null }>("/resolve/status", {
    method: "GET",
    token,
  });
  return {
    available: response.available,
    message: response.message,
  };
}
