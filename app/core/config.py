from functools import cached_property
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_FILE_PATH = Path(__file__).resolve()
APP_ROOT = CONFIG_FILE_PATH.parents[1]
PROJECT_ROOT = CONFIG_FILE_PATH.parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "metroGen API"
    APP_ENV: str = "development"
    APP_TIMEZONE: str = "Asia/Yekaterinburg"
    API_V1_PREFIX: str = "/api/v1"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8001
    API_RELOAD: bool = False
    API_LOG_LEVEL: str = "info"
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_TTL_HOURS: int = 12
    BOOTSTRAP_ADMIN_FIRST_NAME: str = "Bootstrap"
    BOOTSTRAP_ADMIN_LAST_NAME: str = "Administrator"
    BOOTSTRAP_ADMIN_PATRONYMIC: str = ""
    BOOTSTRAP_ADMIN_EMAIL: str = "admin@metrogen.local"
    BOOTSTRAP_ADMIN_PASSWORD: str = "ChangeMe123"
    FRONTEND_APP_URL: str = "http://localhost:5174"
    FRONTEND_DIST_DIR: str = "frontend/dist"
    BACKEND_CORS_ORIGINS_RAW: str = Field(
        default="http://localhost:5174",
        alias="BACKEND_CORS_ORIGINS",
    )
    ARSHIN_TIMEOUT: float = 30.0
    ARSHIN_CONCURRENCY: int = 8
    ARSHIN_RETRY_ATTEMPTS: int = 4
    ARSHIN_FAST_FAIL: bool = False
    ARSHIN_RETRY_BACKOFF_BASE: float = 0.5
    ARSHIN_RETRY_BACKOFF_MAX: float = 5.0
    ARSHIN_RETRY_JITTER: float = 0.3
    USER_AGENT: str = "arshin-fastapi/0.1"
    DATABASE_URL: str | None = None
    EXPORTS_DIR: str = "exports"  # base folder for saved files
    SIGNATURES_DIR: str = "signatures"  # base folder for signature images
    PROTOCOL_BUILD_CONCURRENCY: int = 16  # параллельная сборка контекстов
    PROTOCOL_RETRY_ATTEMPTS: int = 3  # дополнительные попытки при 429/транспортных ошибках
    PROTOCOL_RETRY_DELAY: float = 2.0  # базовая задержка между повторными попытками
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 465
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str | None = None
    SMTP_FROM_NAME: str = "metroGen Robot"

    model_config = SettingsConfigDict(
        env_file=(
            str(PROJECT_ROOT / ".env"),
            str(APP_ROOT / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @cached_property
    def backend_cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS_RAW.split(",")
            if origin.strip()
        ]

    @cached_property
    def frontend_dist_path(self) -> Path:
        return (PROJECT_ROOT / self.FRONTEND_DIST_DIR).resolve()

    @cached_property
    def exports_path(self) -> Path:
        return (PROJECT_ROOT / self.EXPORTS_DIR).resolve()

    @cached_property
    def signatures_path(self) -> Path:
        return (PROJECT_ROOT / "data" / self.SIGNATURES_DIR).resolve()


settings = Settings()
