from ..STTInterface import STTInterface
from groq import Groq
import logging
import os
from typing import Optional
from helpers.config import get_settings

class GroqProvider(STTInterface):
    """Groq provider for speech-to-text"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = Groq(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        self.model_id = "whisper-large-v3-turbo"

    def set_generation_model(self, model_id: str):
        """Set the transcription model for Groq"""
        self.model_id = model_id
        self.logger.info(f"Set Groq model to: {model_id}")

    def generate_text(self, prompt: str, chat_history: list[dict],
                     max_output_tokens: int=None, temperature: float = None):
        """Generate text is not supported by this provider's current integration focus"""
        self.logger.warning("generate_text called on GroqProvider, which is currently STT only.")
        return None

    def construct_prompt(self, prompt: str, role: str):
        """Construct prompt is not supported by this provider's current integration focus"""
        return {"role": role, "content": prompt}
    
    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio file using Groq's whisper model"""
        try:
            # Validate audio file exists
            if not os.path.exists(audio_file_path):
                self.logger.error(f"Audio file does not exist: {audio_file_path}")
                return None
            
            settings = get_settings()
            model = settings.STT_PROVIDER_MODEL_ID or self.model_id

            with open(audio_file_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(audio_file_path, file.read()),
                    model=model,
                    temperature=0,
                    response_format="verbose_json",
                )
                
                if hasattr(transcription, 'text'):
                    transcribed_text = transcription.text.strip()
                    self.logger.info(f"Successfully transcribed audio using Groq: {len(transcribed_text)} characters")
                    return transcribed_text
                else:
                    self.logger.error("Groq transcription response missing 'text' attribute")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error transcribing audio file with Groq: {e}")
            return None
