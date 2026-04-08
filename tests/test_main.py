from app import main
from app.core.config import settings


def test_run_uses_env_backed_server_settings(monkeypatch):
    called = {}

    def fake_run(app_path, **kwargs):
        called["app_path"] = app_path
        called["kwargs"] = kwargs

    monkeypatch.setattr(main.uvicorn, "run", fake_run)
    monkeypatch.setattr(settings, "API_HOST", "127.0.0.1")
    monkeypatch.setattr(settings, "API_PORT", 18000)
    monkeypatch.setattr(settings, "API_RELOAD", False)
    monkeypatch.setattr(settings, "API_LOG_LEVEL", "info")

    main.run()

    assert called["app_path"] == "app.main:app"
    assert called["kwargs"] == {
        "host": "127.0.0.1",
        "port": 18000,
        "reload": False,
        "log_level": "info",
    }
