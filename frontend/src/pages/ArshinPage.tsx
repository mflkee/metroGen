import { FormEvent, useState } from "react";

import { fetchVriDetails, resolveVriId } from "@/api/arshin";
import { PageHeader } from "@/components/layout/PageHeader";

export function ArshinPage() {
  const [certificate, setCertificate] = useState("");
  const [vriId, setVriId] = useState("");
  const [resolvedVriId, setResolvedVriId] = useState<string | null>(null);
  const [details, setDetails] = useState<Record<string, unknown> | null>(null);
  const [etalonLine, setEtalonLine] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleResolveCertificate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsLoading(true);
    setDetails(null);

    try {
      const result = await resolveVriId(certificate);
      setResolvedVriId(result.vriId);
      setVriId(result.vriId ?? "");
    } catch (lookupError) {
      setError(lookupError instanceof Error ? lookupError.message : "Не удалось выполнить поиск.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleLoadDetails(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const result = await fetchVriDetails(vriId);
      setResolvedVriId(result.vriId);
      setEtalonLine(result.etalonLine);
      setDetails(result.result);
    } catch (lookupError) {
      setError(lookupError instanceof Error ? lookupError.message : "Не удалось получить детали.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section>
      <PageHeader
        title="Аршин"
        description="Вспомогательная диагностическая панель для работы с номером свидетельства, vri_id и сырыми деталями поверки."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        <form className="section-card space-y-4" onSubmit={handleResolveCertificate}>
          <div>
            <h3 className="text-lg font-semibold text-ink">Поиск по свидетельству</h3>
            <p className="mt-1 text-sm text-steel">
              Быстрый способ проверить, находит ли backend `vri_id` для конкретного сертификата.
            </p>
          </div>
          <label className="block text-sm text-steel">
            Номер свидетельства
            <input className="form-input" type="text" value={certificate} onChange={(event) => setCertificate(event.target.value)} />
          </label>
          <button className="btn-primary" disabled={isLoading} type="submit">
            {isLoading ? "Ищем..." : "Найти vri_id"}
          </button>
          {resolvedVriId !== null ? (
            <div className="rounded-2xl border border-line px-4 py-3 text-sm">
              <div className="text-steel">Результат поиска</div>
              <div className="mt-1 font-semibold text-ink">{resolvedVriId || "Не найден"}</div>
            </div>
          ) : null}
        </form>

        <form className="section-card space-y-4" onSubmit={handleLoadDetails}>
          <div>
            <h3 className="text-lg font-semibold text-ink">Детали по vri_id</h3>
            <p className="mt-1 text-sm text-steel">
              Загружает краткий payload из backend и показывает строку эталона, которую он собрал.
            </p>
          </div>
          <label className="block text-sm text-steel">
            vri_id
            <input className="form-input" type="text" value={vriId} onChange={(event) => setVriId(event.target.value)} />
          </label>
          <button className="btn-secondary" disabled={isLoading} type="submit">
            {isLoading ? "Загружаем..." : "Получить детали"}
          </button>
          {etalonLine ? (
            <div className="rounded-2xl border border-line px-4 py-3 text-sm">
              <div className="text-steel">Строка эталона</div>
              <div className="mt-1 font-medium text-ink">{etalonLine}</div>
            </div>
          ) : null}
        </form>
      </div>

      {error ? <p className="mt-5 text-sm text-[#b04c43]">{error}</p> : null}

      {details ? (
        <section className="section-card mt-6">
          <h3 className="text-lg font-semibold text-ink">Сырой payload</h3>
          <pre className="mt-4 overflow-x-auto rounded-3xl border border-line p-4 text-xs text-ink">
            {JSON.stringify(details, null, 2)}
          </pre>
        </section>
      ) : null}
    </section>
  );
}
