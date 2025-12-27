from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from app.core.config import settings
from typing import Optional, Tuple
from datetime import datetime
import structlog

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
        Get response from an agent using Azure AI Foundry versioning pattern.
        
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
            
            # Create or get agent version using the Azure AI Foundry pattern
            agent = self.client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions=instructions,
                )
            )
            
            logger.info(f"Agent version created/retrieved", 
                       agent_name=agent.name, 
                       agent_id=agent.id,
                       agent_version=agent.version)
            
            # Use OpenAI client for conversation
            with self.client.get_openai_client() as openai_client:
                # Create conversation
                conversation = openai_client.conversations.create(
                    items=[{
                        "type": "message",
                        "role": "user",
                        "content": prompt
                    }],
                )
                
                # Get response using agent reference
                response = openai_client.responses.create(
                    conversation=conversation.id,
                    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                    input="",
                )
                
                response_text = response.output_text
                
                # Extract token usage
                tokens_used = None
                if hasattr(response, 'usage') and response.usage:
                    tokens_used = response.usage.total_tokens
                
                # Clean up conversation
                openai_client.conversations.delete(conversation_id=conversation.id)
                
                return response_text, tokens_used, agent.version, timestamp
            
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
