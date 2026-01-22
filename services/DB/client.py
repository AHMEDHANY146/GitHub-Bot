import os
from supabase import create_client, Client
from helpers.config import get_settings
from utils.logger import Logger

logger = Logger.get_logger(__name__)

class SupabaseClient:
    _instance = None
    _client: Client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._initialize_client()

    def _initialize_client(self):
        settings = get_settings()
        
        try:
            url: str = settings.SUPABASE_URL
            key: str = settings.SUPABASE_KEY
            
            if not url or not key:
                logger.error("Supabase credentials missing in configuration")
                raise ValueError("Supabase URL and Key are required")

            self._client = create_client(url, key)
            logger.info("Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    def get_client(self) -> Client:
        return self._client

# Global instance
_supabase_manager = SupabaseClient()

def get_supabase() -> Client:
    """Get the Supabase client instance"""
    return _supabase_manager.get_client()
