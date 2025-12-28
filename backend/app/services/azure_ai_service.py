from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from app.core.config import settings
from app.models.schemas import AgentResponseData
from typing import Optional, Tuple, Dict
from datetime import datetime
import structlog
import hashlib
import json
import threading

logger = structlog.get_logger()


class AzureAIService:
    """Service for interacting with Azure AI Projects."""
    
    _instance: Optional['AzureAIService'] = None
    _client: Optional[AIProjectClient] = None
    _agents_cache: Dict[str, str] = {}  # Cache: agent_key -> agent_id
    _cache_lock = threading.Lock()  # Thread-safe access to cache
    
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
    
    def _get_or_create_agent(self, agent_name: str, instructions: str, model_deployment_name: str) -> str:
        """
        Get or create an agent based on name, instructions, and model deployment.
        Agents are cached to avoid recreating them on every request.
        Thread-safe implementation using a lock.
        
        Args:
            agent_name: The fixed name of the agent (e.g., "C1Agent", "PersonaAgent")
            instructions: The instruction set for the agent
            model_deployment_name: The model deployment to use (e.g., "gpt-4")
            
        Returns:
            agent_id: The ID of the created or cached agent
        """
        # Create a cache key based on agent name and instructions hash
        instructions_hash = hashlib.sha256(instructions.encode()).hexdigest()[:8]
        cache_key = f"{agent_name}_{instructions_hash}_{model_deployment_name}"
        
        # Thread-safe cache access
        agent_id = None
        with self._cache_lock:
            # Check if agent already exists in cache
            if cache_key in self._agents_cache:
                agent_id = self._agents_cache[cache_key]
        
        # Log cache hit outside critical section
        if agent_id is not None:
            logger.info("Using cached agent", 
                       agent_name=agent_name,
                       agent_id=agent_id,
                       cache_key=cache_key)
            return agent_id
        
        # Create new agent using the agents API (outside lock to avoid blocking)
        try:
            created_agent = self.client.agents.create_agent(
                model=model_deployment_name,
                name=agent_name,
                instructions=instructions,
                description=f"Agent for {agent_name}"
            )
            agent_id = created_agent.id
            
            # Cache the agent ID (with lock)
            with self._cache_lock:
                self._agents_cache[cache_key] = agent_id
            
            logger.info("Created new agent", 
                       agent_name=agent_name,
                       agent_id=agent_id,
                       cache_key=cache_key)
            
            return agent_id
            
        except Exception as e:
            logger.error(f"Error creating agent: {e}", 
                        agent_name=agent_name,
                        error=str(e))
            raise

    async def get_agent_response(
        self,
        agent_name: str,
        instructions: str,
        prompt: str,
        model_deployment_name: str
    ) -> AgentResponseData:
        """
        Get response from an agent with instructions using Azure AI Agent workflow.
        
        This method creates and uses agents instead of direct model calls.
        The workflow includes:
        1. Create or retrieve cached agent
        2. Create a thread for the conversation
        3. Post user message to the thread
        4. Run the agent on the thread
        5. Retrieve the agent's response
        
        Args:
            agent_name: The fixed name of the agent (e.g., "C1Agent", "PersonaAgent")
            instructions: The instruction set for the agent
            prompt: The prompt to send to the agent
            model_deployment_name: The model deployment to use (e.g., "gpt-4")
            
        Returns:
            AgentResponseData with response_text, tokens_used, agent_version, timestamp, and thread_id
        """
        try:
            timestamp = datetime.utcnow()
            
            # Generate version hash from instructions
            instructions_hash = hashlib.sha256(instructions.encode()).hexdigest()[:8]
            agent_version = f"v{instructions_hash}"
            
            logger.info(f"Getting agent response", 
                       agent_name=agent_name,
                       agent_version=agent_version,
                       model_deployment_name=model_deployment_name)
            
            # Step 1: Get or create agent
            agent_id = self._get_or_create_agent(agent_name, instructions, model_deployment_name)
            
            # Step 2: Create a thread for this conversation
            thread = self.client.agents.create_thread()
            thread_id = thread.id
            
            logger.info("Created thread", thread_id=thread_id)
            
            # Step 3: Post user message to the thread
            message = self.client.agents.create_message(
                thread_id=thread_id,
                role="user",
                content=prompt
            )
            
            logger.info("Posted message to thread", 
                       thread_id=thread_id,
                       message_id=message.id)
            
            # Step 4: Run the agent on the thread using create_and_process_run
            # This method automatically polls for completion
            run = self.client.agents.create_and_process_run(
                thread_id=thread_id,
                assistant_id=agent_id
            )
            
            logger.info("Run completed", 
                       run_id=run.id,
                       status=run.status)
            
            # Step 5: Retrieve agent responses from the thread
            messages = self.client.agents.list_messages(thread_id=thread_id)
            
            # Get the assistant's response using get_last_text_message_by_role
            response_text = None
            
            # Try to use the helper method if available
            if hasattr(messages, 'get_last_text_message_by_role'):
                try:
                    assistant_message = messages.get_last_text_message_by_role("assistant")
                    if assistant_message and hasattr(assistant_message, 'text'):
                        response_text = assistant_message.text.value
                except AttributeError as e:
                    logger.warning(f"Error using get_last_text_message_by_role: {e}")
            
            # Fallback: manually iterate through messages if helper method failed or doesn't exist
            if response_text is None:
                for msg in messages:
                    if msg.role == "assistant":
                        # The content is in msg.content - it's a list of content items
                        if msg.content and len(msg.content) > 0:
                            # Extract text from the first content item
                            content_item = msg.content[0]
                            if hasattr(content_item, 'text'):
                                response_text = content_item.text.value
                            elif hasattr(content_item, 'value'):
                                response_text = content_item.value
                            else:
                                response_text = str(content_item)
                        break
            
            if response_text is None:
                raise ValueError("No assistant response found in thread")
            
            # Extract token usage from run if available
            tokens_used = None
            if hasattr(run, 'usage') and run.usage:
                tokens_used = run.usage.total_tokens
            
            logger.info("Agent response retrieved successfully",
                       response_length=len(response_text),
                       tokens_used=tokens_used,
                       thread_id=thread_id)
            
            return AgentResponseData(
                response_text=response_text,
                tokens_used=tokens_used,
                agent_version=agent_version,
                timestamp=timestamp,
                thread_id=thread_id
            )
            
        except Exception as e:
            logger.error(f"Error getting agent response: {e}", 
                        agent_name=agent_name,
                        error=str(e))
            raise
    
    async def get_model_response(
        self,
        model_deployment_name: str,
        prompt: str
    ) -> tuple[str, Optional[int]]:
        """
        Get response from a model directly (not using agent).
        Uses the responses API for conversational context.
        
        Args:
            model_deployment_name: The deployment name of the model to use
            prompt: The prompt to send to the model
            
        Returns:
            Tuple of (response_text, tokens_used)
        """
        try:
            # Use the responses API via OpenAI client
            with self.client.get_openai_client() as openai_client:
                response = openai_client.responses.create(
                    model=model_deployment_name,
                    input=prompt
                )
                
                response_text = response.output_text
                # Note: The responses API may not provide token usage in the same way
                # Check if usage information is available
                tokens_used = None
                if hasattr(response, 'usage') and response.usage:
                    tokens_used = response.usage.total_tokens
                
                return response_text, tokens_used
            
        except Exception as e:
            logger.error(f"Error getting model response: {e}")
            raise


# Singleton instance
azure_ai_service = AzureAIService()
