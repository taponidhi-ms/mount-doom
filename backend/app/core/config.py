from pydantic_settings import BaseSettings
from typing import List
import json
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure AI Projects Configuration
    azure_ai_project_connection_string: str
    
    # Cosmos DB Configuration
    cosmos_db_endpoint: str
    cosmos_db_database_name: str
    
    # Default Model Configuration
    default_model_deployment: str = "gpt-4"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    
    # Logging Configuration
    log_dir: str = "logs"
    log_file: str = "mount_doom.log"
    log_max_bytes: int = 10485760  # 10MB
    log_backup_count: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
