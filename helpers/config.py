from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str
    APP_VERSION: str

    TELEGRAM_BOT_TOKEN: str

    # Database
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str

    # Backends
    STT_PROVIDER_MODEL_ID: str
    GENERATION_MODEL_ID: str
    GENERATION_PROVIDER: str
    STT_PROVIDER: str

    # API Keys
    COHERE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


def get_settings() -> Settings:
    return Settings()
