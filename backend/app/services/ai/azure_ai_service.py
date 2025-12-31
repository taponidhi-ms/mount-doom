from azure.ai.projects.models import PromptAgentDefinition, AgentVersionObject
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai import OpenAI

from app.core.config import settings
from typing import Optional, NamedTuple, Dict
import structlog

logger = structlog.get_logger()


class Agent(NamedTuple):
    """Represents a cached agent with its configuration."""
    instructions: str
    model_deployment_name: str
    agent_version_object: AgentVersionObject


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
            self._client = AIProjectClient(
                endpoint=settings.azure_ai_project_connection_string,
                credential=DefaultAzureCredential()
            )
            self._openai_client = self._client.get_openai_client()
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
        if agent_name in self._agents_cache:
            return self._agents_cache[agent_name]

        model_deployment_name = settings.default_model_deployment
        try:
            agent_version_object = self.client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model_deployment_name,
                    instructions=instructions
                ),
            )

            agent = Agent(
                instructions=instructions,
                model_deployment_name=model_deployment_name,
                agent_version_object=agent_version_object
            )
            self._agents_cache[agent_name] = agent
            
            logger.info("Created agent",
                        agent_name=agent_name,
                        agent_id=agent_version_object.id,
                        model=model_deployment_name)

            return agent

        except Exception as e:
            logger.error(f"Error creating agent: {e}",
                         agent_name=agent_name,
                         error=str(e))
            raise


# Singleton instance
azure_ai_service = AzureAIService()
