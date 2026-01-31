import logging
import os
import re
from datetime import datetime
from typing import Optional


class SecretScrubber(logging.Filter):
    """Filter to scrub secrets from log messages"""
    
    SECRET_PATTERNS = [
        r'ghp_[a-zA-Z0-9]{36}',
        r'github_pat_[a-zA-Z0-9_]{82}',
    ]
    
    def filter(self, record):
        if not isinstance(record.msg, str):
            return True
            
        for pattern in self.SECRET_PATTERNS:
            record.msg = re.sub(pattern, '[REDACTED]', record.msg)
            
        if record.args:
            new_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for pattern in self.SECRET_PATTERNS:
                        arg = re.sub(pattern, '[REDACTED]', arg)
                new_args.append(arg)
            record.args = tuple(new_args)
            
        return True


class Logger:
    """Centralized logger configuration for the GitHub Bot"""
    
    @staticmethod
    def setup_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
        """
        Setup a logger with consistent formatting
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional log file path
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Set logging level
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Scrub secrets
        scrubber = SecretScrubber()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(scrubber)
        logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            file_handler.addFilter(scrubber)
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger with default configuration"""
        log_dir = os.path.join(os.getcwd(), 'logs')
        log_file = os.path.join(log_dir, f'github_bot_{datetime.now().strftime("%Y%m%d")}.log')
        return Logger.setup_logger(name, "INFO", log_file)


# Default logger for the application
app_logger = Logger.get_logger(__name__)