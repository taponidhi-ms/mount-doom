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
    
    # Model Deployments Configuration (JSON string)
    # Format: [{"model_deployment_name": "gpt-4", "display_name": "GPT-4", "description": "..."}]
    models_config: str = '[{"model_deployment_name": "gpt-4", "display_name": "GPT-4", "description": "Advanced language model for complex tasks"}, {"model_deployment_name": "gpt-35-turbo", "display_name": "GPT-3.5 Turbo", "description": "Fast and efficient model for general tasks"}]'
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_models(self):
        """Parse and return the list of model configurations."""
        try:
            return json.loads(self.models_config)
        except json.JSONDecodeError:
            # Fallback to default models if parsing fails
            return [
                {"model_deployment_name": "gpt-4", "display_name": "GPT-4", "description": "Advanced language model for complex tasks"},
                {"model_deployment_name": "gpt-35-turbo", "display_name": "GPT-3.5 Turbo", "description": "Fast and efficient model for general tasks"}
            ]


settings = Settings()
