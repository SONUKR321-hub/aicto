"""Configuration management for the agent"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

class Config:
    """Configuration manager for the agent"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config_data = {}
        self.env_vars = {}
        
        load_dotenv()
        self._load_config()
        self._load_env_vars()
        
    def _load_config(self):
        """Load configuration from YAML file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
        else:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
    
    def _load_env_vars(self):
        """Load environment variables"""
        self.env_vars = {
            'instagram_username': os.getenv('INSTAGRAM_USERNAME'),
            'instagram_password': os.getenv('INSTAGRAM_PASSWORD'),
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
            'ai_provider': os.getenv('AI_PROVIDER', 'openai'),
            'database_path': os.getenv('DATABASE_PATH', 'data/database.db'),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'enable_content_filter': os.getenv('ENABLE_CONTENT_FILTER', 'true').lower() == 'true',
            'enable_copyright_check': os.getenv('ENABLE_COPYRIGHT_CHECK', 'true').lower() == 'true',
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: config.get('content.category')
        """
        keys = key_path.split('.')
        value = self.config_data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_env(self, key: str, default: Any = None) -> Any:
        """Get environment variable"""
        return self.env_vars.get(key, default)
    
    def validate(self) -> bool:
        """Validate required configuration"""
        required_config = [
            'content.category',
            'content.youtube_source_keywords',
            'instagram.account',
        ]
        
        required_env = [
            'instagram_username',
            'instagram_password',
        ]
        
        # Check required config
        for key in required_config:
            if self.get(key) is None:
                print(f"Missing required configuration: {key}")
                return False
        
        # Check required environment variables
        for key in required_env:
            if self.get_env(key) is None:
                print(f"Missing required environment variable: {key.upper()}")
                return False
        
        # Check AI provider
        if not self.get_env('openai_api_key') and not self.get_env('anthropic_api_key'):
            print("Missing AI API key. Set either OPENAI_API_KEY or ANTHROPIC_API_KEY")
            return False
        
        return True
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration data"""
        return self.config_data
    
    @property
    def instagram_username(self) -> str:
        return self.get_env('instagram_username')
    
    @property
    def instagram_password(self) -> str:
        return self.get_env('instagram_password')
    
    @property
    def ai_provider(self) -> str:
        return self.get_env('ai_provider')
    
    @property
    def openai_api_key(self) -> str:
        return self.get_env('openai_api_key')
    
    @property
    def anthropic_api_key(self) -> str:
        return self.get_env('anthropic_api_key')
    
    @property
    def database_path(self) -> str:
        return self.get_env('database_path')
