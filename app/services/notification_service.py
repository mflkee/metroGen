from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings


class NotificationConfigurationError(RuntimeError):
    pass


class NotificationDeliveryError(RuntimeError):
    pass


class NotificationService:
    def is_configured(self) -> bool:
        return bool(settings.SMTP_HOST and settings.SMTP_FROM_EMAIL)

    def send_test_email(self, *, recipient_email: str, recipient_name: str) -> None:
        message = EmailMessage()
        message["Subject"] = "metroGen: тестовое письмо"
        message["From"] = self._from_header()
        message["To"] = recipient_email
        message.set_content(
            f"{recipient_name},\n\n"
            "SMTP в metroGen настроен и это тестовое письмо доставлено успешно.\n"
        )
        self._send_message(message)

    def send_temporary_password_email(
        self,
        *,
        recipient_email: str,
        recipient_name: str,
        temporary_password: str,
    ) -> None:
        message = EmailMessage()
        message["Subject"] = "metroGen: временный пароль"
        message["From"] = self._from_header()
        message["To"] = recipient_email
        app_url = settings.FRONTEND_APP_URL.strip()
        login_hint = f"Войти в сервис: {app_url}\n\n" if app_url else ""
        message.set_content(
            f"{recipient_name},\n\n"
            "Для вас создана учетная запись в metroGen.\n"
            f"Временный пароль: {temporary_password}\n\n"
            f"{login_hint}"
            "После входа смените пароль в профиле."
        )
        self._send_message(message)

    def _from_header(self) -> str:
        if not settings.SMTP_FROM_EMAIL:
            raise NotificationConfigurationError("SMTP_FROM_EMAIL is not configured.")
        from_name = settings.SMTP_FROM_NAME.strip()
        if not from_name:
            return settings.SMTP_FROM_EMAIL
        return f"{from_name} <{settings.SMTP_FROM_EMAIL}>"

    def _send_message(self, message: EmailMessage) -> None:
        if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
            raise NotificationConfigurationError(
                "SMTP is not configured. Set SMTP_HOST and SMTP_FROM_EMAIL."
            )

        try:
            if settings.SMTP_PORT == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(
                    settings.SMTP_HOST,
                    settings.SMTP_PORT,
                    context=context,
                    timeout=20,
                ) as smtp:
                    self._login_if_needed(smtp)
                    smtp.send_message(message)
            else:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as smtp:
                    smtp.ehlo()
                    try:
                        smtp.starttls(context=ssl.create_default_context())
                        smtp.ehlo()
                    except smtplib.SMTPException:
                        pass
                    self._login_if_needed(smtp)
                    smtp.send_message(message)
        except OSError as exc:
            raise NotificationDeliveryError(f"SMTP delivery failed: {exc}") from exc
        except smtplib.SMTPException as exc:
            raise NotificationDeliveryError(f"SMTP delivery failed: {exc}") from exc

    def _login_if_needed(self, smtp: smtplib.SMTP) -> None:
        if settings.SMTP_USERNAME:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD or "")
