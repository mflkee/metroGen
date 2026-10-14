import { Fragment, FormEvent, useEffect, useState } from "react";

import { useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchGenerationJob,
  fetchHtmlPreview,
  mapKindToApi,
  startGenerationJob,
  type GenerationJob,
  type GenerationResponse,
  type InstrumentKind,
} from "@/api/protocols";
import {
  fetchRegistryEntries,
  importRegistryFile,
  type RegistryImportResponse,
} from "@/api/registry";
import {
  deleteExportFolder,
  fetchExportFile,
  fetchExportFolderArchive,
  fetchSystemStatus,
} from "@/api/system";
import { fetchTemplateCatalog, fetchTemplateRules } from "@/api/templates";
import { ApiError } from "@/api/client";
import { DeleteConfirmModal } from "@/components/DeleteConfirmModal";
import { DateInput } from "@/components/date-input";
import { FileInput } from "@/components/ui/file-input";
import { NumberInput } from "@/components/number-input";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
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
  const [templateOverride, setTemplateOverride] = useState("");
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

  const [registryFiles, setRegistryFiles] = useState<File[]>([]);
  const [registryError, setRegistryError] = useState<string | null>(null);
  const [registryResult, setRegistryResult] = useState<RegistryImportResponse | null>(null);
  const [isImportingRegistry, setIsImportingRegistry] = useState(false);
  const [isDeletingFolder, setIsDeletingFolder] = useState<string | null>(null);
  const [pendingFolderDelete, setPendingFolderDelete] = useState<{ path: string; name: string } | null>(null);
  const [deleteFolderError, setDeleteFolderError] = useState<string | null>(null);

  const [registrySearch, setRegistrySearch] = useState("");
  const [expandedRegistryId, setExpandedRegistryId] = useState<number | null>(null);
  const [registryFilterKind, setRegistryFilterKind] = useState<InstrumentKind | "all">("all");
  const [registryActiveOnly, setRegistryActiveOnly] = useState(true);
  const [registrySource, setRegistrySource] = useState("");
  const [registryLoadedAtFrom, setRegistryLoadedAtFrom] = useState("");
  const [registryLoadedAtTo, setRegistryLoadedAtTo] = useState("");

  const statusQuery = useQuery({
    queryKey: ["system-status", "generation"],
    queryFn: () => fetchSystemStatus(token ?? ""),
    enabled: Boolean(token),
    refetchInterval: 60_000,
  });

  const templateCatalogQuery = useQuery({
    queryKey: ["template-catalog"],
    queryFn: () => fetchTemplateCatalog(token ?? ""),
    enabled: Boolean(token),
    staleTime: 60_000,
  });

  const templateRulesQuery = useQuery({
    queryKey: ["template-rules"],
    queryFn: () => fetchTemplateRules(token ?? ""),
    enabled: Boolean(token),
    staleTime: 60_000,
  });

  const registryEntriesQuery = useQuery({
    queryKey: [
      "registry-entries",
      token,
      registrySearch,
      registryFilterKind,
      registryActiveOnly,
      registrySource,
      registryLoadedAtFrom,
      registryLoadedAtTo,
    ],
    queryFn: () =>
      fetchRegistryEntries(token ?? "", {
        search: registrySearch || undefined,
        instrumentKind: registryFilterKind === "all" ? undefined : registryFilterKind,
        activeOnly: registryActiveOnly,
        source: registrySource || undefined,
        loadedAtFrom: registryLoadedAtFrom || undefined,
        loadedAtTo: registryLoadedAtTo || undefined,
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
        const job = await startGenerationJob(kind, { instrumentFile, dbFile }, (kind === "manometers" || kind === "pressure_sensors") && failedMode, kind === "controllers" ? channelsCount : 0, templateOverride || null);
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
    if (!registryFiles.length) {
      setRegistryError("Выберите файл(ы) выгрузки реестра.");
      return;
    }
    setIsImportingRegistry(true);
    try {
      const results = await Promise.all(
        registryFiles.map((file) => importRegistryFile(token, { file }))
      );
      const totalProcessed = results.reduce((sum, r) => sum + r.processed, 0);
      const totalDeactivated = results.reduce((sum, r) => sum + r.deactivated, 0);
      setRegistryResult({
        processed: totalProcessed,
        deactivated: totalDeactivated,
        instrumentKind: null,
        sourceFile: `${results.length} файл(ов)`,
      });
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

  /** The dialog asks; nothing is deleted until the owner confirms in it. */
  function handleDeleteFolder(folderPath: string, folderName: string) {
    setDeleteFolderError(null);
    setPendingFolderDelete({ path: folderPath, name: folderName });
  }

  async function confirmDeleteFolder() {
    const target = pendingFolderDelete;
    if (!token || !target) return;
    setIsDeletingFolder(target.path);
    setDeleteFolderError(null);
    try {
      await deleteExportFolder(token, target.path);
      await queryClient.invalidateQueries({ queryKey: ["system-status"] });
      setPendingFolderDelete(null);
    } catch (caught) {
      // The refusal stays inside the dialog: the page's own banner would be behind it.
      setDeleteFolderError(caught instanceof ApiError ? caught.message : "Не удалось удалить папку.");
    } finally {
      setIsDeletingFolder(null);
    }
  }

  const currentExportFolderPath = generationResult?.exportFolder ?? deriveFolderPath(generationResult?.files ?? []);
  const currentExportFolderName = generationResult?.exportFolderName ?? (currentExportFolderPath?.split(/[\\/]/).pop() ?? null);
  const isRunLocked = isSubmitting || Boolean(activeJobId);

  const apiKind = mapKindToApi(kind);
  const templateTitles = new Map(
    (templateCatalogQuery.data?.templates ?? []).map((item) => [item.id, item.title]),
  );
  const kindRules = (templateRulesQuery.data ?? [])
    .filter((rule) => rule.is_active && rule.instrument_kind === apiKind)
    .sort((left, right) => left.priority - right.priority);

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

      {error ? <p className="text-sm text-[var(--danger-text)] mb-4">{error}</p> : null}

      {activeTab === "generation" ? (
        <div className="space-y-6">
          <form className="section-card space-y-4" onSubmit={handleSubmit}>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block text-sm text-steel">
                Тип прибора
                <Select<InstrumentKind>
                  className="mt-1"
                  onChange={(next) => setKind(next)}
                  options={INSTRUMENT_KIND_OPTIONS}
                  value={kind}
                />
              </label>
              <label className="block text-sm text-steel">
                Режим
                <Select<"pdf" | "html">
                  className="mt-1"
                  onChange={(next) => setMode(next)}
                  options={[
                    { value: "pdf", label: "PDF-пакет" },
                    { value: "html", label: "HTML-превью" },
                  ]}
                  value={mode}
                />
              </label>
              <label className="block text-sm text-steel">
                Файл приборов
                <FileInput
                  accept=".xlsx,.xlsm,.xls"
                  className="mt-1"
                  fileName={instrumentFile?.name ?? null}
                  onChange={(e) => setInstrumentFile(e.target.files?.[0] ?? null)}
                />
              </label>
              {mode === "pdf" ? (
                <label className="block text-sm text-steel">
                  Файл реестра (опционально)
                  <FileInput
                    accept=".xlsx,.xlsm,.xls"
                    className="mt-1"
                    fileName={dbFile?.name ?? null}
                    onChange={(e) => setDbFile(e.target.files?.[0] ?? null)}
                  />
                </label>
              ) : (
                <label className="block text-sm text-steel">
                  Строка для превью
                  <NumberInput
                    className="form-input mt-1"
                    value={String(previewRow)}
                    onValueChange={(value) => setPreviewRow(Number(value) || 1)}
                  />
                </label>
              )}
            </div>

            <div className="rounded-2xl border border-line p-3 text-sm">
              <div className="text-xs uppercase tracking-[0.16em] text-steel">Форма протокола</div>
              {kindRules.length ? (
                <ul className="mt-2 space-y-1 text-steel">
                  {kindRules.slice(0, 6).map((rule) => (
                    <li key={rule.id}>
                      #{rule.priority} · {rule.match_field} «{rule.match_value}» →{" "}
                      {templateTitles.get(rule.template_id) ?? rule.template_id}
                    </li>
                  ))}
                  {kindRules.length > 6 ? <li>… и ещё {kindRules.length - 6}</li> : null}
                </ul>
              ) : (
                <p className="mt-2 text-steel">
                  Правил для этого типа нет — форма выбирается встроенной эвристикой.
                </p>
              )}
              <label className="mt-3 block text-steel">
                Форма на этот запуск
                <Select
                  className="mt-1"
                  onChange={(next) => setTemplateOverride(next)}
                  options={[
                    { value: "", label: "Автоматически (по правилам)" },
                    ...(templateCatalogQuery.data?.templates ?? []).map((item) => ({
                      value: item.id,
                      label: item.title,
                    })),
                  ]}
                  value={templateOverride}
                />
              </label>
            </div>

            {kind === "controllers" && mode === "pdf" ? (
              <label className="block text-sm text-steel">
                Количество каналов
                <NumberInput
                  className="form-input mt-1"
                  maxLength={2}
                  value={channelsCountStr}
                  onValueChange={setChannelsCountStr}
                />
              </label>
            ) : null}

            {(kind === "manometers" || kind === "pressure_sensors") && mode === "pdf" ? (
              <label className="flex items-center gap-3 rounded-2xl border border-line px-4 py-3 text-sm text-ink" htmlFor="generation-failed-mode">
                <Switch checked={failedMode} id="generation-failed-mode" onCheckedChange={setFailedMode} />
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
                        <div key={i} className="text-[var(--danger-text)]">Строка {item.row ?? "?"}: {item.reason ?? "ошибка"}</div>
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
                Excel-файл(ы)
                <FileInput
                  accept=".xlsx,.xlsm,.xls"
                  className="mt-1"
                  fileName={
                    registryFiles.length
                      ? `${registryFiles.length} файл(ов): ${registryFiles.map((f) => f.name).join(", ")}`
                      : null
                  }
                  multiple
                  onChange={(e) => setRegistryFiles(Array.from(e.target.files ?? []))}
                />
              </label>
              {registryFiles.length > 0 ? (
                <ul className="text-xs text-steel space-y-1">
                  {registryFiles.map((f) => (
                    <li key={f.name}>{f.name}</li>
                  ))}
                </ul>
              ) : null}
              {registryError ? <p className="text-sm text-[var(--danger-text)]">{registryError}</p> : null}
              {registryResult ? (
                <div className="rounded-2xl border border-line p-3 text-sm text-steel">
                  <div className="text-ink font-medium">Импорт завершён</div>
                  <div>Файлов: {registryResult.sourceFile}</div>
                  <div>Строк обработано: {registryResult.processed}</div>
                  {registryResult.deactivated ? <div>Деактивировано: {registryResult.deactivated}</div> : null}
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
                  <Select<InstrumentKind | "all">
                    className="max-w-[200px]"
                    compact
                    onChange={(next) => setRegistryFilterKind(next)}
                    options={[{ value: "all", label: "Все типы" }, ...INSTRUMENT_KIND_OPTIONS]}
                    value={registryFilterKind}
                  />
                  <input className="form-input max-w-[180px]" placeholder="Источник файла..." type="text" value={registrySource} onChange={(e) => setRegistrySource(e.target.value)} />
                  <label className="flex items-center gap-1 text-sm text-steel">
                    от
                    <DateInput className="form-input w-[130px]" value={registryLoadedAtFrom} onChange={(value) => setRegistryLoadedAtFrom(value)} />
                  </label>
                  <label className="flex items-center gap-1 text-sm text-steel">
                    до
                    <DateInput className="form-input w-[130px]" value={registryLoadedAtTo} onChange={(value) => setRegistryLoadedAtTo(value)} />
                  </label>
                  <label className="flex items-center gap-2 text-sm text-steel" htmlFor="registry-active-only">
                    <Switch checked={registryActiveOnly} id="registry-active-only" onCheckedChange={setRegistryActiveOnly} />
                    Активные
                  </label>
                </div>
              </div>

              <div className="overflow-x-auto rounded-2xl border border-line">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th />
                      <th>Дата поверки</th>
                      <th>Серийник</th>
                      <th>Документ</th>
                      <th>Владелец</th>
                      <th>Методика</th>
                      <th>Источник</th>
                      <th>Загружено</th>
                      <th>Статус</th>
                    </tr>
                  </thead>
                  <tbody>
                    {registryEntriesQuery.isLoading ? (
                      <tr><td className="text-center text-steel" colSpan={9}>Загрузка...</td></tr>
                    ) : registryEntriesQuery.data?.items.length ? (
                      registryEntriesQuery.data.items.map((entry) => {
                        const isOpen = expandedRegistryId === entry.id;
                        return (
                          <Fragment key={entry.id}>
                            <tr>
                              <td className="w-8">
                                <button
                                  aria-expanded={isOpen}
                                  aria-label={isOpen ? "Свернуть строку реестра" : "Раскрыть строку реестра"}
                                  className="btn-secondary btn-sm"
                                  type="button"
                                  onClick={() => setExpandedRegistryId((current) => (current === entry.id ? null : entry.id))}
                                >
                                  <span aria-hidden="true" className={["inline-block transition-transform", isOpen ? "rotate-180" : ""].join(" ")}>
                                    ▾
                                  </span>
                                </button>
                              </td>
                              <td className="whitespace-nowrap px-3 py-2 text-ink">{entry.verificationDate ? new Date(entry.verificationDate).toLocaleDateString("ru-RU") : "—"}</td>
                              <td className="text-ink">{entry.serial ?? "—"}</td>
                              <td className="text-ink">{entry.documentNo ?? "—"}</td>
                              <td className="text-ink">{entry.ownerName ?? "—"}</td>
                              <td className="text-ink">{entry.methodology ?? "—"}</td>
                              <td className="text-ink text-xs">{entry.sourceFile ?? "—"}</td>
                              <td className="whitespace-nowrap px-3 py-2 text-ink">{entry.loadedAt ? new Date(entry.loadedAt).toLocaleDateString("ru-RU") : "—"}</td>
                              <td ><span className={["status-chip", entry.isActive ? "status-chip--ok" : ""].join(" ")}>{entry.isActive ? "Активна" : "Архив"}</span></td>
                            </tr>
                            {isOpen ? (
                              <tr className="tone-child">
                                <td colSpan={9}>
                                  <dl className="grid gap-2 text-sm sm:grid-cols-2 lg:grid-cols-3">
                                    <div>
                                      <dt className="text-xs uppercase tracking-[0.16em] text-steel">Тип прибора</dt>
                                      <dd className="text-ink">{entry.instrumentKind ?? "—"}</dd>
                                    </div>
                                    <div>
                                      <dt className="text-xs uppercase tracking-[0.16em] text-steel">Лист выгрузки</dt>
                                      <dd className="text-ink">{entry.sourceSheet ?? "—"}</dd>
                                    </div>
                                    <div>
                                      <dt className="text-xs uppercase tracking-[0.16em] text-steel">Номер протокола</dt>
                                      <dd className="text-ink">{entry.protocolNo ?? "—"}</dd>
                                    </div>
                                    <div>
                                      <dt className="text-xs uppercase tracking-[0.16em] text-steel">Действительно до</dt>
                                      <dd className="text-ink">{entry.validTo ? new Date(entry.validTo).toLocaleDateString("ru-RU") : "—"}</dd>
                                    </div>
                                    <div>
                                      <dt className="text-xs uppercase tracking-[0.16em] text-steel">Строка в файле</dt>
                                      <dd className="text-ink">{entry.rowIndex}</dd>
                                    </div>
                                    <div>
                                      <dt className="text-xs uppercase tracking-[0.16em] text-steel">Загружено</dt>
                                      <dd className="text-ink">{entry.loadedAt ? new Date(entry.loadedAt).toLocaleString("ru-RU") : "—"}</dd>
                                    </div>
                                    <div className="sm:col-span-2 lg:col-span-3">
                                      <dt className="text-xs uppercase tracking-[0.16em] text-steel">Источник</dt>
                                      <dd className="break-all text-ink">{entry.sourceFile ?? "—"}</dd>
                                    </div>
                                  </dl>
                                </td>
                              </tr>
                            ) : null}
                          </Fragment>
                        );
                      })
                    ) : (
                      <tr><td className="text-center text-steel" colSpan={9}>Нет записей.</td></tr>
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
            statusQuery.data.recentExports.map((folder) => (
              <article key={folder.path} className="section-card">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h4 className="font-semibold text-ink">{folder.name}</h4>
                    <p className="text-sm text-steel">{folder.filesCount} файлов · {new Date(folder.modifiedAt).toLocaleString("ru-RU")}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <button className="btn-primary btn-sm" type="button" onClick={() => void downloadExportFolder(folder.path, folder.name)}>
                      Скачать ZIP
                    </button>
                    <button
                      className="btn-danger btn-sm"
                      disabled={isDeletingFolder === folder.path}
                      type="button"
                      onClick={() => void handleDeleteFolder(folder.path, folder.name)}
                    >
                      {isDeletingFolder === folder.path ? "Удаление..." : "Удалить"}
                    </button>
                  </div>
                </div>
              </article>
            ))
          ) : statusQuery.isLoading ? null : (
            <p className="text-sm text-steel">История пуста.</p>
          )}
        </div>
      ) : null}

      <DeleteConfirmModal
        confirmLabel="Удалить папку"
        description={
          pendingFolderDelete
            ? `Папка «${pendingFolderDelete.name}» будет удалена со всеми файлами. Это необратимо.`
            : undefined
        }
        errorMessage={deleteFolderError}
        isOpen={pendingFolderDelete !== null}
        isPending={isDeletingFolder !== null}
        title="Удалить папку экспорта?"
        onClose={() => {
          setPendingFolderDelete(null);
          setDeleteFolderError(null);
        }}
        onConfirm={() => void confirmDeleteFolder()}
      />
    </section>
  );
}

/** The instrument kinds the generator accepts, in the order the forms offer them. */
const INSTRUMENT_KIND_OPTIONS: Array<{ value: InstrumentKind; label: string }> = [
  { value: "manometers", label: "Манометры" },
  { value: "pressure_sensors", label: "Датчики давления" },
  { value: "controllers", label: "Контроллеры" },
  { value: "thermometers", label: "Термопреобразователи" },
  { value: "level_meters", label: "Уровнемеры" },
];

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
