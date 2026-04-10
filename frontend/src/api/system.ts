import { fetchBinary, apiRequest } from "@/api/client";

type RawExportFile = {
  path: string;
  size_bytes: number;
  modified_at: string;
};

type RawExportFolder = {
  name: string;
  path: string;
  files_count: number;
  modified_at: string;
  files: RawExportFile[];
};

type RawSystemStatus = {
  app_name: string;
  app_env: string;
  exports_dir: string;
  signatures_dir: string;
  smtp_configured: boolean;
  pdf_generation_available: boolean;
  users_count: number;
  active_users_count: number;
  export_folders_count: number;
  generated_files_count: number;
  database: {
    backend: string;
    database: string | null;
    host: string | null;
    owners_count: number;
    methodologies_count: number;
    registry_entries_count: number;
    active_registry_entries_count: number;
    auxiliary_instruments_count: number;
    etalon_devices_count: number;
    etalon_certifications_count: number;
    measuring_instruments_count: number;
    protocols_count: number;
  };
  recent_exports: RawExportFolder[];
};

export type ExportFile = {
  path: string;
  sizeBytes: number;
  modifiedAt: string;
};

export type ExportFolder = {
  name: string;
  path: string;
  filesCount: number;
  modifiedAt: string;
  files: ExportFile[];
};

export type SystemStatus = {
  appName: string;
  appEnv: string;
  exportsDir: string;
  signaturesDir: string;
  smtpConfigured: boolean;
  pdfGenerationAvailable: boolean;
  usersCount: number;
  activeUsersCount: number;
  exportFoldersCount: number;
  generatedFilesCount: number;
  database: {
    backend: string;
    database: string | null;
    host: string | null;
    ownersCount: number;
    methodologiesCount: number;
    registryEntriesCount: number;
    activeRegistryEntriesCount: number;
    auxiliaryInstrumentsCount: number;
    etalonDevicesCount: number;
    etalonCertificationsCount: number;
    measuringInstrumentsCount: number;
    protocolsCount: number;
  };
  recentExports: ExportFolder[];
};

export async function fetchSystemStatus(token: string): Promise<SystemStatus> {
  const response = await apiRequest<RawSystemStatus>("/system/status", {
    method: "GET",
    token,
  });
  return {
    appName: response.app_name,
    appEnv: response.app_env,
    exportsDir: response.exports_dir,
    signaturesDir: response.signatures_dir,
    smtpConfigured: response.smtp_configured,
    pdfGenerationAvailable: response.pdf_generation_available,
    usersCount: response.users_count,
    activeUsersCount: response.active_users_count,
    exportFoldersCount: response.export_folders_count,
    generatedFilesCount: response.generated_files_count,
    database: {
      backend: response.database.backend,
      database: response.database.database,
      host: response.database.host,
      ownersCount: response.database.owners_count,
      methodologiesCount: response.database.methodologies_count,
      registryEntriesCount: response.database.registry_entries_count,
      activeRegistryEntriesCount: response.database.active_registry_entries_count,
      auxiliaryInstrumentsCount: response.database.auxiliary_instruments_count,
      etalonDevicesCount: response.database.etalon_devices_count,
      etalonCertificationsCount: response.database.etalon_certifications_count,
      measuringInstrumentsCount: response.database.measuring_instruments_count,
      protocolsCount: response.database.protocols_count,
    },
    recentExports: response.recent_exports.map((folder) => ({
      name: folder.name,
      path: folder.path,
      filesCount: folder.files_count,
      modifiedAt: folder.modified_at,
      files: folder.files.map((file) => ({
        path: file.path,
        sizeBytes: file.size_bytes,
        modifiedAt: file.modified_at,
      })),
    })),
  };
}

export async function fetchExportFile(token: string, path: string): Promise<Blob> {
  return fetchBinary(`/system/export-file?path=${encodeURIComponent(path)}`, token);
}

export async function fetchExportFolderArchive(token: string, path: string): Promise<Blob> {
  return fetchBinary(`/system/export-folder-archive?path=${encodeURIComponent(path)}`, token);
}
