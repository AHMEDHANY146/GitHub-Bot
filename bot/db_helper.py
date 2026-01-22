"""
Database Helper Functions for Bot Handlers
Provides easy-to-use functions to save data to database
"""

from typing import Optional, Dict, Any, List
from utils.logger import Logger

logger = Logger.get_logger(__name__)

# Flag to track if database is available
_db_available = False

try:
    from services.DB import UserService, SessionService, SkillService, RatingService
    _db_available = True
except ImportError:
    logger.warning("Database services not available - running without database")


def is_db_available() -> bool:
    """Check if database is available"""
    return _db_available


def save_user(telegram_id: int, **kwargs) -> Optional[int]:
    """
    Save or update user in database
    
    Args:
        telegram_id: Telegram user ID
        **kwargs: User fields (name, github_username, linkedin_url, portfolio_url, email)
    
    Returns:
        User database ID or None if database unavailable
    """
    if not _db_available:
        return None
    
    try:
        # Get or create user
        user = UserService.get_or_create_user(telegram_id)
        
        # Update with provided data
        if kwargs:
            user = UserService.update_user(telegram_id, **kwargs)
        
        logger.info(f"Saved user to database: telegram_id={telegram_id}")
        return user.id if user else None
        
    except Exception as e:
        logger.error(f"Error saving user to database: {e}")
        return None


def create_readme_session(telegram_id: int, raw_input_text: str = None) -> Optional[int]:
    """
    Create a new README session for user
    
    Args:
        telegram_id: Telegram user ID
        raw_input_text: Voice transcription or text input
    
    Returns:
        Session ID or None if failed
    """
    if not _db_available:
        return None
    
    try:
        # Get user ID first
        user = UserService.get_user_by_telegram_id(telegram_id)
        if not user:
            user = UserService.get_or_create_user(telegram_id)
        
        # Create session
        session = SessionService.create_session(user.id, raw_input_text)
        logger.info(f"Created README session: id={session.id}")
        return session.id
        
    except Exception as e:
        logger.error(f"Error creating README session: {e}")
        return None


def complete_readme_session(session_id: int, generated_readme: str, structured_data: Dict[str, Any], skills: List[str] = None) -> bool:
    """
    Complete a README session with generated content
    
    Args:
        session_id: Session database ID
        generated_readme: Generated README content
        structured_data: Extracted structured data
        skills: List of skill names
    
    Returns:
        True if successful
    """
    if not _db_available or not session_id:
        return False
    
    try:
        # Update session with generated content
        SessionService.complete_session(session_id, generated_readme, structured_data)
        
        # Save skills if provided
        if skills:
            skill_data = []
            for skill in skills:
                skill_data.append({
                    'name': skill,
                    'category': _categorize_skill(skill),
                    'has_icon': True  # Assuming skills with icons were already filtered
                })
            SkillService.add_skills(session_id, skill_data)
        
        logger.info(f"Completed README session: id={session_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error completing README session: {e}")
        return False


def save_rating(telegram_id: int, stars: int, feedback_text: str = None, session_id: int = None) -> bool:
    """
    Save user rating
    
    Args:
        telegram_id: Telegram user ID
        stars: Rating 1-5
        feedback_text: Optional feedback text
        session_id: Optional session ID
    
    Returns:
        True if successful
    """
    if not _db_available:
        return False
    
    try:
        # Get user ID
        user = UserService.get_user_by_telegram_id(telegram_id)
        if not user:
            logger.warning(f"User not found for rating: telegram_id={telegram_id}")
            return False
        
        # Save rating
        RatingService.add_rating(user.id, stars, feedback_text, session_id)
        logger.info(f"Saved rating: user_id={user.id}, stars={stars}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving rating: {e}")
        return False


def _categorize_skill(skill: str) -> str:
    """Categorize a skill for analytics"""
    skill_lower = skill.lower()
    
    programming_keywords = ['python', 'javascript', 'java', 'c++', 'c#', 'typescript', 'go', 'rust', 'php', 'swift', 'kotlin', 'ruby']
    framework_keywords = ['react', 'vue', 'angular', 'django', 'flask', 'spring', 'express', 'laravel']
    database_keywords = ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite']
    cloud_keywords = ['aws', 'azure', 'gcp', 'docker', 'kubernetes']
    
    if any(kw in skill_lower for kw in programming_keywords):
        return 'programming_language'
    elif any(kw in skill_lower for kw in framework_keywords):
        return 'framework'
    elif any(kw in skill_lower for kw in database_keywords):
        return 'database'
    elif any(kw in skill_lower for kw in cloud_keywords):
        return 'cloud'
    else:
        return 'other'


def get_user(telegram_id: int) -> Optional[dict]:
    """
    Get user data from database by Telegram ID
    
    Args:
        telegram_id: Telegram user ID
    
    Returns:
        Dictionary with user data or None if not found
    """
    if not _db_available:
        return None
    
    try:
        user = UserService.get_user_by_telegram_id(telegram_id)
        if user:
            # Use model_dump to convert to dict, but ensure we return specific fields expected by legacy code
            # Or better, just return the relevant fields or the whole dump
            user_dict = user.model_dump()
            
            # Map newer fields to keys expected by legacy code if needed, 
            # though get_user users seem to expect keys: telegram_id, name, github, linkedin, portfolio, email
            # Our model already has snake_case fields matching DB.
            return {
                'id': user.id,
                'telegram_id': user.telegram_id,
                'name': user.name,
                'github': user.github_username,
                'linkedin': user.linkedin_url,
                'portfolio': user.portfolio_url,
                'email': user.email,
                'state': user.state,
                'data': user.data
            }
        return None
        
    except Exception as e:
        logger.error(f"Error getting user from database: {e}")
        return None


def update_user_state(telegram_id: int, state: str, data: Dict[str, Any] = None) -> bool:
    """
    Update user state and data in database
    
    Args:
        telegram_id: Telegram user ID
        state: New state string
        data: User data dictionary
    
    Returns:
        True if successful
    """
    if not _db_available:
        return False
        
    try:
        UserService.update_user(telegram_id, state=state, data=data)
        return True
    except Exception as e:
        logger.error(f"Error updating user state: {e}")
        return False


def get_user_state(telegram_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user state and data from database
    
    Args:
        telegram_id: Telegram user ID
    
    Returns:
        Dict with state and data, or None
    """
    if not _db_available:
        return None
        
    try:
        user = UserService.get_user_by_telegram_id(telegram_id)
        if user:
            return {
                'state': user.state,
                'data': user.data
            }
        return None
    except Exception as e:
        logger.error(f"Error getting user state: {e}")
        return None
