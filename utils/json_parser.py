import json
import re
import logging
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

def clean_json_string(json_str: str) -> str:
    """Clean a string containing JSON from common LLM artifacts"""
    # Remove markdown code blocks
    json_str = re.sub(r'```json\s*', '', json_str)
    json_str = re.sub(r'```\s*', '', json_str)
    
    # Extract only the content between the first { and last }
    first_brace = json_str.find('{')
    last_brace = json_str.rfind('}')
    
    if first_brace != -1 and last_brace != -1:
        json_str = json_str[first_brace:last_brace + 1]
    
    return json_str.strip()

def safe_parse_json(json_str: str, model: Optional[Type[BaseModel]] = None) -> Optional[Dict[str, Any]]:
    """Safely parse JSON from LLM output, optionally validating with Pydantic"""
    if not json_str:
        return None
        
    cleaned = clean_json_string(json_str)
    
    try:
        data = json.loads(cleaned)
        
        if model:
            try:
                validated = model(**data)
                return validated.model_dump()
            except ValidationError as e:
                logger.error(f"Pydantic validation failed: {e}")
                # Log the data that failed validation
                logger.debug(f"Failed data: {data}")
                return data # Return raw data as fallback in some cases, or None? 
                           # Requirement says "fail gracefully". Let's return raw data 
                           # if it's at least valid JSON, or None if validation is mandatory.
                           # Given the bot's flow, it's better to return None and let provider handle fallback.
                return None
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode failed: {e}")
        logger.debug(f"Offending string: {cleaned}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing JSON: {e}")
        return None
