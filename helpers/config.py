from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str
    APP_VERSION: str

    TELEGRAM_BOT_TOKEN: str

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
