from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Arshin helper API"
    ARSHIN_TIMEOUT: int = 30
    ARSHIN_CONCURRENCY: int = 8
    USER_AGENT: str = "arshin-fastapi/0.1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
