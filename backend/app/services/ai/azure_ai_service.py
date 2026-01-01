from azure.ai.projects.models import PromptAgentDefinition, AgentVersionObject
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai import OpenAI

from app.core.config import settings
from typing import Optional, NamedTuple, Dict, TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from app.models.schemas import AgentDetails

logger = structlog.get_logger()


class Agent(NamedTuple):
    """Represents a cached agent with its configuration."""
    instructions: str
    model_deployment_name: str
    agent_version_object: 'AgentVersionObject'
    agent_details: 'AgentDetails'


class AzureAIService:
    """Service for initializing and managing Azure AI Projects clients.
    
    This service is responsible for:
    - Initializing and caching the AIProjectClient and OpenAI client
    - Creating agents with specified names, instructions, and model deployments
    
    Business logic for specific usecases should be implemented in dedicated service classes
    that use this service to get clients and create agents as needed.
    """

    _instance: Optional['AzureAIService'] = None
    _client: Optional[AIProjectClient] = None
    _openai_client: Optional["OpenAI"] = None
    _agents_cache: Dict[str, Agent] = {}

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
            logger.info("Initializing Azure AI Project Client...", 
                       endpoint=settings.azure_ai_project_connection_string[:50] + "...")
            self._client = AIProjectClient(
                endpoint=settings.azure_ai_project_connection_string,
                credential=DefaultAzureCredential()
            )
            logger.debug("AIProjectClient created, getting OpenAI client...")
            self._openai_client = self._client.get_openai_client()
            logger.info("Azure AI Project Client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Azure AI Project Client", error=str(e), exc_info=True)
            raise

    @property
    def client(self) -> AIProjectClient:
        """Get the Azure AI Project Client instance."""
        if self._client is None:
            self._initialize_client()
        return self._client

    @property
    def openai_client(self) -> "OpenAI":
        """Get the Azure OpenAI Client instance."""
        if self._openai_client is None:
            self._openai_client = self._client.get_openai_client()
        return self._openai_client

    def create_agent(
            self,
            agent_name: str,
            instructions: str
    ) -> Agent:
        """
        Get or create an agent with the specified configuration.
        
        Args:
            agent_name: The name of the agent
            instructions: The system instructions for the agent
            
        Returns:
            Agent: The created or cached Agent object
        """
        logger.debug("Agent requested", agent_name=agent_name, instructions_length=len(instructions))
        
        if agent_name in self._agents_cache:
            cached_agent = self._agents_cache[agent_name]
            logger.info("Agent retrieved from cache", 
                       agent_name=agent_name, 
                       agent_version=cached_agent.agent_version_object.version,
                       model=cached_agent.model_deployment_name)
            return cached_agent
        
        logger.info("Agent not in cache, creating new agent", agent_name=agent_name)

        model_deployment_name = settings.default_model_deployment
        try:
            from app.models.schemas import AgentDetails
            
            agent_version_object = self.client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model_deployment_name,
                    instructions=instructions
                ),
            )

            agent_details = AgentDetails(
                agent_name=agent_name,
                agent_version=agent_version_object.version,
                instructions=instructions,
                model_deployment_name=model_deployment_name,
                created_at=agent_version_object.created_at
            )

            agent = Agent(
                instructions=instructions,
                model_deployment_name=model_deployment_name,
                agent_version_object=agent_version_object,
                agent_details=agent_details
            )
            self._agents_cache[agent_name] = agent
            
            logger.info("Agent created successfully",
                        agent_name=agent_name,
                        agent_id=agent_version_object.id,
                        agent_version=agent_version_object.version,
                        model=model_deployment_name,
                        instructions_length=len(instructions),
                        created_at=agent_version_object.created_at)
            logger.debug("Agent cached", agent_name=agent_name, cache_size=len(self._agents_cache))

            return agent

        except Exception as e:
            logger.error(f"Error creating agent: {e}",
                         agent_name=agent_name,
                         error=str(e))
            raise


# Singleton instance
azure_ai_service = AzureAIService()
