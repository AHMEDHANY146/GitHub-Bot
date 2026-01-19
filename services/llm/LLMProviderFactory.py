from .LLMEnums import LLMEnums
from .LLMInterface import LLMInterface
from .providers.CohereProvider import CohereProvider
from .providers.GeminiProvider import GeminiProvider
import os
from typing import Optional


class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    @staticmethod
    def create_provider(provider: str) -> Optional[LLMInterface]:
        """Create an LLM provider instance"""
        
        if provider == LLMEnums.COHERE.value:
            api_key = os.getenv('COHERE_API_KEY')
            if not api_key:
                raise ValueError("COHERE_API_KEY not found in environment variables")
            return CohereProvider(api_key=api_key)

        elif provider == LLMEnums.GEMINI.value:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            return GeminiProvider(api_key=api_key)

        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def get_default_provider() -> LLMInterface:
        """Get the default LLM provider based on available API keys"""
        
        # Try Gemini first, then Cohere
        if os.getenv('GEMINI_API_KEY'):
            return LLMProviderFactory.create_provider(LLMEnums.GEMINI.value)
        elif os.getenv('COHERE_API_KEY'):
            return LLMProviderFactory.create_provider(LLMEnums.COHERE.value)
        else:
            raise ValueError("No LLM API keys found in environment variables")
