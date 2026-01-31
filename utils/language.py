"""
Language management utility for bilingual support (English/Arabic)
"""

import os
import json
from enum import Enum
from typing import Dict, Any
from utils.logger import Logger


class Language(Enum):
    ENGLISH = "en"
    ARABIC = "ar"
    EGYPTIAN = "masri"


class LanguageManager:
    """Manages bilingual text support for the bot using external JSON files"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LanguageManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.logger = Logger.get_logger(__name__)
        self.translations: Dict[Language, Dict[str, str]] = {}
        self.locales_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'locales')
        self._load_translations()
        self.initialized = True
    
    def _load_translations(self):
        """Load translations from JSON files in the locales directory"""
        for lang in Language:
            file_path = os.path.join(self.locales_dir, f"{lang.value}.json")
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                    self.logger.info(f"Loaded translations for {lang.value}")
                else:
                    self.logger.warning(f"Translation file not found: {file_path}")
                    self.translations[lang] = {}
            except Exception as e:
                self.logger.error(f"Error loading translations for {lang.value}: {e}")
                self.translations[lang] = {}

    def get_text(self, key: str, language: Language = Language.ENGLISH, **kwargs) -> str:
        """Get translated text with optional string formatting"""
        try:
            # Handle string language input
            if isinstance(language, str):
                language = self.get_language_from_code(language)
                
            lang_dict = self.translations.get(language, self.translations.get(Language.ENGLISH, {}))
            text = lang_dict.get(key)
            
            # Fallback to English if key not found in requested language
            if text is None and language != Language.ENGLISH:
                text = self.translations.get(Language.ENGLISH, {}).get(key, key)
            elif text is None:
                text = key
                
            if kwargs:
                return text.format(**kwargs)
            return text
        except Exception as e:
            self.logger.error(f"Error getting translation for key '{key}': {e}")
            return key
    
    def get_language_from_code(self, language_code: Any) -> Language:
        """Convert language code string to Language enum"""
        try:
            if isinstance(language_code, Language):
                return language_code
            elif isinstance(language_code, str):
                code = language_code.lower()
                for lang in Language:
                    if lang.value == code:
                        return lang
            return Language.ENGLISH
        except Exception:
            return Language.ENGLISH


# Global instance
language_manager = LanguageManager()
