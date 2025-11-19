from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Arshin helper API"
    ARSHIN_TIMEOUT: float = 30.0
    ARSHIN_CONCURRENCY: int = 8
    ARSHIN_RETRY_ATTEMPTS: int = 4
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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
