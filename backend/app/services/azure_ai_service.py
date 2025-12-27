from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from app.core.config import settings
from typing import Optional
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
        agent_id: str,
        prompt: str,
        stream: bool = False
    ) -> tuple[str, Optional[int]]:
        """
        Get response from an agent.
        
        Args:
            agent_id: The ID of the agent to use
            prompt: The prompt to send to the agent
            stream: Whether to stream the response
            
        Returns:
            Tuple of (response_text, tokens_used)
        """
        try:
            # Create agent with the specified agent_id
            agent = self.client.agents.create_agent(
                model=agent_id,
                name="agent",
                instructions=prompt
            )
            
            # Create thread
            thread = self.client.agents.create_thread()
            
            # Create message
            message = self.client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            
            # Run agent
            run = self.client.agents.create_run(
                thread_id=thread.id,
                agent_id=agent.id
            )
            
            # Wait for completion
            while run.status in ["queued", "in_progress"]:
                run = self.client.agents.get_run(
                    thread_id=thread.id,
                    run_id=run.id
                )
            
            # Get messages
            messages = self.client.agents.list_messages(thread_id=thread.id)
            response_text = messages.data[0].content[0].text.value if messages.data else ""
            
            # Extract token usage
            tokens_used = None
            if hasattr(run, 'usage') and run.usage:
                tokens_used = run.usage.total_tokens
            
            return response_text, tokens_used
            
        except Exception as e:
            logger.error(f"Error getting agent response: {e}")
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
