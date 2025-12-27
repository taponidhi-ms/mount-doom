from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from app.core.config import settings
from typing import Optional, Tuple
from datetime import datetime
import structlog
import hashlib
import json

logger = structlog.get_logger()


class AzureAIService:
    """Service for interacting with Azure AI Projects."""
    
    _instance: Optional['AzureAIService'] = None
    _client: Optional[AIProjectClient] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Azure AI Project Client."""
        try:
            credential = DefaultAzureCredential()
            self._client = AIProjectClient.from_connection_string(
                conn_str=settings.azure_ai_project_connection_string,
                credential=credential
            )
            logger.info("Azure AI Project Client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI Project Client: {e}")
            raise
    
    @property
    def client(self) -> AIProjectClient:
        """Get the Azure AI Project Client instance."""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    async def get_agent_response(
        self,
        agent_name: str,
        instructions: str,
        prompt: str,
        model: str,
        stream: bool = False
    ) -> tuple[str, Optional[int], str, datetime]:
        """
        Get response from an agent with instructions.
        
        Args:
            agent_name: The fixed name of the agent (e.g., "C1Agent", "PersonaAgent")
            instructions: The instruction set for the agent
            prompt: The prompt to send to the agent
            model: The model to use (e.g., "gpt-4")
            stream: Whether to stream the response
            
        Returns:
            Tuple of (response_text, tokens_used, agent_version, timestamp)
        """
        try:
            timestamp = datetime.utcnow()
            
            # Generate version hash from instructions
            # This ensures that whenever instructions change, a new version is created
            instructions_hash = hashlib.sha256(instructions.encode()).hexdigest()[:8]
            agent_version = f"v{instructions_hash}"
            
            logger.info(f"Using agent", 
                       agent_name=agent_name,
                       agent_version=agent_version,
                       model=model)
            
            # Use OpenAI client for conversation with instructions
            # The instructions are passed as a system message
            with self.client.get_openai_client() as openai_client:
                # Create messages with instructions as system message
                messages = [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": prompt}
                ]
                
                # Get chat completion
                response = openai_client.chat.completions.create(
                    model=model,
                    messages=messages
                )
                
                response_text = response.choices[0].message.content
                
                # Extract token usage
                tokens_used = None
                if hasattr(response, 'usage') and response.usage:
                    tokens_used = response.usage.total_tokens
                
                return response_text, tokens_used, agent_version, timestamp
            
        except Exception as e:
            logger.error(f"Error getting agent response: {e}", 
                        agent_name=agent_name,
                        error=str(e))
            raise
    
    async def get_model_response(
        self,
        model_id: str,
        prompt: str,
        stream: bool = False
    ) -> tuple[str, Optional[int]]:
        """
        Get response from a model directly (not using agent).
        
        Args:
            model_id: The ID of the model to use
            prompt: The prompt to send to the model
            stream: Whether to stream the response
            
        Returns:
            Tuple of (response_text, tokens_used)
        """
        try:
            # Use the chat completions API directly
            response = self.client.inference.get_chat_completions(
                model=model_id,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
            
            return response_text, tokens_used
            
        except Exception as e:
            logger.error(f"Error getting model response: {e}")
            raise


# Singleton instance
azure_ai_service = AzureAIService()
