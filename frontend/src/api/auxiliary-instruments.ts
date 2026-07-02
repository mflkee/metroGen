import { apiRequest } from "@/api/client";

export type AuxInstrumentOut = {
  id: number;
  title: string;
  reg_number: string;
  modification: string | null;
  manufacture_num: string;
  certificate_no: string | null;
  verification_date: string | null;
  valid_to: string | null;
};

export type AuxInstrumentCreatePayload = {
  title: string;
  reg_number: string;
  modification?: string | null;
  manufacture_num: string;
  certificate_no?: string | null;
  verification_date?: string | null;
  valid_to?: string | null;
};

export async function fetchAuxInstruments(token: string): Promise<AuxInstrumentOut[]> {
  return apiRequest<AuxInstrumentOut[]>("/auxiliary-instruments", { method: "GET", token });
}

export async function createAuxInstrument(
  token: string,
  payload: AuxInstrumentCreatePayload,
): Promise<AuxInstrumentOut> {
  return apiRequest<AuxInstrumentOut>("/auxiliary-instruments", {
    method: "POST",
    token,
    body: {
      title: payload.title,
      reg_number: payload.reg_number,
      modification: payload.modification ?? null,
      manufacture_num: payload.manufacture_num,
      certificate_no: payload.certificate_no ?? null,
      verification_date: payload.verification_date ?? null,
      valid_to: payload.valid_to ?? null,
    },
  });
}
