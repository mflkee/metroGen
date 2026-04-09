import { PageHeader } from "@/components/layout/PageHeader";

export function HelpPage() {
  return (
    <section>
      <PageHeader
        title="Документация"
        description="Короткая памятка по базовым сценариям metroGen через новый интерфейс."
      />
      <div className="grid gap-4 lg:grid-cols-3">
        <article className="section-card">
          <h3 className="text-lg font-semibold text-ink">1. Генерация PDF</h3>
          <p className="mt-3 text-sm leading-6 text-steel">
            Откройте «Генерация», выберите тип прибора, загрузите основной файл и, при необходимости, БД-файл. После запуска готовые PDF сохраняются в `exports/` и доступны для открытия прямо из интерфейса.
          </p>
        </article>
        <article className="section-card">
          <h3 className="text-lg font-semibold text-ink">2. HTML-превью</h3>
          <p className="mt-3 text-sm leading-6 text-steel">
            Для проверки одной строки переключите режим на HTML-превью и задайте номер строки. Это ускоряет проверку шаблонов без ожидания полного пакетного рендера.
          </p>
        </article>
        <article className="section-card">
          <h3 className="text-lg font-semibold text-ink">3. Пользователи и темы</h3>
          <p className="mt-3 text-sm leading-6 text-steel">
            Администраторы и разработчики управляют пользователями в разделе «Пользователи». Тема, доступные оформления и SMTP-проверка находятся в «Настройках».
          </p>
        </article>
      </div>
    </section>
  );
}
