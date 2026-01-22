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
    WAITING_GITHUB_TOKEN = "waiting_github_token"
    COMPLETED = "completed"


class UserData:
    """User data container for conversation state"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.state = BotState.START
        self.data = {}
        self.temp_files = []
        self._dirty = False  # Track if needs saving
    
    def update_state(self, new_state: BotState):
        """Update conversation state"""
        self.state = new_state
        self._dirty = True
        self.save()
    
    def add_data(self, key: str, value: Any):
        """Add data to user profile"""
        self.data[key] = value
        self._dirty = True
        self.save()
    
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
        
    def save(self):
        """Save state to database"""
        try:
            from bot.db_helper import update_user_state
            # Convert enum to string
            state_str = self.state.value if isinstance(self.state, BotState) else str(self.state)
            update_user_state(self.user_id, state_str, self.data)
            self._dirty = False
        except Exception as e:
            # logger might not be imported here to avoid circular imports
            print(f"Error saving user state: {e}")

    @classmethod
    def from_db(cls, user_id: int, state_str: str, data: dict):
        """Create UserData from DB record"""
        instance = cls(user_id)
        if state_str:
            try:
                instance.state = BotState(state_str)
            except ValueError:
                instance.state = BotState.START
        if data:
            instance.data = data
        return instance


class ConversationManager:
    """Manage user conversations and state with DB persistence"""
    
    def __init__(self):
        self.users: Dict[int, UserData] = {}
        # Simple LRU-like cache or just trusted local cache
    
    def get_user(self, user_id: int) -> UserData:
        """Get or create user data (loads from DB if not in memory)"""
        # 1. Check memory
        if user_id in self.users:
            return self.users[user_id]
            
        # 2. Try load from DB
        try:
            from bot.db_helper import get_user_state
            db_state = get_user_state(user_id)
            
            if db_state:
                # Reconstruct user from DB
                user = UserData.from_db(user_id, db_state.get('state'), db_state.get('data'))
                self.users[user_id] = user
                return user
        except ImportError:
            pass # DB helper might not be ready
        except Exception as e:
            print(f"Error loading user from DB: {e}")
            
        # 3. Create new if not found
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
        try:
            return Language(language_code)
        except ValueError:
            return Language.ENGLISH
    
    def clear_user(self, user_id: int):
        """Clear user data and cleanup (resets to start in DB too)"""
        if user_id in self.users:
            self.users[user_id].clear_temp_files()
            # Don't delete from memory entirely, just reset state
            user = self.users[user_id]
            user.state = BotState.START
            user.data = {}
            user.save()
            # Optional: del self.users[user_id] to free memory, but keeping it is fine for active users
    
    def get_all_users(self) -> Dict[int, UserData]:
        """Get all active in-memory users"""
        return self.users.copy()


# Global conversation manager instance
conversation_manager = ConversationManager()