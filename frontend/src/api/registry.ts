import { apiRequest } from "@/api/client";

type RawRegistryImportResponse = {
  processed: number;
  deactivated: number;
  instrument_kind: string | null;
  source_file: string;
};

export type RegistryImportPayload = {
  file: File;
  sourceSheet?: string;
  instrumentKind?: string;
  headerRow?: number;
  dataStartRow?: number;
};

export type RegistryImportResponse = {
  processed: number;
  deactivated: number;
  instrumentKind: string | null;
  sourceFile: string;
};

export async function importRegistryFile(
  token: string,
  payload: RegistryImportPayload,
): Promise<RegistryImportResponse> {
  const search = new URLSearchParams();
  if (payload.sourceSheet?.trim()) {
    search.set("source_sheet", payload.sourceSheet.trim());
  }
  if (payload.instrumentKind?.trim()) {
    search.set("instrument_kind", payload.instrumentKind.trim());
  }
  if (payload.headerRow) {
    search.set("header_row", String(payload.headerRow));
  }
  if (payload.dataStartRow) {
    search.set("data_start_row", String(payload.dataStartRow));
  }

  const formData = new FormData();
  formData.append("db_file", payload.file);

  const response = await apiRequest<RawRegistryImportResponse>(
    `/registry/import${search.size ? `?${search.toString()}` : ""}`,
    {
      method: "POST",
      token,
      body: formData,
    },
  );

  return {
    processed: response.processed,
    deactivated: response.deactivated,
    instrumentKind: response.instrument_kind,
    sourceFile: response.source_file,
  };
}
