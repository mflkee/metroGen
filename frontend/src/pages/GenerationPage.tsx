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
  fetchExportFile,
  fetchExportFolderArchive,
  fetchSystemStatus,
  type ExportFolder,
} from "@/api/system";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAuthStore } from "@/store/auth";

type WorkspaceTab = "generation" | "database" | "exports";
type RunStatus = "idle" | "running" | "success" | "error";
type ProgressStage = {
  id: string;
  label: string;
  description: string;
};

const workspaceTabs: Array<{ id: WorkspaceTab; label: string; description: string }> = [
  {
    id: "generation",
    label: "Генерация",
    description: "Запуск PDF-пакета и HTML-превью с реальным статусом выполнения.",
  },
  {
    id: "database",
    label: "База данных",
    description: "Импорт реестра и просмотр записей с фильтрацией.",
  },
  {
    id: "exports",
    label: "Готовые генерации",
    description: "История run-папок, ZIP-архивы и отдельные PDF.",
  },
];

const pdfStages: ProgressStage[] = [
  { id: "preparation", label: "Подготовка", description: "Проверяем сценарий и создаём run." },
  { id: "upload", label: "Загрузка", description: "Читаем Excel и подготавливаем входные данные." },
  { id: "contexts", label: "Аршин и реестр", description: "Собираем контексты и сертификаты по строкам." },
  { id: "saving", label: "Сохранение", description: "Рендерим PDF и сохраняем файлы в exports." },
  { id: "completed", label: "Готово", description: "Пакет собран и готов к скачиванию." },
];

const previewStages: ProgressStage[] = [
  { id: "preparation", label: "Подготовка", description: "Проверяем входные файлы и номер строки." },
  { id: "contexts", label: "Контекст", description: "Поднимаем данные для одной записи." },
  { id: "template", label: "Шаблон", description: "Рендерим HTML тем же шаблоном, что и для PDF." },
  { id: "completed", label: "Готово", description: "Превью можно проверять прямо в интерфейсе." },
];

export function GenerationPage() {
  const token = useAuthStore((state) => state.token);
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<WorkspaceTab>("generation");
  const [kind, setKind] = useState<InstrumentKind>("manometers");
  const [mode, setMode] = useState<"pdf" | "html">("pdf");
  const [failedMode, setFailedMode] = useState(false);
  const [previewRow, setPreviewRow] = useState(1);
  const [instrumentFile, setInstrumentFile] = useState<File | null>(null);
  const [dbFile, setDbFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [previewHtml, setPreviewHtml] = useState<string | null>(null);
  const [generationResult, setGenerationResult] = useState<GenerationResponse | null>(null);
  const [runStatus, setRunStatus] = useState<RunStatus>("idle");
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [runStartedAt, setRunStartedAt] = useState<number | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [jobProgress, setJobProgress] = useState<GenerationJob | null>(null);

  const [registryFile, setRegistryFile] = useState<File | null>(null);
  const [registrySourceSheet, setRegistrySourceSheet] = useState("");
  const [registryInstrumentKind, setRegistryInstrumentKind] = useState<InstrumentKind>("manometers");
  const [headerRow, setHeaderRow] = useState(5);
  const [dataStartRow, setDataStartRow] = useState(6);
  const [registryError, setRegistryError] = useState<string | null>(null);
  const [registryResult, setRegistryResult] = useState<RegistryImportResponse | null>(null);
  const [isImportingRegistry, setIsImportingRegistry] = useState(false);
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
      return undefined;
    }

    setElapsedSeconds(Math.max(1, Math.round((Date.now() - runStartedAt) / 1_000)));
    const intervalId = window.setInterval(() => {
      setElapsedSeconds(Math.max(1, Math.round((Date.now() - runStartedAt) / 1_000)));
    }, 1_000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [runStartedAt, runStatus]);

  useEffect(() => {
    if (!activeJobId) {
      return undefined;
    }

    let cancelled = false;
    let timeoutId: number | null = null;

    const poll = async () => {
      try {
        const snapshot = await fetchGenerationJob(activeJobId);
        if (cancelled) {
          return;
        }

        setJobProgress(snapshot);
        const startedAtMs = Date.parse(snapshot.startedAt);
        if (Number.isFinite(startedAtMs)) {
          setRunStartedAt(startedAtMs);
        }
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
          if (snapshot.result) {
            setGenerationResult(snapshot.result);
          }
          setActiveJobId(null);
          await queryClient.invalidateQueries({ queryKey: ["system-status"] });
          return;
        }

        setRunStatus("running");
        timeoutId = window.setTimeout(() => {
          void poll();
        }, 1_000);
      } catch (pollError) {
        if (cancelled) {
          return;
        }
        setRunStatus("error");
        setActiveJobId(null);
        setError(pollError instanceof Error ? pollError.message : "Не удалось получить статус run.");
      }
    };

    void poll();

    return () => {
      cancelled = true;
      if (timeoutId !== null) {
        window.clearTimeout(timeoutId);
      }
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
        const html = await fetchHtmlPreview(kind, {
          instrumentFile,
          dbFile,
          row: Math.max(1, previewRow),
        });
        setPreviewHtml(html);
        setCurrentStageIndex(previewStages.length - 1);
        setRunStatus("success");
      } else {
        const job = await startGenerationJob(
          kind,
          { instrumentFile, dbFile },
          kind === "manometers" && failedMode,
        );
        const startedAtMs = Date.parse(job.startedAt);
        setRunStartedAt(Number.isFinite(startedAtMs) ? startedAtMs : Date.now());
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
      setError(
        submitError instanceof Error ? submitError.message : "Не удалось выполнить генерацию.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleRegistryImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }

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
        sourceSheet: registrySourceSheet || undefined,
        instrumentKind: registryInstrumentKind,
        headerRow,
        dataStartRow,
      });
      setRegistryResult(result);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["system-status"] }),
        queryClient.invalidateQueries({ queryKey: ["registry-entries"] }),
      ]);
    } catch (importError) {
      setRegistryError(
        importError instanceof Error ? importError.message : "Не удалось импортировать реестр.",
      );
    } finally {
      setIsImportingRegistry(false);
    }
  }

  async function openExport(path: string) {
    if (!token) {
      return;
    }
    setError(null);
    setRegistryError(null);
    try {
      const blob = await fetchExportFile(token, path);
      openBlobInNewWindow(blob);
    } catch (downloadError) {
      setError(downloadError instanceof Error ? downloadError.message : "Не удалось открыть файл.");
    }
  }

  async function downloadExportFolder(path: string, folderName?: string | null) {
    if (!token) {
      return;
    }
    setError(null);
    try {
      const blob = await fetchExportFolderArchive(token, path);
      downloadBlob(blob, `${folderName || basename(path) || "generation"}.zip`);
    } catch (downloadError) {
      setError(
        downloadError instanceof Error ? downloadError.message : "Не удалось скачать архив.",
      );
    }
  }

  const activeStages = mode === "html" ? previewStages : pdfStages;
  const resolvedStageIndex =
    mode === "pdf" && jobProgress ? resolvePdfStageIndex(jobProgress.stage) : currentStageIndex;
  const currentStage = activeStages[Math.min(resolvedStageIndex, activeStages.length - 1)];
  const stageProgress =
    mode === "pdf"
      ? computePdfProgress(jobProgress, runStatus, resolvedStageIndex)
      : computePreviewProgress(runStatus, resolvedStageIndex, activeStages.length);
  const currentExportFolderPath =
    generationResult?.exportFolder ?? deriveFolderPath(generationResult?.files ?? []);
  const currentExportFolderName =
    generationResult?.exportFolderName ?? basename(currentExportFolderPath ?? "");
  const visibleGeneratedFiles = generationResult?.files.slice(0, 12) ?? [];
  const hiddenGeneratedFilesCount = Math.max(0, (generationResult?.files.length ?? 0) - visibleGeneratedFiles.length);
  const runMetrics = mode === "pdf" ? jobProgress : null;
  const isRunLocked = isSubmitting || Boolean(activeJobId);

  return (
    <section className="space-y-6">
      <PageHeader
        title="Генерация"
        description="Рабочая зона генератора: пакетный запуск, превью, импорт реестра и доступ к готовым run-папкам."
        action={
          statusQuery.data ? (
            <div
              className={[
                "status-chip",
                statusQuery.data.pdfGenerationAvailable ? "status-chip--ok" : "status-chip--warn",
              ].join(" ")}
            >
              {statusQuery.data.pdfGenerationAvailable ? "PDF-движок готов" : "Нужен Chromium"}
            </div>
          ) : undefined
        }
      />

      <div className="grid gap-3 md:grid-cols-3">
        {workspaceTabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              className={[
                "rounded-3xl border p-4 text-left shadow-panel transition",
                isActive
                  ? "border-signal-info tone-parent"
                  : "border-line bg-[color:var(--surface-1)] hover:bg-[color:var(--tone-child-bg)]",
              ].join(" ")}
              type="button"
              onClick={() => setActiveTab(tab.id)}
            >
              <div className="flex items-center justify-between gap-3">
                <span className="text-base font-semibold text-ink">{tab.label}</span>
                {isActive ? <span className="status-chip status-chip--ok">Активно</span> : null}
              </div>
              <p className="mt-2 text-sm text-steel">{tab.description}</p>
            </button>
          );
        })}
      </div>

      {activeTab === "generation" ? (
        <div className="space-y-6">
          <form className="section-card space-y-5" onSubmit={handleSubmit}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-ink">Сценарий запуска</h3>
                <p className="mt-1 text-sm text-steel">
                  Один экран для batch-PDF и проверки одной строки через HTML-превью. Для пакетного
                  запуска теперь доступен реальный статус run без ожидания одного длинного HTTP-ответа.
                </p>
              </div>
              {currentExportFolderPath ? (
                <button
                  className="btn-secondary btn-sm"
                  type="button"
                  onClick={() => void downloadExportFolder(currentExportFolderPath, currentExportFolderName)}
                >
                  Скачать ZIP последнего run
                </button>
              ) : null}
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              <label className="block text-sm text-steel">
                Тип прибора
                <select
                  className="form-input"
                  value={kind}
                  onChange={(event) => setKind(event.target.value as InstrumentKind)}
                >
                  <option value="manometers">Манометры</option>
                  <option value="controllers">Контроллеры</option>
                  <option value="thermometers">Термопреобразователи</option>
                </select>
              </label>

              <label className="block text-sm text-steel">
                Режим
                <select
                  className="form-input"
                  value={mode}
                  onChange={(event) => setMode(event.target.value as "pdf" | "html")}
                >
                  <option value="pdf">Генерация PDF-пакета</option>
                  <option value="html">HTML-превью строки</option>
                </select>
              </label>

              {kind === "manometers" && mode === "pdf" ? (
                <label className="flex items-center gap-3 rounded-2xl border border-line px-4 py-3 text-sm text-ink">
                  <input
                    checked={failedMode}
                    type="checkbox"
                    onChange={(event) => setFailedMode(event.target.checked)}
                  />
                  Сформировать браковочный протокол
                </label>
              ) : (
                <div className="rounded-2xl border border-dashed border-line px-4 py-3 text-sm text-steel">
                  Для выбранной комбинации дополнительных опций нет.
                </div>
              )}

              {mode === "html" ? (
                <label className="block text-sm text-steel">
                  Строка для превью
                  <input
                    className="form-input"
                    min={1}
                    type="number"
                    value={previewRow}
                    onChange={(event) => setPreviewRow(Number(event.target.value) || 1)}
                  />
                </label>
              ) : (
                <div className="rounded-2xl border border-line px-4 py-3 text-sm text-steel">
                  Для batch-режима результат будет сохранён в отдельную run-папку и сразу доступен как ZIP.
                </div>
              )}

              <label className="block text-sm text-steel">
                Файл приборов
                <input
                  className="form-input"
                  accept=".xlsx,.xlsm,.xls"
                  type="file"
                  onChange={(event) => setInstrumentFile(event.target.files?.[0] ?? null)}
                />
              </label>

              <label className="block text-sm text-steel">
                Файл реестра
                <input
                  className="form-input"
                  accept=".xlsx,.xlsm,.xls"
                  type="file"
                  onChange={(event) => setDbFile(event.target.files?.[0] ?? null)}
                />
              </label>
            </div>

            <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_260px]">
              <div className="rounded-3xl border border-line p-4 text-sm text-steel">
                <div className="font-semibold text-ink">Текущая связка</div>
                <div className="mt-2 space-y-1">
                  <div>
                    Приборы: <span className="text-ink">{instrumentFile?.name ?? "не выбраны"}</span>
                  </div>
                  <div>
                    Реестр: <span className="text-ink">{dbFile?.name ?? "без дополнительной БД"}</span>
                  </div>
                  <div>
                    Сценарий: <span className="text-ink">{describeScenario(kind, mode, failedMode)}</span>
                  </div>
                </div>
              </div>

              <button className="btn-primary h-full min-h-[88px] w-full" disabled={isRunLocked} type="submit">
                {isRunLocked ? "Выполняем..." : mode === "html" ? "Собрать превью" : "Запустить генерацию"}
              </button>
            </div>

            {error ? <p className="text-sm text-[#b04c43]">{error}</p> : null}
          </form>

          <div className="grid gap-6 xl:grid-cols-[minmax(320px,0.9fr)_minmax(0,1.1fr)]">
            <section className="section-card">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 className="text-lg font-semibold text-ink">Этап выполнения</h3>
                  <p className="mt-1 text-sm text-steel">
                    Трекер показывает текущий шаг, длительность run и прогресс сохранения по количеству
                    обработанных строк.
                  </p>
                </div>
                <div
                  className={[
                    "status-chip",
                    runStatus === "success"
                      ? "status-chip--ok"
                      : runStatus === "error"
                        ? "status-chip--danger"
                        : runStatus === "running"
                          ? "status-chip--warn"
                          : "",
                  ].join(" ")}
                >
                  {describeRunStatus(runStatus)}
                </div>
              </div>

              <div className="mt-5 rounded-full bg-black/5">
                <div
                  className="h-3 rounded-full bg-[var(--accent)] transition-[width] duration-500"
                  style={{ width: `${Math.max(stageProgress, 8)}%` }}
                />
              </div>

              <div className="mt-3 flex flex-wrap items-center justify-between gap-3 text-sm">
                <div className="text-ink">{currentStage.label}</div>
                <div className="text-steel">
                  {describeStageMeta(mode, jobProgress, runStatus, currentStage.description, elapsedSeconds)}
                </div>
              </div>

              {runMetrics ? (
                <div className="mt-5 grid gap-3 sm:grid-cols-3">
                  <article className="metric-card">
                    <div className="metric-card__label">Всего строк</div>
                    <div className="metric-card__value">{runMetrics.totalItems || "—"}</div>
                  </article>
                  <article className="metric-card">
                    <div className="metric-card__label">Сохранено</div>
                    <div className="metric-card__value">{runMetrics.savedCount}</div>
                  </article>
                  <article className="metric-card">
                    <div className="metric-card__label">Ошибки</div>
                    <div className="metric-card__value">{runMetrics.failedCount}</div>
                  </article>
                </div>
              ) : null}

              <div className="mt-5 space-y-3">
                {activeStages.map((stage, index) => {
                  const isDone = index < resolvedStageIndex || runStatus === "success";
                  const isCurrent = index === resolvedStageIndex && runStatus !== "success";
                  return (
                    <article
                      key={stage.id}
                      className={[
                        "rounded-2xl border px-4 py-3 transition",
                        isCurrent
                          ? "border-signal-info tone-parent"
                          : isDone
                            ? "border-line tone-child"
                            : "border-line bg-[color:var(--surface-1)]",
                      ].join(" ")}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="font-semibold text-ink">{stage.label}</p>
                          <p className="mt-1 text-sm text-steel">
                            {stage.id === "saving" && jobProgress?.totalItems
                              ? `Обработано ${jobProgress.processedItems}/${jobProgress.totalItems}, сохранено ${jobProgress.savedCount}, ошибок ${jobProgress.failedCount}.`
                              : stage.description}
                          </p>
                        </div>
                        <span
                          className={[
                            "status-chip",
                            isDone
                              ? "status-chip--ok"
                              : isCurrent
                                ? "status-chip--warn"
                                : "",
                          ].join(" ")}
                        >
                          {isDone ? "Готово" : isCurrent ? "Текущий" : "Ожидание"}
                        </span>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>

            <div className="space-y-6">
              {generationResult ? (
                <section className="section-card">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="text-lg font-semibold text-ink">Результат генерации</h3>
                      <p className="mt-1 text-sm text-steel">
                        Успешно создано {generationResult.count} файлов, ошибок: {generationResult.errors.length}.
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {currentExportFolderPath ? (
                        <button
                          className="btn-primary btn-sm"
                          type="button"
                          onClick={() =>
                            void downloadExportFolder(currentExportFolderPath, currentExportFolderName)
                          }
                        >
                          Скачать ZIP
                        </button>
                      ) : null}
                      {generationResult.files[0] ? (
                        <button
                          className="btn-secondary btn-sm"
                          type="button"
                          onClick={() => void openExport(generationResult.files[0])}
                        >
                          Открыть первый PDF
                        </button>
                      ) : null}
                    </div>
                  </div>

                  <div className="mt-5 grid gap-4 md:grid-cols-3">
                    <article className="metric-card">
                      <div className="metric-card__label">Run ID</div>
                      <div className="metric-card__value text-[1.2rem]">{generationResult.runId ?? "—"}</div>
                    </article>
                    <article className="metric-card">
                      <div className="metric-card__label">Папка</div>
                      <div className="metric-card__value text-[1rem] leading-6">
                        {currentExportFolderName || "Не определена"}
                      </div>
                    </article>
                    <article className="metric-card">
                      <div className="metric-card__label">Последнее обновление</div>
                      <div className="metric-card__value text-[1rem] leading-6">
                        {runMetrics?.finishedAt ? formatDateTime(runMetrics.finishedAt) : "—"}
                      </div>
                    </article>
                  </div>

                  <div className="mt-5 space-y-3">
                    {visibleGeneratedFiles.length ? (
                      visibleGeneratedFiles.map((path) => (
                        <div
                          key={path}
                          className="flex flex-col gap-3 rounded-2xl border border-line px-4 py-3 md:flex-row md:items-center md:justify-between"
                        >
                          <div className="min-w-0">
                            <div className="truncate text-sm font-medium text-ink">{basename(path)}</div>
                            <div className="mt-1 break-all text-xs text-steel">{path}</div>
                          </div>
                          <button
                            className="btn-secondary btn-sm shrink-0"
                            type="button"
                            onClick={() => void openExport(path)}
                          >
                            Открыть
                          </button>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-steel">Файлы не были сохранены.</p>
                    )}
                    {hiddenGeneratedFilesCount > 0 ? (
                      <div className="rounded-2xl border border-dashed border-line px-4 py-3 text-sm text-steel">
                        Ещё файлов в run: {hiddenGeneratedFilesCount}. Полный набор доступен в ZIP-архиве.
                      </div>
                    ) : null}
                  </div>

                  {generationResult.errors.length ? (
                    <div className="mt-6 rounded-3xl border border-line p-4">
                      <h4 className="text-base font-semibold text-ink">Ошибки по строкам</h4>
                      <div className="mt-3 space-y-2">
                        {generationResult.errors.map((item, index) => (
                          <div
                            key={`${item.row}-${index}`}
                            className="rounded-2xl border border-line px-3 py-3 text-sm"
                          >
                            <div className="font-medium text-ink">
                              Строка {item.row ?? "?"} · серийник {item.serial ?? "-"}
                            </div>
                            <div className="mt-1 text-steel">{item.reason ?? "Неизвестная ошибка"}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </section>
              ) : null}

              {previewHtml ? (
                <section className="section-card">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h3 className="text-lg font-semibold text-ink">HTML-превью</h3>
                      <p className="mt-1 text-sm text-steel">
                        Рендерится тем же шаблоном, который используется для итогового PDF.
                      </p>
                    </div>
                    <span className="status-chip status-chip--ok">Строка {previewRow}</span>
                  </div>
                  <iframe className="preview-frame mt-5" srcDoc={previewHtml} title="Предпросмотр протокола" />
                </section>
              ) : null}

              {!generationResult && !previewHtml ? (
                <section className="section-card">
                  <div className="rounded-3xl border border-dashed border-line px-5 py-8 text-sm text-steel">
                    Выберите файл приборов, задайте режим и запустите генерацию. После завершения здесь
                    появится run, ошибки по строкам и кнопка загрузки ZIP.
                  </div>
                </section>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      {activeTab === "database" ? (
        <div className="space-y-6">
          <div className="grid gap-6 xl:grid-cols-[minmax(0,430px)_minmax(0,1fr)]">
            <form className="section-card space-y-5" onSubmit={handleRegistryImport}>
              <div>
                <h3 className="text-lg font-semibold text-ink">Импорт выгрузки реестра</h3>
                <p className="mt-1 text-sm text-steel">
                  Загрузите реестр отдельно от batch-генерации, чтобы база была готова заранее.
                </p>
              </div>

              <label className="block text-sm text-steel">
                Excel-файл реестра
                <input
                  className="form-input"
                  accept=".xlsx,.xlsm,.xls"
                  type="file"
                  onChange={(event) => setRegistryFile(event.target.files?.[0] ?? null)}
                />
              </label>

              <label className="block text-sm text-steel">
                Тип прибора
                <select
                  className="form-input"
                  value={registryInstrumentKind}
                  onChange={(event) => setRegistryInstrumentKind(event.target.value as InstrumentKind)}
                >
                  <option value="manometers">Манометры</option>
                  <option value="controllers">Контроллеры</option>
                  <option value="thermometers">Термопреобразователи</option>
                </select>
              </label>

              <label className="block text-sm text-steel">
                Лист Excel
                <input
                  className="form-input"
                  placeholder="Если нужно жёстко указать лист"
                  type="text"
                  value={registrySourceSheet}
                  onChange={(event) => setRegistrySourceSheet(event.target.value)}
                />
              </label>

              <div className="grid gap-4 md:grid-cols-2">
                <label className="block text-sm text-steel">
                  Строка заголовков
                  <input
                    className="form-input"
                    min={1}
                    type="number"
                    value={headerRow}
                    onChange={(event) => setHeaderRow(Number(event.target.value) || 5)}
                  />
                </label>
                <label className="block text-sm text-steel">
                  Старт данных
                  <input
                    className="form-input"
                    min={1}
                    type="number"
                    value={dataStartRow}
                    onChange={(event) => setDataStartRow(Number(event.target.value) || 6)}
                  />
                </label>
              </div>

              {registryError ? <p className="text-sm text-[#b04c43]">{registryError}</p> : null}
              {registryResult ? (
                <div className="rounded-3xl border border-line p-4 text-sm text-steel">
                  <div className="font-semibold text-ink">Импорт завершён</div>
                  <div className="mt-2 space-y-1">
                    <div>
                      Файл: <span className="text-ink">{registryResult.sourceFile}</span>
                    </div>
                    <div>
                      Тип: <span className="text-ink">{registryResult.instrumentKind ?? "не указан"}</span>
                    </div>
                    <div>
                      Обработано строк: <span className="text-ink">{registryResult.processed}</span>
                    </div>
                    <div>
                      Деактивировано старых строк:{" "}
                      <span className="text-ink">{registryResult.deactivated}</span>
                    </div>
                  </div>
                </div>
              ) : null}

              <button className="btn-primary w-full" disabled={isImportingRegistry} type="submit">
                {isImportingRegistry ? "Импортируем..." : "Импортировать в БД"}
              </button>
            </form>

            <div className="space-y-6">
              <section className="section-card">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-ink">Состояние базы</h3>
                    <p className="mt-1 text-sm text-steel">
                      Сводка по наполнению рабочих таблиц, на которые опирается генерация.
                    </p>
                  </div>
                  {statusQuery.data ? (
                    <span className="status-chip status-chip--ok">
                      {statusQuery.data.database.backend}
                      {statusQuery.data.database.database ? ` · ${statusQuery.data.database.database}` : ""}
                    </span>
                  ) : null}
                </div>

                <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                  <article className="metric-card">
                    <div className="metric-card__label">Активные строки реестра</div>
                    <div className="metric-card__value">{statusQuery.data?.database.activeRegistryEntriesCount ?? "..."}</div>
                  </article>
                  <article className="metric-card">
                    <div className="metric-card__label">Все строки реестра</div>
                    <div className="metric-card__value">{statusQuery.data?.database.registryEntriesCount ?? "..."}</div>
                  </article>
                  <article className="metric-card">
                    <div className="metric-card__label">Справочник владельцев</div>
                    <div className="metric-card__value">{statusQuery.data?.database.ownersCount ?? "..."}</div>
                  </article>
                  <article className="metric-card">
                    <div className="metric-card__label">Методики</div>
                    <div className="metric-card__value">{statusQuery.data?.database.methodologiesCount ?? "..."}</div>
                  </article>
                  <article className="metric-card">
                    <div className="metric-card__label">Эталоны</div>
                    <div className="metric-card__value">{statusQuery.data?.database.etalonDevicesCount ?? "..."}</div>
                  </article>
                  <article className="metric-card">
                    <div className="metric-card__label">Вспомогательные СИ</div>
                    <div className="metric-card__value">{statusQuery.data?.database.auxiliaryInstrumentsCount ?? "..."}</div>
                  </article>
                </div>
              </section>

              <section className="section-card">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="rounded-2xl border border-line p-4 text-sm text-steel">
                    <div className="text-xs uppercase tracking-[0.16em]">Backend</div>
                    <div className="mt-1 text-ink">{statusQuery.data?.database.backend ?? "..."}</div>
                    <div className="mt-3 text-xs uppercase tracking-[0.16em]">Host</div>
                    <div className="mt-1 break-all text-ink">{statusQuery.data?.database.host ?? "локально"}</div>
                  </div>
                  <div className="rounded-2xl border border-line p-4 text-sm text-steel">
                    <div className="text-xs uppercase tracking-[0.16em]">Measuring instruments</div>
                    <div className="mt-1 text-ink">{statusQuery.data?.database.measuringInstrumentsCount ?? "..."}</div>
                    <div className="mt-3 text-xs uppercase tracking-[0.16em]">Certifications / Protocols</div>
                    <div className="mt-1 text-ink">
                      {statusQuery.data
                        ? `${statusQuery.data.database.etalonCertificationsCount} / ${statusQuery.data.database.protocolsCount}`
                        : "..."}
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </div>

          <section className="section-card">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-ink">Реестр в базе</h3>
                <p className="mt-1 text-sm text-steel">
                  Таблица показывает загруженные записи с фильтрацией по типу, активности и свободным
                  поиском по серийнику, документу, методике или исходному файлу.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="status-chip status-chip--ok">
                  Найдено: {registryEntriesQuery.data?.total ?? "..."}
                </span>
                <button className="btn-secondary btn-sm" type="button" onClick={() => void registryEntriesQuery.refetch()}>
                  Обновить
                </button>
              </div>
            </div>

            <div className="mt-5 grid gap-3 lg:grid-cols-[minmax(0,1fr)_180px_170px]">
              <label className="block text-sm text-steel">
                Поиск
                <input
                  className="form-input"
                  placeholder="Серийник, документ, методика, файл..."
                  type="text"
                  value={registrySearch}
                  onChange={(event) => setRegistrySearch(event.target.value)}
                />
              </label>

              <label className="block text-sm text-steel">
                Тип прибора
                <select
                  className="form-input"
                  value={registryFilterKind}
                  onChange={(event) =>
                    setRegistryFilterKind(event.target.value as InstrumentKind | "all")
                  }
                >
                  <option value="all">Все типы</option>
                  <option value="manometers">Манометры</option>
                  <option value="controllers">Контроллеры</option>
                  <option value="thermometers">Термопреобразователи</option>
                </select>
              </label>

              <label className="flex items-center gap-3 rounded-2xl border border-line px-4 py-3 text-sm text-ink lg:mt-6">
                <input
                  checked={registryActiveOnly}
                  type="checkbox"
                  onChange={(event) => setRegistryActiveOnly(event.target.checked)}
                />
                Только активные
              </label>
            </div>

            <div className="mt-5 overflow-x-auto rounded-3xl border border-line">
              <table className="min-w-full text-sm">
                <thead className="bg-[color:var(--surface-2)] text-left text-steel">
                  <tr>
                    <th className="px-4 py-3 font-medium">Дата поверки</th>
                    <th className="px-4 py-3 font-medium">Серийник</th>
                    <th className="px-4 py-3 font-medium">Документ</th>
                    <th className="px-4 py-3 font-medium">Протокол</th>
                    <th className="px-4 py-3 font-medium">Владелец</th>
                    <th className="px-4 py-3 font-medium">Методика</th>
                    <th className="px-4 py-3 font-medium">Источник</th>
                    <th className="px-4 py-3 font-medium">Статус</th>
                  </tr>
                </thead>
                <tbody>
                  {registryEntriesQuery.isLoading ? (
                    <tr>
                      <td className="px-4 py-6 text-steel" colSpan={8}>
                        Загружаем записи реестра...
                      </td>
                    </tr>
                  ) : registryEntriesQuery.data?.items.length ? (
                    registryEntriesQuery.data.items.map((entry) => (
                      <RegistryRow key={entry.id} entry={entry} />
                    ))
                  ) : (
                    <tr>
                      <td className="px-4 py-6 text-steel" colSpan={8}>
                        По текущим фильтрам записи не найдены.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      ) : null}

      {activeTab === "exports" ? (
        <div className="space-y-6">
          <section className="section-card">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-ink">Архив готовых генераций</h3>
                <p className="mt-1 text-sm text-steel">
                  Последние run-папки доступны для повторного скачивания. Можно взять весь пакет одним ZIP
                  или открыть отдельный протокол.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="status-chip status-chip--ok">
                  Папок: {statusQuery.data?.exportFoldersCount ?? "..."}
                </span>
                <span className="status-chip">
                  Файлов: {statusQuery.data?.generatedFilesCount ?? "..."}
                </span>
              </div>
            </div>

            <div className="mt-5 space-y-4">
              {statusQuery.isLoading ? <p className="text-sm text-steel">Загружаем историю run-папок...</p> : null}
              {statusQuery.data?.recentExports.length ? (
                statusQuery.data.recentExports.map((folder) => (
                  <ExportFolderCard
                    key={folder.path}
                    folder={folder}
                    onDownloadArchive={() => void downloadExportFolder(folder.path, folder.name)}
                    onOpenFile={(path) => void openExport(path)}
                  />
                ))
              ) : statusQuery.isLoading ? null : (
                <div className="rounded-3xl border border-dashed border-line px-4 py-8 text-sm text-steel">
                  История пока пустая. После первой генерации здесь появятся run-папки, архив и быстрые ссылки
                  на PDF.
                </div>
              )}
            </div>
          </section>
        </div>
      ) : null}
    </section>
  );
}

function RegistryRow({ entry }: { entry: RegistryEntry }) {
  return (
    <tr className="border-t border-line align-top">
      <td className="whitespace-nowrap px-4 py-3 text-ink">
        {entry.verificationDate ? formatDate(entry.verificationDate) : "—"}
      </td>
      <td className="px-4 py-3 text-ink">{entry.serial ?? "—"}</td>
      <td className="px-4 py-3 text-ink">{entry.documentNo ?? "—"}</td>
      <td className="px-4 py-3 text-ink">{entry.protocolNo ?? "—"}</td>
      <td className="px-4 py-3 text-ink">{entry.ownerName ?? "—"}</td>
      <td className="px-4 py-3 text-ink">{entry.methodology ?? "—"}</td>
      <td className="px-4 py-3">
        <div className="max-w-[280px]">
          <div className="truncate text-ink">{basename(entry.sourceFile)}</div>
          <div className="mt-1 text-xs text-steel">
            {entry.instrumentKind ?? "—"} · row {entry.rowIndex}
          </div>
        </div>
      </td>
      <td className="px-4 py-3">
        <div className="flex flex-col gap-2">
          <span className={["status-chip", entry.isActive ? "status-chip--ok" : ""].join(" ")}>
            {entry.isActive ? "Активна" : "Архив"}
          </span>
          <span className="text-xs text-steel">{formatDateTime(entry.loadedAt)}</span>
        </div>
      </td>
    </tr>
  );
}

function ExportFolderCard({
  folder,
  onDownloadArchive,
  onOpenFile,
}: {
  folder: ExportFolder;
  onDownloadArchive: () => void;
  onOpenFile: (path: string) => void;
}) {
  return (
    <article className="tone-child rounded-3xl border border-line p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h4 className="text-base font-semibold text-ink">{folder.name}</h4>
          <p className="mt-1 text-xs text-steel">
            {folder.filesCount} файлов · {formatDateTime(folder.modifiedAt)}
          </p>
        </div>
        <button className="btn-primary btn-sm" type="button" onClick={onDownloadArchive}>
          Скачать ZIP
        </button>
      </div>

      <div className="mt-4 space-y-2">
        {folder.files.map((file) => (
          <div
            key={file.path}
            className="flex flex-col gap-2 rounded-2xl border border-line px-3 py-3 sm:flex-row sm:items-center sm:justify-between"
          >
            <div className="min-w-0">
              <div className="truncate text-sm font-medium text-ink">{basename(file.path)}</div>
              <div className="mt-1 text-xs text-steel">
                {formatSize(file.sizeBytes)} · {formatDateTime(file.modifiedAt)}
              </div>
            </div>
            <button className="btn-secondary btn-sm shrink-0" type="button" onClick={() => onOpenFile(file.path)}>
              Открыть
            </button>
          </div>
        ))}
      </div>
    </article>
  );
}

function describeScenario(kind: InstrumentKind, mode: "pdf" | "html", failedMode: boolean): string {
  const kindLabel =
    kind === "controllers" ? "контроллеры" : kind === "thermometers" ? "термопреобразователи" : "манометры";
  if (mode === "html") {
    return `HTML-превью · ${kindLabel}`;
  }
  if (kind === "manometers" && failedMode) {
    return "Браковочный PDF · манометры";
  }
  return `PDF-пакет · ${kindLabel}`;
}

function describeRunStatus(status: RunStatus): string {
  if (status === "running") {
    return "Выполняется";
  }
  if (status === "success") {
    return "Готово";
  }
  if (status === "error") {
    return "С ошибкой";
  }
  return "Ожидание";
}

function describeStageMeta(
  mode: "pdf" | "html",
  job: GenerationJob | null,
  status: RunStatus,
  fallbackDescription: string,
  elapsedSeconds: number,
): string {
  if (mode === "pdf" && job) {
    if (job.stage === "saving" && job.totalItems > 0) {
      return `Обработано ${job.processedItems}/${job.totalItems} · PDF ${job.savedCount} · ошибки ${job.failedCount}`;
    }
    if (status === "running") {
      return `В работе ${elapsedSeconds} c`;
    }
  }
  return status === "running" ? `В работе ${elapsedSeconds} c` : fallbackDescription;
}

function resolvePdfStageIndex(stage: string): number {
  const index = pdfStages.findIndex((item) => item.id === stage);
  return index >= 0 ? index : 0;
}

function computePdfProgress(
  job: GenerationJob | null,
  runStatus: RunStatus,
  stageIndex: number,
): number {
  if (runStatus === "success") {
    return 100;
  }
  if (runStatus === "error" && stageIndex === pdfStages.length - 1) {
    return 100;
  }
  if (job?.stage === "saving" && job.totalItems > 0) {
    return Math.min(98, 75 + (job.processedItems / job.totalItems) * 20);
  }
  return Math.max((stageIndex / (pdfStages.length - 1)) * 100, 8);
}

function computePreviewProgress(
  runStatus: RunStatus,
  stageIndex: number,
  stagesCount: number,
): number {
  if (runStatus === "success") {
    return 100;
  }
  return Math.max((stageIndex / (Math.max(stagesCount - 1, 1))) * 100, 8);
}

function formatDateTime(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(parsed);
}

function formatDate(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
  }).format(parsed);
}

function formatSize(value: number): string {
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function basename(value: string): string {
  return value.split(/[\\/]/).pop() ?? value;
}

function deriveFolderPath(files: string[]): string | null {
  if (!files.length) {
    return null;
  }

  const normalized = files[0].split(/[\\/]/);
  if (normalized.length <= 1) {
    return null;
  }
  normalized.pop();
  return normalized.join("/");
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

function openBlobInNewWindow(blob: Blob) {
  const url = URL.createObjectURL(blob);
  window.open(url, "_blank", "noopener,noreferrer");
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
}
