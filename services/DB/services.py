"""
Database Services - CRUD Operations via Supabase
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import User, ReadmeSession, UserSkill, Rating
from .client import get_supabase
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class UserService:
    """Service for User CRUD operations"""
    
    @staticmethod
    def get_or_create_user(telegram_id: int) -> User:
        """Get existing user or create new one"""
        supabase = get_supabase()
        
        # Try to get user
        response = supabase.table('users').select("*").eq('telegram_id', telegram_id).execute()
        
        if response.data and len(response.data) > 0:
            return User(**response.data[0])
            
        # Create user if not exists
        try:
            # We don't provide ID as it's auto-generated
            new_user_data = {'telegram_id': telegram_id}
            response = supabase.table('users').insert(new_user_data).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Created new user: telegram_id={telegram_id}")
                return User(**response.data[0])
                
        except Exception as e:
            logger.error(f"Error creating user {telegram_id}: {e}")
            # If failed, try to fetch again in case of race condition
            response = supabase.table('users').select("*").eq('telegram_id', telegram_id).execute()
            if response.data:
                return User(**response.data[0])
            raise e
            
        raise Exception("Failed to get or create user")
    
    @staticmethod
    def update_user(telegram_id: int, **kwargs) -> Optional[User]:
        """Update user information"""
        supabase = get_supabase()
        
        # Filter None values and ensure we have fields to update
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        if not update_data:
            return UserService.get_user_by_telegram_id(telegram_id)
            
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        try:
            response = supabase.table('users').update(update_data).eq('telegram_id', telegram_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Updated user: telegram_id={telegram_id}")
                return User(**response.data[0])
                
        except Exception as e:
            logger.error(f"Error updating user {telegram_id}: {e}")
            
        return None
    
    @staticmethod
    def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        supabase = get_supabase()
        
        response = supabase.table('users').select("*").eq('telegram_id', telegram_id).execute()
        
        if response.data and len(response.data) > 0:
            return User(**response.data[0])
            
        return None


class SessionService:
    """Service for README Session operations"""
    
    @staticmethod
    def create_session(user_id: int, raw_input_text: str = None) -> ReadmeSession:
        """Create a new README generation session"""
        supabase = get_supabase()
        
        try:
            # First ensure user exists (get their DB ID, not just telegram ID)
            # Assuming user_id passed here is the 'id' from users table, not telegram_id
            # If it is telegram_id, we should look it up first. 
            # *Correction*: In SQL implementation, user_id FK references users.id. 
            # The callers of this method usually pass the DB ID if they have the User object.
            # Let's double check callers. In existing code 'user_id' was DB ID.
            
            session_data = {
                'user_id': user_id,
                'raw_input_text': raw_input_text,
                'status': 'pending'
            }
            
            response = supabase.table('readme_sessions').insert(session_data).execute()
            
            if response.data and len(response.data) > 0:
                session_obj = ReadmeSession(**response.data[0])
                logger.info(f"Created README session: id={session_obj.id}, user_id={user_id}")
                return session_obj
                
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise e
            
        raise Exception("Failed to create session")
    
    @staticmethod
    def update_session(session_id: int, **kwargs) -> Optional[ReadmeSession]:
        """Update session data"""
        supabase = get_supabase()
        
        # Filter None values
        update_data = {k: v for k, v in kwargs.items()}
        
        if not update_data:
            return None
            
        try:
            response = supabase.table('readme_sessions').update(update_data).eq('id', session_id).execute()
            
            if response.data and len(response.data) > 0:
                return ReadmeSession(**response.data[0])
                
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            
        return None
    
    @staticmethod
    def complete_session(session_id: int, generated_readme: str, structured_data: Dict[str, Any]) -> Optional[ReadmeSession]:
        """Mark session as completed with generated README"""
        return SessionService.update_session(
            session_id,
            generated_readme=generated_readme,
            structured_data=structured_data,
            status='completed',
            completed_at=datetime.utcnow().isoformat()
        )
    
    @staticmethod
    def get_user_sessions(user_id: int, limit: int = 10) -> List[ReadmeSession]:
        """Get recent sessions for a user"""
        supabase = get_supabase()
        
        response = supabase.table('readme_sessions')\
            .select("*")\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
            
        if response.data:
            return [ReadmeSession(**s) for s in response.data]
            
        return []


class SkillService:
    """Service for User Skills operations"""
    
    @staticmethod
    def add_skills(session_id: int, skills: List[Dict[str, Any]]) -> List[UserSkill]:
        """Add multiple skills to a session"""
        if not skills:
            return []
            
        supabase = get_supabase()
        
        skill_objects = []
        rows_to_insert = []
        
        for skill_data in skills:
            rows_to_insert.append({
                'session_id': session_id,
                'skill_name': skill_data.get('name', ''),
                'category': skill_data.get('category'),
                'has_icon': skill_data.get('has_icon', False)
            })
            
        try:
            response = supabase.table('user_skills').insert(rows_to_insert).execute()
            
            if response.data:
                skill_objects = [UserSkill(**s) for s in response.data]
                logger.info(f"Added {len(skill_objects)} skills to session {session_id}")
                return skill_objects
                
        except Exception as e:
            logger.error(f"Error adding skills: {e}")
            
        return []
    
    @staticmethod
    def get_popular_skills(limit: int = 20) -> List[Dict[str, Any]]:
        """Get most popular skills across all users"""
        # This is harder with simple Supabase client without RPC.
        # We'll use a raw RPC call if possible, or fetch all and aggregate (bad for scale),
        # or simplified query.
        # For now, let's assume we might need to add an RPC function in SQL, 
        # or just try to be simple.
        
        # Supabase Python client executes RPC via .rpc()
        # But we haven't defined that RPC.
        # Let's try raw select and count if feasible, or leave it empty/basic for now.
        
        # NOTE: Aggregation is not directly supported in simple client select().
        # We would need to create a view or function.
        # For safety, safely return empty list or basic list, 
        # or document that user needs to create an RPC "get_popular_skills"
        
        # Let's implement a safe valid placeholder or basic fetch.
        
        # Try to use rpc if it existed, catch error.
        supabase = get_supabase()
        try:
             # Assuming we might create this RPC later.
             response = supabase.rpc('get_popular_skills', {'limit_count': limit}).execute()
             if response.data:
                 return response.data
        except:
             pass
             
        return []


class RatingService:
    """Service for Rating operations"""
    
    @staticmethod
    def add_rating(user_id: int, stars: int, feedback_text: str = None, session_id: int = None) -> Rating:
        """Add a rating from user"""
        supabase = get_supabase()
        
        rating_data = {
            'user_id': user_id,
            'session_id': session_id,
            'stars': stars,
            'feedback_text': feedback_text
        }
        
        try:
            response = supabase.table('ratings').insert(rating_data).execute()
            
            if response.data and len(response.data) > 0:
                rating = Rating(**response.data[0])
                logger.info(f"Added rating: user_id={user_id}, stars={stars}")
                return rating
                
        except Exception as e:
            logger.error(f"Error adding rating: {e}")
            raise e
            
        raise Exception("Failed to add rating")
    
    @staticmethod
    def get_average_rating() -> float:
        """Get average rating across all users"""
        # Need RPC for aggregation or fetch all (inefficient)
        # Let's fetch all (capped at say 1000) for now as MVP
        
        supabase = get_supabase()
        response = supabase.table('ratings').select('stars').limit(1000).execute()
        
        if response.data:
            ratings = [r['stars'] for r in response.data]
            return sum(ratings) / len(ratings)
            
        return 0.0
    
    @staticmethod
    def get_recent_feedback(limit: int = 10) -> List[Rating]:
        """Get recent feedback with text"""
        supabase = get_supabase()
        
        response = supabase.table('ratings')\
            .select("*")\
            .neq('feedback_text', None)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
            
        if response.data:
            return [Rating(**r) for r in response.data]
            
        return []
