import { FormEvent, useState } from "react";

import { PageHeader } from "@/components/layout/PageHeader";
import {
  fetchHtmlPreview,
  generateFailedManometerPdf,
  generateProtocolPdf,
  type GenerationResponse,
  type InstrumentKind,
} from "@/api/protocols";
import { fetchExportFile } from "@/api/system";
import { useAuthStore } from "@/store/auth";

export function GenerationPage() {
  const token = useAuthStore((state) => state.token);
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

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    if (!instrumentFile) {
      setError("Выберите файл приборов.");
      setIsSubmitting(false);
      return;
    }

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
    } catch (submitError) {
      setError(
        submitError instanceof Error ? submitError.message : "Не удалось выполнить генерацию.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function openExport(path: string) {
    if (!token) {
      return;
    }
    try {
      const blob = await fetchExportFile(token, path);
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank", "noopener,noreferrer");
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (downloadError) {
      setError(
        downloadError instanceof Error ? downloadError.message : "Не удалось открыть файл.",
      );
    }
  }

  return (
    <section>
      <PageHeader
        title="Генерация"
        description="Единый экран для запуска PDF-генерации и HTML-превью. Интерфейс построен вокруг текущих ручек metroGen без дублирования старой логики."
      />

      <div className="grid gap-6 xl:grid-cols-[minmax(0,420px)_minmax(0,1fr)]">
        <form className="section-card space-y-5" onSubmit={handleSubmit}>
          <div>
            <h3 className="text-lg font-semibold text-ink">Сценарий</h3>
            <p className="mt-1 text-sm text-steel">
              Выберите тип прибора и режим. Для манометров можно сразу переключиться в браковочный PDF.
            </p>
          </div>

          <label className="block text-sm text-steel">
            Тип прибора
            <select className="form-input" value={kind} onChange={(event) => setKind(event.target.value as InstrumentKind)}>
              <option value="manometers">Манометры</option>
              <option value="controllers">Контроллеры</option>
              <option value="thermometers">Термопреобразователи</option>
            </select>
          </label>

          <label className="block text-sm text-steel">
            Режим
            <select className="form-input" value={mode} onChange={(event) => setMode(event.target.value as "pdf" | "html")}>
              <option value="pdf">Генерация PDF</option>
              <option value="html">HTML-превью</option>
            </select>
          </label>

          {kind === "manometers" && mode === "pdf" ? (
            <label className="flex items-center gap-3 rounded-2xl border border-line px-4 py-3 text-sm text-ink">
              <input checked={failedMode} type="checkbox" onChange={(event) => setFailedMode(event.target.checked)} />
              Браковочный протокол
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
            БД-файл
            <input
              className="form-input"
              accept=".xlsx,.xlsm,.xls"
              type="file"
              onChange={(event) => setDbFile(event.target.files?.[0] ?? null)}
            />
          </label>

          {error ? <p className="text-sm text-[#b04c43]">{error}</p> : null}

          <button className="btn-primary w-full" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Выполняем..." : mode === "html" ? "Собрать превью" : "Запустить генерацию"}
          </button>
        </form>

        <div className="space-y-6">
          {generationResult ? (
            <section className="section-card">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="text-lg font-semibold text-ink">Результат генерации</h3>
                  <p className="mt-1 text-sm text-steel">
                    Успешно создано {generationResult.count} файлов, ошибок: {generationResult.errors.length}.
                  </p>
                </div>
              </div>

              <div className="mt-5 space-y-3">
                {generationResult.files.length ? (
                  generationResult.files.map((path) => (
                    <div key={path} className="flex flex-col gap-3 rounded-2xl border border-line px-4 py-3 md:flex-row md:items-center md:justify-between">
                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium text-ink">{basename(path)}</div>
                        <div className="mt-1 break-all text-xs text-steel">{path}</div>
                      </div>
                      <button className="btn-secondary btn-sm shrink-0" type="button" onClick={() => void openExport(path)}>
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
              </div>
              <iframe className="preview-frame mt-5" srcDoc={previewHtml} title="Предпросмотр протокола" />
            </section>
          ) : (
            <section className="section-card">
              <h3 className="text-lg font-semibold text-ink">Готовые сценарии</h3>
              <div className="mt-5 grid gap-3 md:grid-cols-2">
                <article className="tone-child rounded-3xl border border-line p-4">
                  <h4 className="text-base font-semibold text-ink">PDF-пакет</h4>
                  <p className="mt-2 text-sm text-steel">
                    Массовая генерация файлов в `exports/` с группировкой по run id и месяцу.
                  </p>
                </article>
                <article className="tone-child rounded-3xl border border-line p-4">
                  <h4 className="text-base font-semibold text-ink">HTML-превью</h4>
                  <p className="mt-2 text-sm text-steel">
                    Проверка одной строки без ожидания полного batch-процесса.
                  </p>
                </article>
              </div>
            </section>
          )}
        </div>
      </div>
    </section>
  );
}

function basename(value: string): string {
  return value.split(/[\\/]/).pop() ?? value;
}
