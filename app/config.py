import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Task Manager API"
    APP_ENV: str = "development"  # development | production
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "supersecretkey_replace_in_prod"  # JWT in next level

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Prometheus: Instrumentator reads ENABLE_METRICS from os.environ
    ENABLE_METRICS: bool = True


settings = Settings()

# Sync for libraries that read os.environ directly (prometheus-fastapi-instrumentator)
os.environ["ENABLE_METRICS"] = "true" if settings.ENABLE_METRICS else "false"
