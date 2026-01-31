from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str
    APP_VERSION: str

    TELEGRAM_BOT_TOKEN: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Backends
    STT_PROVIDER_MODEL_ID: str
    GENERATION_MODEL_ID: str
    GENERATION_PROVIDER: str
    STT_PROVIDER: str

    # API Keys
    COHERE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Developer
    DEVELOPER_CHAT_ID: Optional[int] = None

    model_config = SettingsConfigDict(
        env_file=f"{__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__)))}/.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
