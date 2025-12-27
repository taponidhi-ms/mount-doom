from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential
from app.core.config import settings
from typing import Optional, Dict, Any
import structlog
from datetime import datetime

logger = structlog.get_logger()


class CosmosDBService:
    """Service for interacting with Azure Cosmos DB."""
    
    _instance: Optional['CosmosDBService'] = None
    _client: Optional[CosmosClient] = None
    _database = None
    
    # Container names for each use case
    PERSONA_GENERATION_CONTAINER = "persona_generation"
    GENERAL_PROMPT_CONTAINER = "general_prompt"
    PROMPT_VALIDATOR_CONTAINER = "prompt_validator"
    CONVERSATION_SIMULATION_CONTAINER = "conversation_simulation"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Cosmos DB Client."""
        try:
            credential = DefaultAzureCredential()
            self._client = CosmosClient(
                url=settings.cosmos_db_endpoint,
                credential=credential
            )
            self._database = self._client.get_database_client(
                settings.cosmos_db_database_name
            )
            logger.info("Cosmos DB Client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB Client: {e}")
            raise
    
    async def ensure_container(self, container_name: str) -> Any:
        """
        Ensure a container exists, create if it doesn't.
        
        Args:
            container_name: Name of the container
            
        Returns:
            Container client
        """
        try:
            container = self._database.get_container_client(container_name)
            # Try to read container properties to check if it exists
            container.read()
            logger.info(f"Container {container_name} already exists")
            return container
        except exceptions.CosmosResourceNotFoundError:
            # Container doesn't exist, create it
            logger.info(f"Creating container {container_name}")
            container = self._database.create_container(
                id=container_name,
                partition_key=PartitionKey(path="/id")
            )
            return container
        except Exception as e:
            logger.error(f"Error ensuring container {container_name}: {e}")
            raise
    
    async def save_persona_generation(
        self,
        prompt: str,
        response: str,
        tokens_used: Optional[int],
        time_taken_ms: float,
        agent_name: str,
        agent_version: str,
        agent_instructions: str,
        model: str,
        agent_timestamp: datetime
    ):
        """Save persona generation use case data."""
        container = await self.ensure_container(self.PERSONA_GENERATION_CONTAINER)
        
        document = {
            "id": f"{datetime.utcnow().isoformat()}_{agent_name}",
            "prompt": prompt,
            "response": response,
            "tokens_used": tokens_used,
            "time_taken_ms": time_taken_ms,
            "agent_details": {
                "agent_name": agent_name,
                "agent_version": agent_version,
                "instructions": agent_instructions,
                "model": model,
                "timestamp": agent_timestamp.isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        container.create_item(body=document)
        logger.info(f"Saved persona generation data to Cosmos DB")
    
    async def save_general_prompt(
        self,
        model_id: str,
        prompt: str,
        response: str,
        tokens_used: Optional[int],
        time_taken_ms: float
    ):
        """Save general prompt use case data."""
        container = await self.ensure_container(self.GENERAL_PROMPT_CONTAINER)
        
        document = {
            "id": f"{datetime.utcnow().isoformat()}_{model_id}",
            "model_id": model_id,
            "prompt": prompt,
            "response": response,
            "tokens_used": tokens_used,
            "time_taken_ms": time_taken_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        container.create_item(body=document)
        logger.info(f"Saved general prompt data to Cosmos DB")
    
    async def save_prompt_validator(
        self,
        prompt: str,
        response: str,
        tokens_used: Optional[int],
        time_taken_ms: float,
        agent_name: str,
        agent_version: str,
        agent_instructions: str,
        model: str,
        agent_timestamp: datetime
    ):
        """Save prompt validator use case data."""
        container = await self.ensure_container(self.PROMPT_VALIDATOR_CONTAINER)
        
        document = {
            "id": f"{datetime.utcnow().isoformat()}_{agent_name}",
            "prompt": prompt,
            "response": response,
            "tokens_used": tokens_used,
            "time_taken_ms": time_taken_ms,
            "agent_details": {
                "agent_name": agent_name,
                "agent_version": agent_version,
                "instructions": agent_instructions,
                "model": model,
                "timestamp": agent_timestamp.isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        container.create_item(body=document)
        logger.info(f"Saved prompt validator data to Cosmos DB")
    
    async def save_conversation_simulation(
        self,
        conversation_properties: Dict[str, Any],
        conversation_history: list,
        conversation_status: str,
        total_tokens_used: Optional[int],
        total_time_taken_ms: float,
        c1_agent_details: Dict[str, Any],
        c2_agent_details: Dict[str, Any],
        orchestrator_agent_details: Dict[str, Any]
    ):
        """Save conversation simulation use case data."""
        container = await self.ensure_container(self.CONVERSATION_SIMULATION_CONTAINER)
        
        document = {
            "id": f"{datetime.utcnow().isoformat()}_conversation",
            "conversation_properties": conversation_properties,
            "conversation_history": conversation_history,
            "conversation_status": conversation_status,
            "total_tokens_used": total_tokens_used,
            "total_time_taken_ms": total_time_taken_ms,
            "c1_agent_details": c1_agent_details,
            "c2_agent_details": c2_agent_details,
            "orchestrator_agent_details": orchestrator_agent_details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        container.create_item(body=document)
        logger.info(f"Saved conversation simulation data to Cosmos DB")


# Singleton instance
cosmos_db_service = CosmosDBService()
