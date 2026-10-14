import { apiRequest } from "@/api/client";

export type EtalonOut = {
  id: number;
  reg_number: string;
  title: string | null;
  mitype_number: string | null;
  notation: string | null;
  modification: string | null;
  manufacture_num: string | null;
  manufacture_year: number | null;
  rank_code: string | null;
  rank_title: string | null;
  schema_title: string | null;
  certificate_no: string | null;
  verification_date: string | null;
  valid_to: string | null;
};

export type EtalonUpsertPayload = {
  reg_number: string;
  title?: string | null;
  mitype_number?: string | null;
  notation?: string | null;
  modification?: string | null;
  manufacture_num?: string | null;
  manufacture_year?: number | null;
  rank_code?: string | null;
  rank_title?: string | null;
  schema_title?: string | null;
  certificate_no?: string | null;
  verification_date?: string | null;
  valid_to?: string | null;
};

export type EtalonUpdatePayload = Omit<Partial<EtalonUpsertPayload>, "reg_number">;

export type EtalonCertificationOut = {
  id: number;
  certificate_no: string;
  verification_date: string | null;
  valid_to: string | null;
  source: string | null;
};

export type EtalonCertificationPayload = {
  certificate_no: string;
  verification_date?: string | null;
  valid_to?: string | null;
};

export async function fetchEtalons(token: string): Promise<EtalonOut[]> {
  return apiRequest<EtalonOut[]>("/etalons", { method: "GET", token });
}

export async function upsertEtalon(
  token: string,
  payload: EtalonUpsertPayload,
): Promise<EtalonOut> {
  return apiRequest<EtalonOut>("/etalons", {
    method: "POST",
    token,
    body: {
      reg_number: payload.reg_number,
      title: payload.title ?? null,
      mitype_number: payload.mitype_number ?? null,
      notation: payload.notation ?? null,
      modification: payload.modification ?? null,
      manufacture_num: payload.manufacture_num ?? null,
      manufacture_year: payload.manufacture_year ?? null,
      rank_code: payload.rank_code ?? null,
      rank_title: payload.rank_title ?? null,
      schema_title: payload.schema_title ?? null,
      certificate_no: payload.certificate_no ?? null,
      verification_date: payload.verification_date ?? null,
      valid_to: payload.valid_to ?? null,
    },
  });
}

export async function updateEtalon(
  token: string,
  etalonId: number,
  payload: EtalonUpdatePayload,
): Promise<EtalonOut> {
  return apiRequest<EtalonOut>(`/etalons/${etalonId}`, {
    method: "PATCH",
    token,
    body: {
      title: payload.title ?? null,
      mitype_number: payload.mitype_number ?? null,
      notation: payload.notation ?? null,
      modification: payload.modification ?? null,
      manufacture_num: payload.manufacture_num ?? null,
      manufacture_year: payload.manufacture_year ?? null,
      rank_code: payload.rank_code ?? null,
      rank_title: payload.rank_title ?? null,
      schema_title: payload.schema_title ?? null,
      certificate_no: payload.certificate_no ?? null,
      verification_date: payload.verification_date ?? null,
      valid_to: payload.valid_to ?? null,
    },
  });
}

export async function deleteEtalon(token: string, etalonId: number): Promise<void> {
  await apiRequest(`/etalons/${etalonId}`, { method: "DELETE", token });
}

export async function fetchEtalonCertifications(
  token: string,
  etalonId: number,
): Promise<EtalonCertificationOut[]> {
  return apiRequest<EtalonCertificationOut[]>(`/etalons/${etalonId}/certifications`, {
    method: "GET",
    token,
  });
}

export async function addEtalonCertification(
  token: string,
  etalonId: number,
  payload: EtalonCertificationPayload,
): Promise<EtalonCertificationOut> {
  return apiRequest<EtalonCertificationOut>(`/etalons/${etalonId}/certifications`, {
    method: "POST",
    token,
    body: {
      certificate_no: payload.certificate_no,
      verification_date: payload.verification_date ?? null,
      valid_to: payload.valid_to ?? null,
    },
  });
}

export async function deleteEtalonCertification(
  token: string,
  etalonId: number,
  certificationId: number,
): Promise<void> {
  await apiRequest(`/etalons/${etalonId}/certifications/${certificationId}`, {
    method: "DELETE",
    token,
  });
}
