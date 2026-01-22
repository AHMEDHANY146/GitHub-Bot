"""
Database Models for GitHub README Bot
Using Pydantic for data validation (Supabase)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class User(BaseModel):
    """User model - stores Telegram user information"""
    id: Optional[int] = None
    telegram_id: int
    name: Optional[str] = None
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    email: Optional[str] = None
    
    # Conversation State Persistence
    state: Optional[str] = None
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ReadmeSession(BaseModel):
    """README Generation Session - stores each README creation attempt"""
    id: Optional[int] = None
    user_id: int
    
    # Input data
    raw_input_text: Optional[str] = None
    
    # Extracted structured data (stored as JSON)
    structured_data: Optional[Dict[str, Any]] = None
    
    # Generated output
    generated_readme: Optional[str] = None
    
    # Session status: 'pending', 'processing', 'completed', 'cancelled'
    status: str = 'pending'
    
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class UserSkill(BaseModel):
    """User Skills extracted from README sessions"""
    id: Optional[int] = None
    session_id: int
    
    skill_name: str
    # Category: 'programming_language', 'framework', 'tool', 'database', 'cloud', 'other'
    category: Optional[str] = None
    has_icon: bool = False

class Rating(BaseModel):
    """User Ratings and Feedback"""
    id: Optional[int] = None
    user_id: int
    session_id: Optional[int] = None
    
    stars: int
    feedback_text: Optional[str] = None
    
    created_at: Optional[datetime] = None
