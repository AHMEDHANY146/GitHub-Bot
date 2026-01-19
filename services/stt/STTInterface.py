from abc import ABC, abstractmethod
from typing import Optional



class STTInterface(ABC):
    
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
    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio file to text"""
        pass



