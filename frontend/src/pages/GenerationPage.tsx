import { FormEvent, useEffect, useState } from "react";

import { useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchGenerationJob,
  fetchHtmlPreview,
  startGenerationJob,
  type GenerationJob,
  type GenerationResponse,
  type InstrumentKind,
} from "@/api/protocols";
import {
  fetchRegistryEntries,
  importRegistryFile,
  type RegistryEntry,
  type RegistryImportResponse,
} from "@/api/registry";
import {
  deleteExportFiles,
  fetchExportFile,
  fetchExportFolderArchive,
  fetchExportFolderFiles,
  fetchSystemStatus,
  type ExportFile,
  type ExportFolder,
} from "@/api/system";
import { ApiError } from "@/api/client";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAuthStore } from "@/store/auth";

type WorkspaceTab = "generation" | "database" | "exports";
type RunStatus = "idle" | "running" | "success" | "error";

const workspaceTabs: Array<{ id: WorkspaceTab; label: string }> = [
  { id: "generation", label: "Генерация" },
  { id: "database", label: "База данных" },
  { id: "exports", label: "Архив" },
];

export function GenerationPage() {
  const token = useAuthStore((state) => state.token);
  const clearSession = useAuthStore((state) => state.clearSession);
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<WorkspaceTab>("generation");
  const [kind, setKind] = useState<InstrumentKind>("manometers");
  const [mode, setMode] = useState<"pdf" | "html">("pdf");
  const [failedMode, setFailedMode] = useState(false);
  const [channelsCountStr, setChannelsCountStr] = useState("4");
  const [previewRow, setPreviewRow] = useState(1);
  const [instrumentFile, setInstrumentFile] = useState<File | null>(null);
  const [dbFile, setDbFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [previewHtml, setPreviewHtml] = useState<string | null>(null);
  const [generationResult, setGenerationResult] = useState<GenerationResponse | null>(null);
  const [runStatus, setRunStatus] = useState<RunStatus>("idle");
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [runStartedAt, setRunStartedAt] = useState<number | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [jobProgress, setJobProgress] = useState<GenerationJob | null>(null);

  const [registryFile, setRegistryFile] = useState<File | null>(null);
  const [registryInstrumentKind, setRegistryInstrumentKind] = useState<InstrumentKind>("manometers");
  const [registryError, setRegistryError] = useState<string | null>(null);
  const [registryResult, setRegistryResult] = useState<RegistryImportResponse | null>(null);
  const [isImportingRegistry, setIsImportingRegistry] = useState(false);
  const [expandedFolderPath, setExpandedFolderPath] = useState<string | null>(null);
  const [folderFilesCache, setFolderFilesCache] = useState<Record<string, ExportFile[]>>({});
  const [selectedFilePaths, setSelectedFilePaths] = useState<Set<string>>(new Set());
  const [isDeletingFiles, setIsDeletingFiles] = useState(false);
  const [isLoadingFolderFiles, setIsLoadingFolderFiles] = useState(false);

  const [registrySearch, setRegistrySearch] = useState("");
  const [registryFilterKind, setRegistryFilterKind] = useState<InstrumentKind | "all">("all");
  const [registryActiveOnly, setRegistryActiveOnly] = useState(true);

  const statusQuery = useQuery({
    queryKey: ["system-status", "generation"],
    queryFn: () => fetchSystemStatus(token ?? ""),
    enabled: Boolean(token),
    refetchInterval: 60_000,
  });

  const registryEntriesQuery = useQuery({
    queryKey: ["registry-entries", token, registrySearch, registryFilterKind, registryActiveOnly],
    queryFn: () =>
      fetchRegistryEntries(token ?? "", {
        search: registrySearch || undefined,
        instrumentKind: registryFilterKind === "all" ? undefined : registryFilterKind,
        activeOnly: registryActiveOnly,
        limit: 500,
      }),
    enabled: Boolean(token) && activeTab === "database",
  });

  useEffect(() => {
    if (runStatus !== "running" || runStartedAt === null) {
      setElapsedSeconds(0);
      return;
    }
    const intervalId = window.setInterval(() => {
      setElapsedSeconds(Math.max(1, Math.round((Date.now() - runStartedAt) / 1_000)));
    }, 1_000);
    return () => window.clearInterval(intervalId);
  }, [runStatus, runStartedAt]);

  useEffect(() => {
    if (!activeJobId) {
      return;
    }
    let cancelled = false;
    let timeoutId: number | null = null;

    const poll = async () => {
      try {
        const snapshot = await fetchGenerationJob(activeJobId);
        if (cancelled) return;
        setJobProgress(snapshot);
        const startedAtMs = Date.parse(snapshot.startedAt);
        if (Number.isFinite(startedAtMs)) setRunStartedAt(startedAtMs);
        setCurrentStageIndex(resolvePdfStageIndex(snapshot.stage));

        if (snapshot.status === "success") {
          setRunStatus("success");
          setError(null);
          setGenerationResult(snapshot.result);
          setActiveJobId(null);
          await queryClient.invalidateQueries({ queryKey: ["system-status"] });
          return;
        }
        if (snapshot.status === "error") {
          setRunStatus("error");
          setError(snapshot.error ?? "Не удалось выполнить генерацию.");
          if (snapshot.result) setGenerationResult(snapshot.result);
          setActiveJobId(null);
          await queryClient.invalidateQueries({ queryKey: ["system-status"] });
          return;
        }
        setRunStatus("running");
        timeoutId = window.setTimeout(() => void poll(), 1_000);
      } catch {
        if (cancelled) return;
        setRunStatus("error");
        setActiveJobId(null);
      }
    };
    void poll();
    return () => {
      cancelled = true;
      if (timeoutId !== null) window.clearTimeout(timeoutId);
    };
  }, [activeJobId, queryClient]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (!instrumentFile) {
      setError("Выберите файл приборов.");
      return;
    }
    setActiveTab("generation");
    setIsSubmitting(true);
    setRunStatus("running");
    setCurrentStageIndex(0);
    setRunStartedAt(Date.now());
    setGenerationResult(null);
    setPreviewHtml(null);
    setJobProgress(null);
    setActiveJobId(null);

    try {
      if (mode === "html") {
        const html = await fetchHtmlPreview(kind, { instrumentFile, dbFile, row: Math.max(1, previewRow) });
        setPreviewHtml(html);
        setCurrentStageIndex(4);
        setRunStatus("success");
      } else {
        const channelsCount = Math.max(1, parseInt(channelsCountStr, 10) || 1);
        const job = await startGenerationJob(kind, { instrumentFile, dbFile }, (kind === "manometers" || kind === "pressure_sensors") && failedMode, kind === "controllers" ? channelsCount : 0);
        const startedAtMs = Date.parse(job.startedAt);
        if (Number.isFinite(startedAtMs)) setRunStartedAt(startedAtMs);
        setCurrentStageIndex(resolvePdfStageIndex(job.stage));
        setJobProgress({
          jobId: job.jobId,
          status: job.status,
          stage: job.stage,
          totalItems: 0,
          processedItems: 0,
          savedCount: 0,
          failedCount: 0,
          startedAt: job.startedAt,
          updatedAt: job.startedAt,
          finishedAt: null,
          error: null,
          result: null,
        });
        setActiveJobId(job.jobId);
      }
    } catch (submitError) {
      setRunStatus("error");
      setError(submitError instanceof Error ? submitError.message : "Не удалось выполнить генерацию.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleRegistryImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;
    setRegistryError(null);
    setRegistryResult(null);
    if (!registryFile) {
      setRegistryError("Выберите файл выгрузки реестра.");
      return;
    }
    setIsImportingRegistry(true);
    try {
      const result = await importRegistryFile(token, {
        file: registryFile,
        instrumentKind: registryInstrumentKind,
      });
      setRegistryResult(result);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["system-status"] }),
        queryClient.invalidateQueries({ queryKey: ["registry-entries"] }),
      ]);
    } catch (importError) {
      setRegistryError(importError instanceof Error ? importError.message : "Не удалось импортировать реестр.");
    } finally {
      setIsImportingRegistry(false);
    }
  }

  async function openExport(path: string) {
    if (!token) return;
    try {
      const blob = await fetchExportFile(token, path);
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        clearSession();
        return;
      }
      setError("Не удалось открыть файл.");
    }
  }

  async function downloadExportFolder(path: string, folderName?: string | null) {
    if (!token) return;
    try {
      const blob = await fetchExportFolderArchive(token, path);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${folderName || path.split(/[\\/]/).pop() || "generation"}.zip`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        clearSession();
        return;
      }
      setError("Не удалось скачать архив.");
    }
  }

  async function toggleFolder(folderPath: string) {
    if (expandedFolderPath === folderPath) {
      setExpandedFolderPath(null);
      return;
    }
    setExpandedFolderPath(folderPath);
    setSelectedFilePaths(new Set());
    if (folderFilesCache[folderPath]) return;
    if (!token) return;
    setIsLoadingFolderFiles(true);
    try {
      const files = await fetchExportFolderFiles(token, folderPath);
      setFolderFilesCache((prev) => ({ ...prev, [folderPath]: files }));
    } catch {
      setError("Не удалось загрузить список файлов.");
    } finally {
      setIsLoadingFolderFiles(false);
    }
  }

  function toggleFileSelection(filePath: string) {
    setSelectedFilePaths((prev) => {
      const next = new Set(prev);
      if (next.has(filePath)) next.delete(filePath);
      else next.add(filePath);
      return next;
    });
  }

  function toggleSelectAll(files: ExportFile[]) {
    if (files.every((f) => selectedFilePaths.has(f.path))) {
      setSelectedFilePaths(new Set());
    } else {
      setSelectedFilePaths(new Set(files.map((f) => f.path)));
    }
  }

  async function handleDeleteSelected() {
    if (!token || !selectedFilePaths.size) return;
    const confirmed = window.confirm(`Удалить ${selectedFilePaths.size} файл(ов)?`);
    if (!confirmed) return;
    const pathsToDelete = Array.from(selectedFilePaths);
    const pathsSet = new Set(pathsToDelete);
    setIsDeletingFiles(true);
    setError(null);
    try {
      const result = await deleteExportFiles(token, pathsToDelete);
      if (result.errors && Object.keys(result.errors).length) {
        setError(`Удалено ${result.deleted}, ошибок: ${Object.keys(result.errors).length}`);
      }
      setSelectedFilePaths(new Set());
      setFolderFilesCache((prev) => {
        const updated: Record<string, ExportFile[]> = {};
        for (const [folder, files] of Object.entries(prev)) {
          updated[folder] = files.filter((f) => !pathsSet.has(f.path));
        }
        return updated;
      });
      await queryClient.invalidateQueries({ queryKey: ["system-status"] });
    } catch {
      setError("Не удалось удалить файлы.");
    } finally {
      setIsDeletingFiles(false);
    }
  }

  function formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} Б`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
  }

  const currentExportFolderPath = generationResult?.exportFolder ?? deriveFolderPath(generationResult?.files ?? []);
  const currentExportFolderName = generationResult?.exportFolderName ?? (currentExportFolderPath?.split(/[\\/]/).pop() ?? null);
  const isRunLocked = isSubmitting || Boolean(activeJobId);

  return (
    <section className="space-y-6">
      <PageHeader title="Генерация" description="Пакетный запуск PDF, HTML-превью, импорт реестра и архив готовых run-папок." />

      <div className="grid gap-3 md:grid-cols-3">
        {workspaceTabs.map((tab) => (
          <button
            key={tab.id}
            className={[
              "rounded-3xl border p-3 text-left transition",
              activeTab === tab.id
                ? "border-signal-info tone-parent"
                : "border-line bg-[var(--surface-1)] hover:bg-[var(--tone-child-bg)]",
            ].join(" ")}
            type="button"
            onClick={() => setActiveTab(tab.id)}
          >
            <span className={["font-semibold", activeTab === tab.id ? "text-ink" : "text-steel"].join(" ")}>
              {tab.label}
            </span>
          </button>
        ))}
      </div>

      {error ? <p className="text-sm text-[#b04c43] mb-4">{error}</p> : null}

      {activeTab === "generation" ? (
        <div className="space-y-6">
          <form className="section-card space-y-4" onSubmit={handleSubmit}>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block text-sm text-steel">
                Тип прибора
                <select className="form-input mt-1" value={kind} onChange={(e) => setKind(e.target.value as InstrumentKind)}>
                  <option value="manometers">Манометры</option>
                  <option value="pressure_sensors">Датчики давления</option>
                  <option value="controllers">Контроллеры</option>
                  <option value="thermometers">Термопреобразователи</option>
                </select>
              </label>
              <label className="block text-sm text-steel">
                Режим
                <select className="form-input mt-1" value={mode} onChange={(e) => setMode(e.target.value as "pdf" | "html")}>
                  <option value="pdf">PDF-пакет</option>
                  <option value="html">HTML-превью</option>
                </select>
              </label>
              <label className="block text-sm text-steel">
                Файл приборов
                <input className="form-input mt-1" accept=".xlsx,.xlsm,.xls" type="file" onChange={(e) => setInstrumentFile(e.target.files?.[0] ?? null)} />
              </label>
              {mode === "pdf" ? (
                <label className="block text-sm text-steel">
                  Файл реестра (опционально)
                  <input className="form-input mt-1" accept=".xlsx,.xlsm,.xls" type="file" onChange={(e) => setDbFile(e.target.files?.[0] ?? null)} />
                </label>
              ) : (
                <label className="block text-sm text-steel">
                  Строка для превью
                  <input className="form-input mt-1" min={1} type="number" value={previewRow} onChange={(e) => setPreviewRow(Number(e.target.value) || 1)} />
                </label>
              )}
            </div>

            {kind === "controllers" && mode === "pdf" ? (
              <label className="block text-sm text-steel">
                Количество каналов
                <input className="form-input mt-1" min={1} max={99} type="number" value={channelsCountStr} onChange={(e) => setChannelsCountStr(e.target.value)} />
              </label>
            ) : null}

            {(kind === "manometers" || kind === "pressure_sensors") && mode === "pdf" ? (
              <label className="flex items-center gap-3 rounded-2xl border border-line px-4 py-3 text-sm text-ink">
                <input checked={failedMode} type="checkbox" onChange={(e) => setFailedMode(e.target.checked)} />
                Браковочный протокол
              </label>
            ) : null}

            <button className="btn-primary w-full" disabled={isRunLocked} type="submit">
              {isRunLocked ? "Выполняется..." : mode === "html" ? "Собрать превью" : "Запустить генерацию"}
            </button>
          </form>

          {activeJobId || generationResult || previewHtml ? (
            <section className="section-card">
              {activeJobId ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="h-3 flex-1 rounded-full bg-black/5">
                      <div className="h-3 rounded-full bg-[var(--accent)] transition-[width] duration-500" style={{ width: `${computeProgress(jobProgress, runStatus, currentStageIndex)}%` }} />
                    </div>
                    <span className="status-chip status-chip--warn text-sm">{elapsedSeconds} c</span>
                  </div>
                  <div className="text-sm text-steel">
                    {stageLabel(currentStageIndex)}
                    {jobProgress?.stage === "saving" && jobProgress.totalItems
                      ? ` · ${jobProgress.processedItems}/${jobProgress.totalItems}`
                      : null}
                  </div>
                </div>
              ) : null}

              {generationResult ? (
                <div className="space-y-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="font-semibold text-ink">Файлов: {generationResult.count}</span>
                    <span className="text-steel text-sm">Ошибок: {generationResult.errors.length}</span>
                    {currentExportFolderPath ? (
                      <button className="btn-primary btn-sm" type="button" onClick={() => void downloadExportFolder(currentExportFolderPath, currentExportFolderName)}>
                        Скачать ZIP
                      </button>
                    ) : null}
                  </div>
                  {generationResult.files.length ? (
                    <div className="flex flex-wrap gap-2">
                      {generationResult.files.slice(0, 8).map((path) => (
                        <button key={path} className="btn-secondary btn-sm" type="button" onClick={() => void openExport(path)}>
                          {path.split(/[\\/]/).pop()}
                        </button>
                      ))}
                    </div>
                  ) : null}
                  {generationResult.errors.length ? (
                    <div className="rounded-2xl border border-line p-3 text-sm">
                      {generationResult.errors.map((item, i) => (
                        <div key={i} className="text-[#b04c43]">Строка {item.row ?? "?"}: {item.reason ?? "ошибка"}</div>
                      ))}
                    </div>
                  ) : null}
                </div>
              ) : null}

              {previewHtml ? (
                <iframe className="preview-frame mt-3 w-full rounded-2xl border border-line" srcDoc={previewHtml} title="Предпросмотр" style={{ height: "70vh" }} />
              ) : null}
            </section>
          ) : null}
        </div>
      ) : null}

      {activeTab === "database" ? (
        <div className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-[320px_minmax(0,1fr)]">
            <form className="section-card space-y-4" onSubmit={handleRegistryImport}>
              <h3 className="font-semibold text-ink">Импорт реестра</h3>
              <label className="block text-sm text-steel">
                Excel-файл
                <input className="form-input mt-1" accept=".xlsx,.xlsm,.xls" type="file" onChange={(e) => setRegistryFile(e.target.files?.[0] ?? null)} />
              </label>
              <label className="block text-sm text-steel">
                Тип прибора
                <select className="form-input mt-1" value={registryInstrumentKind} onChange={(e) => setRegistryInstrumentKind(e.target.value as InstrumentKind)}>
                  <option value="manometers">Манометры</option>
                  <option value="pressure_sensors">Датчики давления</option>
                  <option value="controllers">Контроллеры</option>
                  <option value="thermometers">Термопреобразователи</option>
                </select>
              </label>
              {registryError ? <p className="text-sm text-[#b04c43]">{registryError}</p> : null}
              {registryResult ? (
                <div className="rounded-2xl border border-line p-3 text-sm text-steel">
                  <div className="text-ink font-medium">Импорт завершён</div>
                  <div>Файл: {registryResult.sourceFile}</div>
                  <div>Строк: {registryResult.processed}</div>
                </div>
              ) : null}
              <button className="btn-primary w-full" disabled={isImportingRegistry} type="submit">
                {isImportingRegistry ? "Импортируем..." : "Импортировать"}
              </button>
            </form>

            <section className="section-card">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                <h3 className="font-semibold text-ink">Реестр</h3>
                <div className="flex flex-wrap items-center gap-2">
                  <input className="form-input max-w-[200px]" placeholder="Поиск..." type="text" value={registrySearch} onChange={(e) => setRegistrySearch(e.target.value)} />
                  <select className="form-input max-w-[160px]" value={registryFilterKind} onChange={(e) => setRegistryFilterKind(e.target.value as InstrumentKind | "all")}>
                    <option value="all">Все типы</option>
                  <option value="manometers">Манометры</option>
                  <option value="pressure_sensors">Датчики давления</option>
                    <option value="controllers">Контроллеры</option>
                    <option value="thermometers">Термопреобразователи</option>
                  </select>
                  <label className="flex items-center gap-2 text-sm text-steel">
                    <input checked={registryActiveOnly} type="checkbox" onChange={(e) => setRegistryActiveOnly(e.target.checked)} />
                    Активные
                  </label>
                </div>
              </div>

              <div className="overflow-x-auto rounded-2xl border border-line">
                <table className="min-w-full text-sm">
                  <thead className="bg-[var(--surface-2)] text-left text-steel">
                    <tr>
                      <th className="px-3 py-2 font-medium">Дата</th>
                      <th className="px-3 py-2 font-medium">Серийник</th>
                      <th className="px-3 py-2 font-medium">Документ</th>
                      <th className="px-3 py-2 font-medium">Владелец</th>
                      <th className="px-3 py-2 font-medium">Методика</th>
                      <th className="px-3 py-2 font-medium">Статус</th>
                    </tr>
                  </thead>
                  <tbody>
                    {registryEntriesQuery.isLoading ? (
                      <tr><td className="px-3 py-4 text-steel" colSpan={6}>Загрузка...</td></tr>
                    ) : registryEntriesQuery.data?.items.length ? (
                      registryEntriesQuery.data.items.map((entry) => (
                        <tr key={entry.id} className="border-t border-line">
                          <td className="whitespace-nowrap px-3 py-2 text-ink">{entry.verificationDate ? new Date(entry.verificationDate).toLocaleDateString("ru-RU") : "—"}</td>
                          <td className="px-3 py-2 text-ink">{entry.serial ?? "—"}</td>
                          <td className="px-3 py-2 text-ink">{entry.documentNo ?? "—"}</td>
                          <td className="px-3 py-2 text-ink">{entry.ownerName ?? "—"}</td>
                          <td className="px-3 py-2 text-ink">{entry.methodology ?? "—"}</td>
                          <td className="px-3 py-2"><span className={["status-chip", entry.isActive ? "status-chip--ok" : ""].join(" ")}>{entry.isActive ? "Активна" : "Архив"}</span></td>
                        </tr>
                      ))
                    ) : (
                      <tr><td className="px-3 py-4 text-steel" colSpan={6}>Нет записей.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
              <div className="mt-2 text-xs text-steel">Найдено: {registryEntriesQuery.data?.total ?? "—"}</div>
            </section>
          </div>
        </div>
      ) : null}

      {activeTab === "exports" ? (
        <div className="space-y-4">
          {statusQuery.isLoading ? <p className="text-sm text-steel">Загрузка...</p> : null}
          {statusQuery.data?.recentExports.length ? (
            statusQuery.data.recentExports.map((folder) => {
              const isExpanded = expandedFolderPath === folder.path;
              const cachedFiles = folderFilesCache[folder.path];
              const displayFiles = cachedFiles ?? folder.files;
              const allSelected = displayFiles.length > 0 && displayFiles.every((f) => selectedFilePaths.has(f.path));
              return (
                <article key={folder.path} className="section-card space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3 cursor-pointer select-none" onClick={() => void toggleFolder(folder.path)}>
                      <span className={`transition-transform ${isExpanded ? "rotate-90" : ""}`}>▶</span>
                      <div>
                        <h4 className="font-semibold text-ink">{folder.name}</h4>
                        <p className="text-sm text-steel">{folder.filesCount} файлов · {new Date(folder.modifiedAt).toLocaleString("ru-RU")}</p>
                      </div>
                    </div>
                    <button className="btn-primary btn-sm" type="button" onClick={() => void downloadExportFolder(folder.path, folder.name)}>Скачать ZIP</button>
                  </div>
                  {isExpanded ? (
                    <div className="space-y-2 border-t border-line pt-3">
                      {selectedFilePaths.size > 0 ? (
                        <div className="flex items-center gap-3 pb-2">
                          <button className="btn-danger btn-sm" disabled={isDeletingFiles} type="button" onClick={() => void handleDeleteSelected()}>
                            {isDeletingFiles ? "Удаление..." : `Удалить выбранные (${selectedFilePaths.size})`}
                          </button>
                        </div>
                      ) : null}
                      {isLoadingFolderFiles && !cachedFiles ? (
                        <p className="text-sm text-steel">Загрузка файлов...</p>
                      ) : (
                        <>
                          <label className="flex items-center gap-2 text-sm text-steel cursor-pointer select-none pb-1">
                            <input checked={allSelected} type="checkbox" onChange={() => toggleSelectAll(displayFiles)} />
                            <span className="font-medium text-ink">{allSelected ? "Снять все" : "Выбрать все"}</span>
                          </label>
                          <div className="max-h-64 space-y-1 overflow-y-auto">
                            {displayFiles.map((file) => (
                              <label key={file.path} className="flex items-center gap-3 rounded-lg px-2 py-1.5 text-sm hover:bg-[var(--tone-child-bg)] cursor-pointer">
                                <input checked={selectedFilePaths.has(file.path)} type="checkbox" onChange={() => toggleFileSelection(file.path)} />
                                <span className="flex-1 truncate text-ink">{file.path.split(/[\\/]/).pop()}</span>
                                <span className="text-xs text-steel shrink-0">{formatFileSize(file.sizeBytes)}</span>
                                <button className="text-xs text-signal-info hover:underline shrink-0" type="button" onClick={(e) => { e.preventDefault(); void openExport(file.path); }}>
                                  Открыть
                                </button>
                              </label>
                            ))}
                          </div>
                        </>
                      )}
                      {cachedFiles && folder.filesCount > cachedFiles.length ? (
                        <p className="text-xs text-steel">Показано {cachedFiles.length} из {folder.filesCount} файлов</p>
                      ) : null}
                    </div>
                  ) : null}
                </article>
              );
            })
          ) : statusQuery.isLoading ? null : (
            <p className="text-sm text-steel">История пуста.</p>
          )}
        </div>
      ) : null}
    </section>
  );
}

function computeProgress(job: GenerationJob | null, status: RunStatus, stageIndex: number): number {
  if (status === "success") return 100;
  if (status === "error" && stageIndex === 4) return 100;
  if (job?.stage === "saving" && job.totalItems > 0) return Math.min(98, 75 + (job.processedItems / job.totalItems) * 20);
  return Math.max((stageIndex / 4) * 100, 8);
}

function stageLabel(index: number): string {
  return ["Подготовка", "Загрузка", "Аршин и реестр", "Сохранение", "Готово"][index] ?? "";
}

function resolvePdfStageIndex(stage: string): number {
  return ["preparation", "upload", "contexts", "saving", "completed"].indexOf(stage);
}

function deriveFolderPath(files: string[]): string | null {
  if (!files.length) return null;
  const parts = files[0].split(/[\\/]/);
  if (parts.length <= 1) return null;
  parts.pop();
  return parts.join("/");
}
