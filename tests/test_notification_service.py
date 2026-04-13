from app.core.config import settings
from app.services.notification_service import NotificationService


def test_send_temporary_password_email_includes_frontend_app_url(monkeypatch):
    service = NotificationService()
    sent = {}

    def fake_send_message(message):
        sent["message"] = message

    monkeypatch.setattr(service, "_send_message", fake_send_message)
    monkeypatch.setattr(settings, "SMTP_FROM_EMAIL", "no-reply@mkair.ru")
    monkeypatch.setattr(settings, "SMTP_FROM_NAME", "metroGen Robot")
    monkeypatch.setattr(settings, "FRONTEND_APP_URL", "https://metrogen.mkair.crazedns.ru")

    service.send_temporary_password_email(
        recipient_email="user@example.com",
        recipient_name="Иван Иванов",
        temporary_password="Temp123456",
    )

    message = sent["message"]
    body = message.get_content()

    assert message["Subject"] == "metroGen: временный пароль"
    assert message["From"] == "metroGen Robot <no-reply@mkair.ru>"
    assert "Для вас создана учетная запись в metroGen." in body
    assert "Временный пароль: Temp123456" in body
    assert "Войти в сервис: https://metrogen.mkair.crazedns.ru" in body
    assert "После входа смените пароль в профиле." in body
