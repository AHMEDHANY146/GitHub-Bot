from abc import ABC, abstractmethod
from typing import Dict, Any, Optional



class LLMInterface(ABC):
    
    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass

    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list[dict],
                     max_output_tokens: int=None, temperature: float = None):
        pass
    
    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        pass
    
    @abstractmethod
    def extract_structured_data(self, text: str, schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract structured data from text following a specific schema"""
        pass



