from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Task Manager API"
    APP_ENV: str = 'development' # development | production
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "supersecretkey_replace_in_prod" # JWT in next level

    # Server Setting
    HOST: str = "0.0.0.0"
    PORT: int = 8000

settings = Settings()