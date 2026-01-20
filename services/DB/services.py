"""
Database Services - CRUD Operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from .models import User, ReadmeSession, UserSkill, Rating
from .database import db_manager
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class UserService:
    """Service for User CRUD operations"""
    
    @staticmethod
    def get_or_create_user(telegram_id: int) -> User:
        """Get existing user or create new one"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            
            if not user:
                user = User(telegram_id=telegram_id)
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(f"Created new user: telegram_id={telegram_id}")
            
            # Detach from session to use outside
            session.expunge(user)
            return user
    
    @staticmethod
    def update_user(telegram_id: int, **kwargs) -> Optional[User]:
        """Update user information"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key) and value is not None:
                        setattr(user, key, value)
                
                session.commit()
                session.refresh(user)
                session.expunge(user)
                logger.info(f"Updated user: telegram_id={telegram_id}")
                return user
            
            return None
    
    @staticmethod
    def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                session.expunge(user)
            return user


class SessionService:
    """Service for README Session operations"""
    
    @staticmethod
    def create_session(user_id: int, raw_input_text: str = None) -> ReadmeSession:
        """Create a new README generation session"""
        with db_manager.get_session() as session:
            readme_session = ReadmeSession(
                user_id=user_id,
                raw_input_text=raw_input_text,
                status='pending'
            )
            session.add(readme_session)
            session.commit()
            session.refresh(readme_session)
            session.expunge(readme_session)
            
            logger.info(f"Created README session: id={readme_session.id}, user_id={user_id}")
            return readme_session
    
    @staticmethod
    def update_session(session_id: int, **kwargs) -> Optional[ReadmeSession]:
        """Update session data"""
        with db_manager.get_session() as session:
            readme_session = session.query(ReadmeSession).filter(ReadmeSession.id == session_id).first()
            
            if readme_session:
                for key, value in kwargs.items():
                    if hasattr(readme_session, key):
                        setattr(readme_session, key, value)
                
                session.commit()
                session.refresh(readme_session)
                session.expunge(readme_session)
                return readme_session
            
            return None
    
    @staticmethod
    def complete_session(session_id: int, generated_readme: str, structured_data: Dict[str, Any]) -> Optional[ReadmeSession]:
        """Mark session as completed with generated README"""
        return SessionService.update_session(
            session_id,
            generated_readme=generated_readme,
            structured_data=structured_data,
            status='completed',
            completed_at=datetime.utcnow()
        )
    
    @staticmethod
    def get_user_sessions(user_id: int, limit: int = 10) -> List[ReadmeSession]:
        """Get recent sessions for a user"""
        with db_manager.get_session() as session:
            sessions = session.query(ReadmeSession)\
                .filter(ReadmeSession.user_id == user_id)\
                .order_by(ReadmeSession.created_at.desc())\
                .limit(limit)\
                .all()
            
            for s in sessions:
                session.expunge(s)
            
            return sessions


class SkillService:
    """Service for User Skills operations"""
    
    @staticmethod
    def add_skills(session_id: int, skills: List[Dict[str, Any]]) -> List[UserSkill]:
        """Add multiple skills to a session"""
        with db_manager.get_session() as session:
            skill_objects = []
            
            for skill_data in skills:
                skill = UserSkill(
                    session_id=session_id,
                    skill_name=skill_data.get('name', ''),
                    category=skill_data.get('category'),
                    has_icon=skill_data.get('has_icon', False)
                )
                session.add(skill)
                skill_objects.append(skill)
            
            session.commit()
            
            for skill in skill_objects:
                session.refresh(skill)
                session.expunge(skill)
            
            logger.info(f"Added {len(skills)} skills to session {session_id}")
            return skill_objects
    
    @staticmethod
    def get_popular_skills(limit: int = 20) -> List[Dict[str, Any]]:
        """Get most popular skills across all users"""
        with db_manager.get_session() as session:
            from sqlalchemy import func
            
            results = session.query(
                UserSkill.skill_name,
                UserSkill.category,
                func.count(UserSkill.id).label('count')
            ).group_by(
                UserSkill.skill_name,
                UserSkill.category
            ).order_by(
                func.count(UserSkill.id).desc()
            ).limit(limit).all()
            
            return [
                {'skill_name': r.skill_name, 'category': r.category, 'count': r.count}
                for r in results
            ]


class RatingService:
    """Service for Rating operations"""
    
    @staticmethod
    def add_rating(user_id: int, stars: int, feedback_text: str = None, session_id: int = None) -> Rating:
        """Add a rating from user"""
        with db_manager.get_session() as session:
            rating = Rating(
                user_id=user_id,
                session_id=session_id,
                stars=stars,
                feedback_text=feedback_text
            )
            session.add(rating)
            session.commit()
            session.refresh(rating)
            session.expunge(rating)
            
            logger.info(f"Added rating: user_id={user_id}, stars={stars}")
            return rating
    
    @staticmethod
    def get_average_rating() -> float:
        """Get average rating across all users"""
        with db_manager.get_session() as session:
            from sqlalchemy import func
            
            result = session.query(func.avg(Rating.stars)).scalar()
            return float(result) if result else 0.0
    
    @staticmethod
    def get_recent_feedback(limit: int = 10) -> List[Rating]:
        """Get recent feedback with text"""
        with db_manager.get_session() as session:
            ratings = session.query(Rating)\
                .filter(Rating.feedback_text.isnot(None))\
                .order_by(Rating.created_at.desc())\
                .limit(limit)\
                .all()
            
            for r in ratings:
                session.expunge(r)
            
            return ratings
