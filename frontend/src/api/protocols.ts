import { apiRequest } from "@/api/client";

export type InstrumentKind = "manometers" | "controllers" | "thermometers";

type RawGenerationResponse = {
  files: string[];
  count: number;
  run_id?: string | null;
  export_folder?: string | null;
  export_folder_name?: string | null;
  errors?: Array<{
    row?: number;
    serial?: string | null;
    certificate?: string | null;
    reason?: string | null;
  }>;
};

type RawGenerationJobAccepted = {
  job_id: string;
  status: string;
  stage: string;
  started_at: string;
};

type RawGenerationJob = {
  job_id: string;
  status: string;
  stage: string;
  total_items: number;
  processed_items: number;
  saved_count: number;
  failed_count: number;
  started_at: string;
  updated_at: string;
  finished_at?: string | null;
  error?: string | null;
  result?: RawGenerationResponse | null;
};

export type GenerationResponse = {
  files: string[];
  count: number;
  runId: string | null;
  exportFolder: string | null;
  exportFolderName: string | null;
  errors: Array<{
    row?: number;
    serial?: string | null;
    certificate?: string | null;
    reason?: string | null;
  }>;
};

export type GenerationJobAccepted = {
  jobId: string;
  status: string;
  stage: string;
  startedAt: string;
};

export type GenerationJob = {
  jobId: string;
  status: string;
  stage: string;
  totalItems: number;
  processedItems: number;
  savedCount: number;
  failedCount: number;
  startedAt: string;
  updatedAt: string;
  finishedAt: string | null;
  error: string | null;
  result: GenerationResponse | null;
};

type FilePayload = {
  instrumentFile: File;
  dbFile?: File | null;
};

function buildPdfPayload(kind: InstrumentKind, payload: FilePayload): FormData {
  const formData = new FormData();
  if (kind === "manometers") {
    formData.append("manometers_file", payload.instrumentFile);
  } else if (kind === "controllers") {
    formData.append("controllers_file", payload.instrumentFile);
  } else {
    formData.append("thermometers_file", payload.instrumentFile);
  }

  if (payload.dbFile) {
    formData.append("db_file", payload.dbFile);
  }
  return formData;
}

export async function generateProtocolPdf(
  kind: InstrumentKind,
  payload: FilePayload,
): Promise<GenerationResponse> {
  const response = await apiRequest<RawGenerationResponse>(resolvePdfPath(kind, false), {
    method: "POST",
    body: buildPdfPayload(kind, payload),
  });
  return {
    files: response.files,
    count: response.count,
    runId: response.run_id ?? null,
    exportFolder: response.export_folder ?? null,
    exportFolderName: response.export_folder_name ?? null,
    errors: response.errors ?? [],
  };
}

export async function startGenerationJob(
  kind: InstrumentKind,
  payload: FilePayload,
  failedMode = false,
): Promise<GenerationJobAccepted> {
  const formData = new FormData();
  formData.append("instrument_kind", kind);
  formData.append("failed_mode", String(failedMode));
  formData.append("instrument_file", payload.instrumentFile);
  if (payload.dbFile) {
    formData.append("db_file", payload.dbFile);
  }

  const response = await apiRequest<RawGenerationJobAccepted>("/protocols/jobs", {
    method: "POST",
    body: formData,
  });
  return {
    jobId: response.job_id,
    status: response.status,
    stage: response.stage,
    startedAt: response.started_at,
  };
}

export async function fetchGenerationJob(jobId: string): Promise<GenerationJob> {
  const response = await apiRequest<RawGenerationJob>(`/protocols/jobs/${encodeURIComponent(jobId)}`, {
    method: "GET",
  });
  return {
    jobId: response.job_id,
    status: response.status,
    stage: response.stage,
    totalItems: response.total_items,
    processedItems: response.processed_items,
    savedCount: response.saved_count,
    failedCount: response.failed_count,
    startedAt: response.started_at,
    updatedAt: response.updated_at,
    finishedAt: response.finished_at ?? null,
    error: response.error ?? null,
    result: response.result
      ? {
          files: response.result.files,
          count: response.result.count,
          runId: response.result.run_id ?? null,
          exportFolder: response.result.export_folder ?? null,
          exportFolderName: response.result.export_folder_name ?? null,
          errors: response.result.errors ?? [],
        }
      : null,
  };
}

export async function generateFailedManometerPdf(payload: FilePayload): Promise<GenerationResponse> {
  const response = await apiRequest<RawGenerationResponse>(resolvePdfPath("manometers", true), {
    method: "POST",
    body: buildPdfPayload("manometers", payload),
  });
  return {
    files: response.files,
    count: response.count,
    runId: response.run_id ?? null,
    exportFolder: response.export_folder ?? null,
    exportFolderName: response.export_folder_name ?? null,
    errors: response.errors ?? [],
  };
}

export async function fetchHtmlPreview(
  kind: InstrumentKind,
  payload: FilePayload & { row: number },
): Promise<string> {
  const formData = buildPreviewPayload(kind, payload);
  const response = await fetch(`${resolvePreviewUrl(kind, payload.row)}`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Preview request failed (HTTP ${response.status}).`);
  }
  return response.text();
}

function resolvePdfPath(kind: InstrumentKind, failed: boolean): string {
  if (kind === "manometers" && failed) {
    return "/protocols/manometers/failed/pdf-files";
  }
  if (kind === "controllers") {
    return "/protocols/controllers/pdf-files";
  }
  if (kind === "thermometers") {
    return "/protocols/thermometers/pdf-files";
  }
  return "/protocols/manometers/pdf-files";
}

function buildPreviewPayload(kind: InstrumentKind, payload: FilePayload): FormData {
  const formData = new FormData();
  if (kind === "controllers") {
    formData.append("file", payload.instrumentFile);
  } else if (kind === "thermometers") {
    formData.append("thermometers_file", payload.instrumentFile);
  } else {
    formData.append("manometers_file", payload.instrumentFile);
  }
  if (payload.dbFile) {
    formData.append("db_file", payload.dbFile);
  }
  return formData;
}

function resolvePreviewUrl(kind: InstrumentKind, row: number): string {
  const path =
    kind === "controllers"
      ? `/api/v1/protocols/html-by-excel?instrument_kind=controllers&row=${row}`
      : kind === "thermometers"
        ? `/api/v1/protocols/thermometers/html-preview?row=${row}`
        : `/api/v1/protocols/manometers/html-preview?row=${row}`;
  return path;
}
