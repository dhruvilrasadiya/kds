"""
Configuration management for the Smart Kitchen Queue Management System.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class."""
    
    # Excel Configuration
    EXCEL_FILE_PATH: str = os.getenv("EXCEL_FILE_PATH", "data/kitchen_config.xlsx")
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "True").lower() == "true"
    
    # Kitchen Configuration
    MAX_STARVATION_COUNT: int = int(os.getenv("MAX_STARVATION_COUNT", "3"))
    SYNCHRONIZATION_WINDOW_MINUTES: int = int(os.getenv("SYNCHRONIZATION_WINDOW_MINUTES", "3"))
    PERFORMANCE_HISTORY_DAYS: int = int(os.getenv("PERFORMANCE_HISTORY_DAYS", "30"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/kitchen_queue.log")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings."""
        required_settings = [
            cls.EXCEL_FILE_PATH,
            cls.OLLAMA_BASE_URL,
            cls.OLLAMA_MODEL
        ]
        
        for setting in required_settings:
            if not setting:
                return False
        
        return True


# Global configuration instance
config = Config()
print(config.OLLAMA_BASE_URL)
print(config.OLLAMA_MODEL)
