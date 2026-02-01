import re
from typing import Optional, List
from urllib.parse import urlparse


class Validators:
    """Input validation utilities for the GitHub Bot"""
    
    @staticmethod
    def validate_telegram_token(token: str) -> bool:
        """
        Validate Telegram bot token format
        
        Args:
            token: Telegram bot token
            
        Returns:
            True if valid, False otherwise
        """
        if not token or not isinstance(token, str):
            return False
        
        # Telegram tokens are like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
        pattern = r'^\d+:[A-Za-z0-9_-]{35}$'
        return bool(re.match(pattern, token.strip()))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format
        
        Args:
            email: Email address
            
        Returns:
            True if valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))
    
    @staticmethod
    def validate_github_username(username: str) -> bool:
        """
        Validate GitHub username format
        
        Args:
            username: GitHub username
            
        Returns:
            True if valid, False otherwise
        """
        if not username or not isinstance(username, str):
            return False
        
        # GitHub usernames: 1-39 characters, alphanumeric and hyphens, cannot start or end with hyphen
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$'
        return bool(re.match(pattern, username.strip()))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        try:
            result = urlparse(url.strip())
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_linkedin_url(url: str) -> bool:
        """
        Validate LinkedIn URL format
        
        Args:
            url: LinkedIn URL
            
        Returns:
            True if valid, False otherwise
        """
        if not Validators.validate_url(url):
            return False
        
        url = url.strip().lower()
        return ('linkedin.com/in/' in url or 'linkedin.com/company/' in url)
    
    @staticmethod
    def validate_portfolio_url(url: str) -> bool:
        """
        Validate portfolio URL format
        
        Args:
            url: Portfolio URL
            
        Returns:
            True if valid, False otherwise
        """
        if not Validators.validate_url(url):
            return False
        
        # Common portfolio platforms
        portfolio_domains = [
            'github.io', 'vercel.app', 'netlify.app', 
            'behance.net', 'dribbble.com', 'codepen.io'
        ]
        
        url = url.strip().lower()
        return any(domain in url for domain in portfolio_domains)
    
    @staticmethod
    def validate_text_length(text: str, min_length: int = 10, max_length: int = 5000) -> bool:
        """
        Validate text length
        
        Args:
            text: Text to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            
        Returns:
            True if valid length, False otherwise
        """
        if not text or not isinstance(text, str):
            return False
        
        length = len(text.strip())
        return min_length <= length <= max_length
    
    @staticmethod
    def validate_audio_file(filename: str) -> bool:
        """
        Validate audio file format
        
        Args:
            filename: Audio filename
            
        Returns:
            True if valid audio format, False otherwise
        """
        if not filename or not isinstance(filename, str):
            return False
        
        # Supported audio formats
        audio_extensions = ['.mp3', '.wav', '.ogg', '.oga', '.m4a', '.flac']
        filename_lower = filename.lower()
        
        return any(filename_lower.endswith(ext) for ext in audio_extensions)
    
    @staticmethod
    def validate_skills(skills: List[str]) -> List[str]:
        """
        Validate and clean skills list against devicon.json
        
        Args:
            skills: List of skills to validate
            
        Returns:
            List of valid canonical skill names
        """
        if not skills or not isinstance(skills, list):
            return []
        
        from devicon.resolver import DeviconResolver
        resolver = DeviconResolver()
        
        valid_skills = []
        for skill in skills:
            if isinstance(skill, str) and skill.strip():
                canonical = resolver.get_canonical_name(skill)
                if canonical:
                    valid_skills.append(canonical)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in valid_skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate person name format
        
        Args:
            name: Person's name
            
        Returns:
            True if valid, False otherwise
        """
        if not name or not isinstance(name, str):
            return False
        
        name = name.strip()
        
        # Name should be 2-50 characters, letters, spaces, hyphens, apostrophes
        if len(name) < 2 or len(name) > 50:
            return False
        
        pattern = r'^[a-zA-Z\s\-\'\.]+$'
        return bool(re.match(pattern, name))
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe file system usage
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        if not filename or not isinstance(filename, str):
            return "file"
        
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\?*]', '', filename.strip())
        
        # Replace spaces with underscores
        sanitized = re.sub(r'\s+', '_', sanitized)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = "file"
        
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate phone number format (international)
        
        Args:
            phone: Phone number
            
        Returns:
            True if valid, False otherwise
        """
        if not phone or not isinstance(phone, str):
            return False
        
        # Remove common formatting characters
        cleaned = re.sub(r'[^\d+]', '', phone.strip())
        
        # Should start with + and have 8-15 digits
        pattern = r'^\+\d{8,15}$'
        return bool(re.match(pattern, cleaned))