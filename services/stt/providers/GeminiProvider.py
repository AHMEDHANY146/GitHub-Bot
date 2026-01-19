from ..STTInterface import STTInterface
from ..STTEnums import GeminiEnums as GeminiRoleEnums
import google.generativeai as genai
import logging
import os
import tempfile
from typing import Optional
from helpers.config import get_settings


class GeminiProvider(STTInterface):
    """Gemini provider for speech-to-text and text generation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.default_generation_temperature = 0.7
        
        genai.configure(api_key=self.api_key)
        self.client = None
        self.enums = GeminiRoleEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        """Set the generation model for Gemini"""
        try:
            self.client = genai.GenerativeModel(model_id)
            self.logger.info(f"Set generation model to: {model_id}")
        except Exception as e:
            self.logger.error(f"Error setting generation model: {e}")
            raise

    def generate_text(self, prompt: str, chat_history: list[dict],
                     max_output_tokens: int=None, temperature: float = None):
        """Generate text using Gemini"""
        try:
            if not self.client:
                settings = get_settings()
                self.client = genai.GenerativeModel(settings.STT_PROVIDER_MODEL_ID)
            
            # Construct conversation
            contents = []
            
            # Add chat history
            for message in chat_history:
                contents.append(message)
            
            # Add current prompt
            contents.append(self.construct_prompt(prompt, "user"))
            
            # Generate response
            response = self.client.generate_content(contents)
            
            if response and response.candidates:
                # Handle multi-part response
                text_parts = []
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'text'):
                                text_parts.append(part.text)
                            elif hasattr(part, 'inline_data'):
                                self.logger.debug("Found inline data part in transcription response")
                    else:
                        self.logger.warning(f"Unexpected candidate structure: {candidate}")
                        # Try to extract text directly from candidate if available
                        if hasattr(candidate, 'text'):
                            text_parts.append(candidate.text)
                
                if text_parts:
                    transcribed_text = ' '.join(text_parts).strip()
                    self.logger.info(f"Successfully transcribed audio: {len(transcribed_text)} characters")
                    return transcribed_text
                else:
                    self.logger.error("No text parts found in response")
                    self.logger.debug(f"Response structure: {response}")
                    # Try to get response text directly as fallback
                    if hasattr(response, 'text'):
                        transcribed_text = response.text.strip()
                        if transcribed_text:
                            self.logger.info(f"Extracted text from response directly: {len(transcribed_text)} characters")
                            return transcribed_text
                    return None
            else:
                self.logger.error("Failed to get transcription from audio - no candidates in response")
                self.logger.debug(f"Full response: {response}")
                # Try to get response text directly as fallback
                if hasattr(response, 'text'):
                    transcribed_text = response.text.strip()
                    if transcribed_text:
                        self.logger.info(f"Extracted text from response directly: {len(transcribed_text)} characters")
                        return transcribed_text
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating text: {e}")
            return None

    def construct_prompt(self, prompt: str, role: str):
        """Construct a prompt in Gemini format"""
        return {
            "role": role,
            "parts": [{"text": prompt}]
        }

    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio file to text"""
        try:
            # Validate audio file exists
            if not os.path.exists(audio_file_path):
                self.logger.error(f"Audio file does not exist: {audio_file_path}")
                return None
            
            # Initialize client if not already done
            if not self.client:
                settings = get_settings()
                self.client = genai.GenerativeModel(settings.STT_PROVIDER_MODEL_ID)
            
            # Read audio file as bytes
            import mimetypes
            mime_type, _ = mimetypes.guess_type(audio_file_path)
            
            if not mime_type or not mime_type.startswith('audio/'):
                self.logger.warning(f"Unexpected mime type for audio file: {mime_type}")
            
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()
            
            if not audio_data:
                self.logger.error("Audio file is empty")
                return None
            
            self.logger.info(f"Processing audio file: {len(audio_data)} bytes, mime type: {mime_type}")
            
            # Create audio part for the model
            audio_part = {
                "mime_type": mime_type or "audio/ogg",
                "data": audio_data
            }
            
            # Transcribe audio with proper prompt
            response = self.client.generate_content([
                "Please transcribe this audio file accurately. Return only the transcribed text without any additional commentary or formatting.",
                audio_part
            ])
            
            if response and response.candidates:
                # Handle multi-part response
                text_parts = []
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'text'):
                                text_parts.append(part.text)
                            elif hasattr(part, 'inline_data'):
                                self.logger.debug("Found inline data part in transcription response")
                    else:
                        self.logger.warning(f"Unexpected candidate structure: {candidate}")
                        # Try to extract text directly from candidate if available
                        if hasattr(candidate, 'text'):
                            text_parts.append(candidate.text)
                
                if text_parts:
                    transcribed_text = ' '.join(text_parts).strip()
                    self.logger.info(f"Successfully transcribed audio: {len(transcribed_text)} characters")
                    return transcribed_text
                else:
                    self.logger.error("No text parts found in response")
                    self.logger.debug(f"Response structure: {response}")
                    # Try to get response text directly as fallback
                    if hasattr(response, 'text'):
                        transcribed_text = response.text.strip()
                        if transcribed_text:
                            self.logger.info(f"Extracted text from response directly: {len(transcribed_text)} characters")
                            return transcribed_text
                    return None
            else:
                self.logger.error("Failed to get transcription from audio - no candidates in response")
                self.logger.debug(f"Full response: {response}")
                # Try to get response text directly as fallback
                if hasattr(response, 'text'):
                    transcribed_text = response.text.strip()
                    if transcribed_text:
                        self.logger.info(f"Extracted text from response directly: {len(transcribed_text)} characters")
                        return transcribed_text
                return None
                
        except Exception as e:
            self.logger.error(f"Error transcribing audio file: {e}")
            # Check for specific Google AI errors
            if "quota" in str(e).lower():
                self.logger.error("API quota exceeded for Gemini")
            elif "model" in str(e).lower() and "not found" in str(e).lower():
                self.logger.error(f"Model not found: {settings.STT_PROVIDER_MODEL_ID}")
            elif "permission" in str(e).lower() or "forbidden" in str(e).lower():
                self.logger.error("Permission denied - check API key")
            return None

    def process_text(self, text: str):
        """Process and clean text"""
        return text.strip()
