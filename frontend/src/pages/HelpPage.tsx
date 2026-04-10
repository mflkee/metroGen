import { PageHeader } from "@/components/layout/PageHeader";

export function HelpPage() {
  return (
    <section>
      <PageHeader
        title="Документация"
        description="Короткая памятка по обновлённым рабочим зонам metroGen."
      />
      <div className="grid gap-4 lg:grid-cols-3">
        <article className="section-card">
          <h3 className="text-lg font-semibold text-ink">1. Генерация</h3>
          <p className="mt-3 text-sm leading-6 text-steel">
            Во вкладке «Генерация» выберите тип прибора, загрузите основной файл и при необходимости
            реестр. Для batch-режима интерфейс покажет этапы процесса и сразу предложит ZIP по всей
            run-папке.
          </p>
        </article>
        <article className="section-card">
          <h3 className="text-lg font-semibold text-ink">2. База данных</h3>
          <p className="mt-3 text-sm leading-6 text-steel">
            Во вкладке «База данных» можно отдельно загрузить выгрузку реестра, проверить количество
            активных строк, владельцев, методик и вспомогательных СИ до запуска самой генерации.
          </p>
        </article>
        <article className="section-card">
          <h3 className="text-lg font-semibold text-ink">3. Готовые генерации</h3>
          <p className="mt-3 text-sm leading-6 text-steel">
            Во вкладке «Готовые генерации» лежит архив последних run-папок. Оттуда можно скачать ZIP целиком
            или открыть конкретный PDF без перехода в файловую систему.
          </p>
        </article>
      </div>
    </section>
  );
}
