import { apiRequest } from "@/api/client";

type RawRegistryImportResponse = {
  processed: number;
  deactivated: number;
  instrument_kind: string | null;
  source_file: string;
};

type RawRegistryEntry = {
  id: number;
  source_file: string;
  source_sheet?: string | null;
  instrument_kind?: string | null;
  row_index: number;
  normalized_serial?: string | null;
  document_no?: string | null;
  protocol_no?: string | null;
  owner_name_raw?: string | null;
  methodology_raw?: string | null;
  verification_date?: string | null;
  valid_to?: string | null;
  is_active: boolean;
  loaded_at: string;
};

type RawRegistryEntryList = {
  total: number;
  items: RawRegistryEntry[];
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

export type RegistryEntry = {
  id: number;
  sourceFile: string;
  sourceSheet: string | null;
  instrumentKind: string | null;
  rowIndex: number;
  serial: string | null;
  documentNo: string | null;
  protocolNo: string | null;
  ownerName: string | null;
  methodology: string | null;
  verificationDate: string | null;
  validTo: string | null;
  isActive: boolean;
  loadedAt: string;
};

export type RegistryEntryList = {
  total: number;
  items: RegistryEntry[];
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

export async function fetchRegistryEntries(
  token: string,
  params: {
    search?: string;
    instrumentKind?: string;
    activeOnly?: boolean;
    limit?: number;
  } = {},
): Promise<RegistryEntryList> {
  const search = new URLSearchParams();
  if (params.search?.trim()) {
    search.set("search", params.search.trim());
  }
  if (params.instrumentKind?.trim()) {
    search.set("instrument_kind", params.instrumentKind.trim());
  }
  if (params.activeOnly !== undefined) {
    search.set("active_only", String(params.activeOnly));
  }
  if (params.limit) {
    search.set("limit", String(params.limit));
  }

  const response = await apiRequest<RawRegistryEntryList>(
    `/registry/entries${search.size ? `?${search.toString()}` : ""}`,
    {
      method: "GET",
      token,
    },
  );

  return {
    total: response.total,
    items: response.items.map((item) => ({
      id: item.id,
      sourceFile: item.source_file,
      sourceSheet: item.source_sheet ?? null,
      instrumentKind: item.instrument_kind ?? null,
      rowIndex: item.row_index,
      serial: item.normalized_serial ?? null,
      documentNo: item.document_no ?? null,
      protocolNo: item.protocol_no ?? null,
      ownerName: item.owner_name_raw ?? null,
      methodology: item.methodology_raw ?? null,
      verificationDate: item.verification_date ?? null,
      validTo: item.valid_to ?? null,
      isActive: item.is_active,
      loadedAt: item.loaded_at,
    })),
  };
}
