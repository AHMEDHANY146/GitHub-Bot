from ..LLMInterface import LLMInterface
from ..LLMEnums import CohereEnums as CohereRoleEnums
import cohere
import logging
import json
from typing import Dict, Any, Optional


class CohereProvider(LLMInterface):
    """Cohere provider for LLM operations"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.default_generation_temperature = 0.7
        self.default_output_max_tokens = 8192
        
        self.client = cohere.Client(api_key=self.api_key)
        self.enums = CohereRoleEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        """Set the generation model for Cohere"""
        try:
            self.generation_model_id = model_id
            self.logger.info(f"Set generation model to: {model_id}")
        except Exception as e:
            self.logger.error(f"Error setting generation model: {e}")
            raise

    def generate_text(self, prompt: str, chat_history: list[dict],
                     max_output_tokens: int=None, temperature: float = None):
        """Generate text using Cohere"""
        try:
            if not self.client:
                raise ValueError("Cohere client not initialized")
            
            if not hasattr(self, 'generation_model_id'):
                self.generation_model_id = 'command'
            
            max_output_tokens = max_output_tokens if max_output_tokens else self.default_output_max_tokens
            temperature = temperature if temperature else self.default_generation_temperature
            
            response = self.client.chat(
                model=self.generation_model_id,
                message=prompt,
                temperature=temperature,
                max_tokens=max_output_tokens
            )
            
            if response and hasattr(response, 'text') and response.text:
                return response.text
            else:
                self.logger.error("Failed to get text response")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating text: {e}")
            return None

    def construct_prompt(self, prompt: str, role: str):
        """Construct a prompt in Cohere format"""
        return {
            "role": role,
            "message": prompt
        }

    def extract_structured_data(self, text: str, schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract structured data from text following a specific schema"""
        try:
            if not self.client:
                raise ValueError("Cohere client not initialized")
            
            if not hasattr(self, 'generation_model_id'):
                self.generation_model_id = 'command'
            
            # Create prompt for structured data extraction
            prompt = f"""
Extract the following information from the text and return it as a JSON object with this exact structure:
{json.dumps(schema, indent=2)}

Text to analyze:
{text}

IMPORTANT: Return ONLY the JSON object. No markdown formatting, no explanations, just the raw JSON.
"""
            
            response = self.client.chat(
                model=self.generation_model_id,
                message=prompt,
                temperature=0.1  # Lower temperature for structured data
            )
            
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
      

