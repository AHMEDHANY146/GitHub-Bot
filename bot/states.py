from enum import Enum
from typing import Dict, Any, Optional
import os
from utils.language import Language



class BotState(Enum):
    """Bot conversation states"""
    START = "start"
    LANGUAGE_SELECTION = "language_selection"
    COLLECTING_INFO = "collecting_info"
    WAITING_NAME = "waiting_name"
    WAITING_GITHUB = "waiting_github"
    WAITING_LINKEDIN = "waiting_linkedin"
    WAITING_PORTFOLIO = "waiting_portfolio"
    WAITING_EMAIL = "waiting_email"
    WAITING_VOICE = "waiting_voice"
    WAITING_TEXT = "waiting_text"
    WAITING_CONTACT = "waiting_contact"
    WAITING_TECH_STACK = "waiting_tech_stack"
    PROCESSING = "processing"
    CONFIRMATION = "confirmation"
    COMPLETED = "completed"


class UserData:
    """User data container for conversation state"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.state = BotState.START
        self.data = {}
        self.temp_files = []
    
    def update_state(self, new_state: BotState):
        """Update conversation state"""
        self.state = new_state
    
    def add_data(self, key: str, value: Any):
        """Add data to user profile"""
        self.data[key] = value
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get data from user profile"""
        return self.data.get(key, default)
    
    def add_temp_file(self, file_path: str):
        """Add temporary file for cleanup"""
        self.temp_files.append(file_path)
    
    def clear_temp_files(self):
        """Clear temporary files"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception:
                pass
        self.temp_files.clear()
    
    def is_complete(self) -> bool:
        """Check if required data is complete"""
        required_fields = ['name']
        return all(field in self.data for field in required_fields)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'state': self.state.value,
            'data': self.data,
            'temp_files': self.temp_files
        }


class ConversationManager:
    """Manage user conversations and state"""
    
    def __init__(self):
        self.users: Dict[int, UserData] = {}
    
    def get_user(self, user_id: int) -> UserData:
        """Get or create user data"""
        if user_id not in self.users:
            self.users[user_id] = UserData(user_id)
        return self.users[user_id]
    
    def update_user_state(self, user_id: int, state: BotState):
        """Update user conversation state"""
        user = self.get_user(user_id)
        user.update_state(state)
    
    def add_user_data(self, user_id: int, key: str, value: Any):
        """Add data to user profile"""
        user = self.get_user(user_id)
        user.add_data(key, value)
    
    def get_user_data(self, user_id: int, key: str, default: Any = None) -> Any:
        """Get data from user profile"""
        user = self.get_user(user_id)
        return user.get_data(key, default)
    
    def get_user_language(self, user_id: int) -> Language:
        """Get user's preferred language, default to English"""
        language_code = self.get_user_data(user_id, 'language', 'en')
        return Language(language_code) if language_code in ['en', 'ar'] else Language.ENGLISH
    
    def clear_user(self, user_id: int):
        """Clear user data and cleanup"""
        if user_id in self.users:
            self.users[user_id].clear_temp_files()
            del self.users[user_id]
    
    def get_all_users(self) -> Dict[int, UserData]:
        """Get all users"""
        return self.users.copy()


# Global conversation manager instance
conversation_manager = ConversationManager()