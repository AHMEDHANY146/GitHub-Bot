from .STTEnums import STTEnums
from .STTInterface import STTInterface
from .providers.GeminiProvider import GeminiProvider
from .providers.GroqProvider import GroqProvider
from typing import Optional
from helpers.config import get_settings

settings = get_settings()


class STTProviderFactory:
    """Factory for creating STT providers"""
    
    @staticmethod
    def create_provider(provider: str) -> Optional[STTInterface]:
        """Create an STT provider instance"""
        
        if provider == STTEnums.GEMINI.value:
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            return GeminiProvider(api_key=api_key)
        
        elif provider == STTEnums.GROQ.value:
            api_key = settings.GROQ_API_KEY
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            return GroqProvider(api_key=api_key)

        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def get_default_provider() -> STTInterface:
        """Get the default STT provider based on available API keys"""
        
        if settings.GROQ_API_KEY:
            return STTProviderFactory.create_provider(STTEnums.GROQ.value)
        elif settings.GEMINI_API_KEY:
            return STTProviderFactory.create_provider(STTEnums.GEMINI.value)
        else:
            raise ValueError("No STT API keys found in environment variables")
