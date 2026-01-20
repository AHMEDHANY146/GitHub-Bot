"""
Database Models for GitHub README Bot
Using SQLAlchemy ORM with PostgreSQL
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model - stores Telegram user information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    github_username = Column(String(50), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    portfolio_url = Column(String(255), nullable=True)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = relationship("ReadmeSession", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, name='{self.name}')>"


class ReadmeSession(Base):
    """README Generation Session - stores each README creation attempt"""
    __tablename__ = 'readme_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Input data
    raw_input_text = Column(Text, nullable=True)  # Voice transcription or text input
    
    # Extracted structured data (stored as JSON)
    structured_data = Column(JSON, nullable=True)
    
    # Generated output
    generated_readme = Column(Text, nullable=True)
    
    # Session status: 'pending', 'processing', 'completed', 'cancelled'
    status = Column(String(20), default='pending')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    skills = relationship("UserSkill", back_populates="session", cascade="all, delete-orphan")
    rating = relationship("Rating", back_populates="session", uselist=False)
    
    def __repr__(self):
        return f"<ReadmeSession(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


class UserSkill(Base):
    """User Skills extracted from README sessions"""
    __tablename__ = 'user_skills'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('readme_sessions.id', ondelete='CASCADE'), nullable=False)
    
    skill_name = Column(String(100), nullable=False)
    # Category: 'programming_language', 'framework', 'tool', 'database', 'cloud', 'other'
    category = Column(String(50), nullable=True)
    has_icon = Column(Boolean, default=False)
    
    # Relationships
    session = relationship("ReadmeSession", back_populates="skills")
    
    def __repr__(self):
        return f"<UserSkill(skill_name='{self.skill_name}', category='{self.category}')>"


class Rating(Base):
    """User Ratings and Feedback"""
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_id = Column(Integer, ForeignKey('readme_sessions.id', ondelete='SET NULL'), nullable=True)
    
    stars = Column(Integer, nullable=False)  # 1-5 stars
    feedback_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    session = relationship("ReadmeSession", back_populates="rating")
    
    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, stars={self.stars})>"
