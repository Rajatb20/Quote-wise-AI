"""
Configuration management system for QuoteWise AI.
Handles environment variables, settings, and configuration validation.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from .exceptions import ConfigurationError

# Load environment variables
load_dotenv(override=True)


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    csv_path: str
    encoding: str = 'utf-8'
    backup_enabled: bool = True


@dataclass
class APIConfig:
    """API configuration settings."""
    google_api_key: str
    serper_api_key: str
    model_name: str = "gemini/gemini-2.5-flash"
    temperature: float = 0.0
    max_retries: int = 3
    timeout: int = 30


@dataclass
class UIConfig:
    """UI configuration settings."""
    page_title: str = "QuoteWise AI"
    page_icon: str = "🚀"
    layout: str = "wide"
    sidebar_state: str = "collapsed"
    theme: str = "light"


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    file_rotation: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


class Config:
    """Main configuration class for QuoteWise AI."""
    
    def __init__(self):
        self._validate_environment()
        self._load_configurations()
    
    def _validate_environment(self):
        """Validate required environment variables."""
        required_vars = [
            'GOOGLE_API_KEY',
            'SERPER_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing_vars)}",
                error_code="MISSING_ENV_VARS"
            )
    
    def _load_configurations(self):
        """Load all configuration settings."""
        self.database = DatabaseConfig(
            csv_path=os.getenv('INVENTORY_CSV_PATH', 'src/data/Westside_Inventory.csv'),
            encoding=os.getenv('CSV_ENCODING', 'utf-8'),
            backup_enabled=os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
        )
        
        self.api = APIConfig(
            google_api_key=os.getenv('GOOGLE_API_KEY'),
            serper_api_key=os.getenv('SERPER_API_KEY'),
            model_name=os.getenv('MODEL_NAME', 'gemini/gemini-2.5-flash'),
            temperature=float(os.getenv('MODEL_TEMPERATURE', '0.0')),
            max_retries=int(os.getenv('API_MAX_RETRIES', '3')),
            timeout=int(os.getenv('API_TIMEOUT', '30'))
        )
        
        self.ui = UIConfig(
            page_title=os.getenv('PAGE_TITLE', 'QuoteWise AI'),
            page_icon=os.getenv('PAGE_ICON', '🚀'),
            layout=os.getenv('PAGE_LAYOUT', 'wide'),
            sidebar_state=os.getenv('SIDEBAR_STATE', 'collapsed'),
            theme=os.getenv('THEME', 'light')
        )
        
        self.logging = LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            file_rotation=os.getenv('LOG_FILE_ROTATION', 'true').lower() == 'true',
            max_file_size=int(os.getenv('LOG_MAX_FILE_SIZE', str(10 * 1024 * 1024))),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5'))
        )
    
    def get_database_path(self) -> str:
        """Get the full path to the database CSV file."""
        return os.path.abspath(self.database.csv_path)
    
    def get_output_directory(self) -> str:
        """Get the output directory for generated files."""
        return os.path.abspath('src/outputs')
    
    def get_final_quotes_directory(self) -> str:
        """Get the final quotes directory."""
        return os.path.abspath('final_quotes')
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'


# Global configuration instance
config = Config()

