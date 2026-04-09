import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <main className="auth-layout">
      <section className="auth-panel space-y-4">
        <h1 className="text-2xl font-semibold text-ink">Страница не найдена</h1>
        <p className="text-sm text-steel">
          Такой записи в metroGen нет. Вернитесь на главную или откройте генерацию.
        </p>
        <div className="flex gap-3">
          <Link className="btn-primary" to="/dashboard">Главная</Link>
          <Link className="btn-secondary" to="/generation">Генерация</Link>
        </div>
      </section>
    </main>
  );
}
