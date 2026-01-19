from ..LLMInterface import LLMInterface
from ..LLMEnums import GeminiEnums as GeminiRoleEnums
import google.generativeai as genai
import logging
import json
from typing import Dict, Any, Optional
from helpers.config import get_settings


class GeminiProvider(LLMInterface):
    """Gemini provider for LLM operations"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.default_generation_temperature = 0.7
        self.default_output_max_tokens = 8192
        
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
                self.client = genai.GenerativeModel(settings.GENERATION_MODEL_ID)
            
            # Construct conversation
            contents = []
            
            # Add chat history
            for message in chat_history:
                contents.append(message)
            
            # Add current prompt
            contents.append(self.construct_prompt(prompt, "user"))
            
            # Generate response
            response = self.client.generate_content(contents)
            
            if response and hasattr(response, 'text') and response.text:
                return response.text
            else:
                self.logger.error("Failed to get text response")
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

    def extract_structured_data(self, text: str, schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract structured data from text following a specific schema"""
        try:
            if not self.client:
                settings = get_settings()
                self.client = genai.GenerativeModel(settings.GENERATION_MODEL_ID)
            
            # Create prompt for structured data extraction
            prompt = f"""
Extract the following information from the text and return it as a JSON object with this exact structure:
{json.dumps(schema, indent=2)}

Text to analyze:
{text}

IMPORTANT: Return ONLY the JSON object. No markdown formatting, no explanations, just the raw JSON.
"""
            
            response = self.client.generate_content(prompt)
            
            if response and hasattr(response, 'text') and response.text:
                # Clean the response to extract JSON
                response_text = response.text.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON response: {e}")
                    self.logger.error(f"Raw response: {response_text}")
                    return None
            else:
                self.logger.error("Failed to get structured data response")
                return None
                
        except Exception as e:
            self.logger.error(f"Error extracting structured data: {e}")
            return None

