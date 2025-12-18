"""
Advanced logging system for QuoteWise AI application.
Provides structured logging with different levels and file rotation.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


class QuoteWiseLogger:
    """
    Centralized logging system for the QuoteWise AI application.
    Provides structured logging with file rotation and console output.
    """
    
    def __init__(self, name: str = "quotewise", log_level: str = "INFO"):
        """
        Initialize the logger with specified name and level.
        
        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup console and file handlers with proper formatting."""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_dir / "quotewise.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        # Error file handler
        error_handler = RotatingFileHandler(
            log_dir / "quotewise_errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context."""
        self.logger.debug(f"{message} | Context: {kwargs}" if kwargs else message)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context."""
        self.logger.info(f"{message} | Context: {kwargs}" if kwargs else message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context."""
        self.logger.warning(f"{message} | Context: {kwargs}" if kwargs else message)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception and context."""
        if exception:
            self.logger.error(f"{message} | Exception: {str(exception)} | Context: {kwargs}")
        else:
            self.logger.error(f"{message} | Context: {kwargs}" if kwargs else message)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical message with optional exception and context."""
        if exception:
            self.logger.critical(f"{message} | Exception: {str(exception)} | Context: {kwargs}")
        else:
            self.logger.critical(f"{message} | Context: {kwargs}" if kwargs else message)
    
    def log_quotation_event(self, event_type: str, quotation_id: str, **kwargs):
        """Log quotation-specific events."""
        self.info(f"Quotation Event: {event_type}", quotation_id=quotation_id, **kwargs)
    
    def log_agent_activity(self, agent_name: str, activity: str, **kwargs):
        """Log agent-specific activities."""
        self.info(f"Agent Activity: {agent_name} - {activity}", **kwargs)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics."""
        self.info(f"Performance: {operation} took {duration:.2f}s", **kwargs)


# Global logger instance
logger = QuoteWiseLogger()


def get_logger(name: str = "quotewise") -> QuoteWiseLogger:
    """Get a logger instance."""
    return QuoteWiseLogger(name)

