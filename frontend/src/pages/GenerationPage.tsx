import { FormEvent, useEffect, useMemo, useState } from "react";

import { useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchHtmlPreview,
  generateFailedManometerPdf,
  generateProtocolPdf,
  type GenerationResponse,
  type InstrumentKind,
} from "@/api/protocols";
import { importRegistryFile, type RegistryImportResponse } from "@/api/registry";
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
  label: string;
  description: string;
};

const workspaceTabs: Array<{ id: WorkspaceTab; label: string; description: string }> = [
  {
    id: "generation",
    label: "Генерация",
    description: "Запуск PDF-пакета и HTML-превью с визуальным прогрессом.",
  },
  {
    id: "database",
    label: "База данных",
    description: "Импорт реестра поверок и контроль наполнения справочников.",
  },
  {
    id: "exports",
    label: "Готовые генерации",
    description: "Архив последних запусков, ZIP-выдача и быстрый доступ к PDF.",
  },
];

const pdfStages: ProgressStage[] = [
  { label: "Подготовка", description: "Проверяем сценарий, файлы и параметры запуска." },
  { label: "Загрузка", description: "Передаём Excel и реестр на backend." },
  { label: "Аршин и реестр", description: "Собираем контексты и поднимаем данные по сертификатам." },
  { label: "Рендер", description: "Строим HTML и готовим пакет PDF." },
  { label: "Сохранение", description: "Фиксируем run в exports и собираем выдачу." },
];

const previewStages: ProgressStage[] = [
  { label: "Подготовка", description: "Проверяем строку и входные файлы." },
  { label: "Контекст", description: "Поднимаем данные для одной записи." },
  { label: "Шаблон", description: "Рендерим HTML тем же шаблоном, что и для PDF." },
  { label: "Готово", description: "Превью можно проверять прямо в интерфейсе." },
];

const pdfStageDelays = [600, 2_200, 5_100, 8_400];
const previewStageDelays = [500, 1_500, 3_000];

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

  const [registryFile, setRegistryFile] = useState<File | null>(null);
  const [registrySourceSheet, setRegistrySourceSheet] = useState("");
  const [registryInstrumentKind, setRegistryInstrumentKind] = useState<InstrumentKind>("manometers");
  const [headerRow, setHeaderRow] = useState(5);
  const [dataStartRow, setDataStartRow] = useState(6);
  const [registryError, setRegistryError] = useState<string | null>(null);
  const [registryResult, setRegistryResult] = useState<RegistryImportResponse | null>(null);
  const [isImportingRegistry, setIsImportingRegistry] = useState(false);

  const statusQuery = useQuery({
    queryKey: ["system-status", "generation"],
    queryFn: () => fetchSystemStatus(token ?? ""),
    enabled: Boolean(token),
    refetchInterval: 60_000,
  });

  const activeStages = mode === "html" ? previewStages : pdfStages;
  const activeStageDelays = mode === "html" ? previewStageDelays : pdfStageDelays;
  const stageProgress = activeStages.length > 1 ? (currentStageIndex / (activeStages.length - 1)) * 100 : 0;
  const currentStage = activeStages[Math.min(currentStageIndex, activeStages.length - 1)];
  const currentExportFolderPath = generationResult?.exportFolder ?? deriveFolderPath(generationResult?.files ?? []);
  const currentExportFolderName = generationResult?.exportFolderName ?? basename(currentExportFolderPath ?? "");

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
    if (!isSubmitting) {
      return undefined;
    }

    setCurrentStageIndex(0);
    const timeoutIds = activeStageDelays.map((delay, index) =>
      window.setTimeout(() => {
        setCurrentStageIndex(Math.min(index + 1, activeStages.length - 1));
      }, delay),
    );

    return () => {
      timeoutIds.forEach((timeoutId) => window.clearTimeout(timeoutId));
    };
  }, [activeStageDelays, activeStages.length, isSubmitting]);

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

    try {
      if (mode === "html") {
        const html = await fetchHtmlPreview(kind, {
          instrumentFile,
          dbFile,
          row: Math.max(1, previewRow),
        });
        setPreviewHtml(html);
        setGenerationResult(null);
      } else {
        const result =
          kind === "manometers" && failedMode
            ? await generateFailedManometerPdf({ instrumentFile, dbFile })
            : await generateProtocolPdf(kind, { instrumentFile, dbFile });
        setGenerationResult(result);
        setPreviewHtml(null);
      }

      setCurrentStageIndex(activeStages.length - 1);
      setRunStatus("success");
      await queryClient.invalidateQueries({ queryKey: ["system-status"] });
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
      await queryClient.invalidateQueries({ queryKey: ["system-status"] });
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
      setError(
        downloadError instanceof Error ? downloadError.message : "Не удалось открыть файл.",
      );
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

  return (
    <section className="space-y-6">
      <PageHeader
        title="Генерация"
        description="Рабочая зона генератора: запуск пакетной выдачи, импорт БД и управление готовыми run-папками без выхода из интерфейса."
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
        <div className="grid gap-6 xl:grid-cols-[minmax(0,430px)_minmax(0,1fr)]">
          <div className="space-y-6">
            <form className="section-card space-y-5" onSubmit={handleSubmit}>
              <div>
                <h3 className="text-lg font-semibold text-ink">Сценарий запуска</h3>
                <p className="mt-1 text-sm text-steel">
                  Один экран для batch-PDF и проверки одной строки через HTML-превью. Результат сразу
                  сохраняется в отдельный run и появляется в истории.
                </p>
              </div>

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
              ) : null}

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
              ) : null}

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

              <div className="rounded-3xl border border-line p-4 text-sm text-steel">
                <div className="font-semibold text-ink">Текущая связка</div>
                <div className="mt-2 space-y-1">
                  <div>Приборы: <span className="text-ink">{instrumentFile?.name ?? "не выбраны"}</span></div>
                  <div>Реестр: <span className="text-ink">{dbFile?.name ?? "без дополнительной БД"}</span></div>
                  <div>Сценарий: <span className="text-ink">{describeScenario(kind, mode, failedMode)}</span></div>
                </div>
              </div>

              {error ? <p className="text-sm text-[#b04c43]">{error}</p> : null}

              <button className="btn-primary w-full" disabled={isSubmitting} type="submit">
                {isSubmitting ? "Выполняем..." : mode === "html" ? "Собрать превью" : "Запустить генерацию"}
              </button>
            </form>

            <section className="section-card">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 className="text-lg font-semibold text-ink">Этап выполнения</h3>
                  <p className="mt-1 text-sm text-steel">
                    Визуальный трекер нужен, чтобы во время batch-запуска было понятно, на каком шаге
                    находится процесс.
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
                  style={{ width: `${runStatus === "success" ? 100 : Math.max(stageProgress, 8)}%` }}
                />
              </div>

              <div className="mt-3 flex flex-wrap items-center justify-between gap-3 text-sm">
                <div className="text-ink">{currentStage.label}</div>
                <div className="text-steel">
                  {runStatus === "running" ? `В работе ${elapsedSeconds} c` : currentStage.description}
                </div>
              </div>

              <div className="mt-5 space-y-3">
                {activeStages.map((stage, index) => {
                  const isDone = index < currentStageIndex || runStatus === "success";
                  const isCurrent = index === currentStageIndex && runStatus !== "success";
                  return (
                    <article
                      key={stage.label}
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
                          <p className="mt-1 text-sm text-steel">{stage.description}</p>
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
          </div>

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
                        onClick={() => void downloadExportFolder(currentExportFolderPath, currentExportFolderName)}
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
                    <div className="metric-card__value text-[1.35rem]">{generationResult.runId ?? "—"}</div>
                  </article>
                  <article className="metric-card">
                    <div className="metric-card__label">Папка</div>
                    <div className="metric-card__value text-[1.1rem] leading-6">
                      {currentExportFolderName || "Не определена"}
                    </div>
                  </article>
                  <article className="metric-card">
                    <div className="metric-card__label">Ошибки</div>
                    <div className="metric-card__value">{generationResult.errors.length}</div>
                  </article>
                </div>

                <div className="mt-5 space-y-3">
                  {generationResult.files.length ? (
                    generationResult.files.map((path) => (
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
                </div>

                {generationResult.errors.length ? (
                  <div className="mt-6 rounded-3xl border border-line p-4">
                    <h4 className="text-base font-semibold text-ink">Ошибки по строкам</h4>
                    <div className="mt-3 space-y-2">
                      {generationResult.errors.map((item, index) => (
                        <div key={`${item.row}-${index}`} className="rounded-2xl border border-line px-3 py-3 text-sm">
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
                <h3 className="text-lg font-semibold text-ink">Как пользоваться страницей</h3>
                <div className="mt-5 grid gap-3 md:grid-cols-2">
                  <article className="tone-child rounded-3xl border border-line p-4">
                    <h4 className="text-base font-semibold text-ink">PDF-пакет</h4>
                    <p className="mt-2 text-sm text-steel">
                      Для массовой выдачи выберите прибор, приложите файл приборов и при необходимости
                      реестр. После запуска получите отдельную run-папку и ZIP одним кликом.
                    </p>
                  </article>
                  <article className="tone-child rounded-3xl border border-line p-4">
                    <h4 className="text-base font-semibold text-ink">HTML-превью</h4>
                    <p className="mt-2 text-sm text-steel">
                      Для проверки шаблона достаточно указать номер строки. Это быстрый цикл без ожидания
                      полного пакетного рендера.
                    </p>
                  </article>
                </div>

                <div className="mt-5 rounded-3xl border border-line p-4 text-sm text-steel">
                  <div className="font-semibold text-ink">Что ещё доступно с этой страницы</div>
                  <div className="mt-2 space-y-1">
                    <div>1. Импорт реестра во вкладке «База данных».</div>
                    <div>2. История готовых run-папок во вкладке «Готовые генерации».</div>
                    <div>3. Повторное скачивание всего набора протоколов через ZIP.</div>
                  </div>
                </div>
              </section>
            ) : null}
          </div>
        </div>
      ) : null}

      {activeTab === "database" ? (
        <div className="grid gap-6 xl:grid-cols-[minmax(0,430px)_minmax(0,1fr)]">
          <form className="section-card space-y-5" onSubmit={handleRegistryImport}>
            <div>
              <h3 className="text-lg font-semibold text-ink">Импорт выгрузки реестра</h3>
              <p className="mt-1 text-sm text-steel">
                Эта зона нужна для самостоятельной загрузки DB-файла без запуска генерации, чтобы
                справочники и активные строки были готовы заранее.
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
                  <div>Файл: <span className="text-ink">{registryResult.sourceFile}</span></div>
                  <div>Тип: <span className="text-ink">{registryResult.instrumentKind ?? "не указан"}</span></div>
                  <div>Обработано строк: <span className="text-ink">{registryResult.processed}</span></div>
                  <div>Деактивировано старых строк: <span className="text-ink">{registryResult.deactivated}</span></div>
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
                    Живой срез наполнения справочников и рабочих таблиц, на которые опирается генерация.
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
              <h3 className="text-lg font-semibold text-ink">Контекст сервиса</h3>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-line p-4 text-sm text-steel">
                  <div className="text-xs uppercase tracking-[0.16em]">Бэкенд БД</div>
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

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
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
