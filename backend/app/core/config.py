from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure AI Projects Configuration
    azure_ai_project_connection_string: str
    
    # Cosmos DB Configuration
    cosmos_db_endpoint: str
    cosmos_db_database_name: str
    
    # Agent IDs
    persona_generation_agent_1: str = ""
    persona_generation_agent_2: str = ""
    prompt_validator_agent: str = ""
    conversation_c1_agent: str = ""
    conversation_c2_agent: str = ""
    conversation_orchestrator_agent: str = ""
    
    # Model IDs
    general_model_1: str = "gpt-4"
    general_model_2: str = "gpt-35-turbo"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
