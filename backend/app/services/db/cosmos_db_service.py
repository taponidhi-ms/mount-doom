from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential
from app.core.config import settings
from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger()


class CosmosDBService:
    """
    Infrastructure service for Cosmos DB.
    
    Responsibilities:
    - Client initialization and management
    - Database reference management
    - Generic container operations
    - Container name constants
    
    Does NOT contain:
    - Feature-specific business logic
    - Document structure definitions
    - Feature-specific save methods
    """
    
    _instance: Optional['CosmosDBService'] = None
    _client: Optional[CosmosClient] = None
    _database = None
    
    # Container names for each use case
    PERSONA_DISTRIBUTION_CONTAINER = "persona_distribution"
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
            logger.info("Initializing Cosmos DB Client...",
                       endpoint=settings.cosmos_db_endpoint[:50] + "...",
                       database=settings.cosmos_db_database_name)
            credential = DefaultAzureCredential()
            self._client = CosmosClient(
                url=settings.cosmos_db_endpoint,
                credential=credential
            )
            logger.debug("CosmosClient created, getting database client...")
            self._database = self._client.get_database_client(
                settings.cosmos_db_database_name
            )
            logger.info("Cosmos DB Client initialized successfully",
                       database=settings.cosmos_db_database_name)
        except Exception as e:
            logger.error("Failed to initialize Cosmos DB Client", error=str(e), exc_info=True)
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
            logger.debug("Checking container existence", container=container_name)
            container = self._database.get_container_client(container_name)
            # Try to read container properties to check if it exists
            container.read()
            logger.debug("Container exists", container=container_name)
            return container
        except exceptions.CosmosResourceNotFoundError:
            # Container doesn't exist, create it
            logger.info("Container not found, creating", container=container_name)
            container = self._database.create_container(
                id=container_name,
                partition_key=PartitionKey(path="/id")
            )
            logger.info("Container created successfully", container=container_name)
            return container
        except Exception as e:
            logger.error("Error ensuring container", container=container_name, error=str(e), exc_info=True)
            raise
    
    async def save_document(
        self,
        container_name: str,
        document: Dict[str, Any]
    ):
        """
        Generic method to save a document to a container.
        
        Args:
            container_name: Name of the container
            document: Document to save (must include 'id' field)
            
        Raises:
            ValueError: If document doesn't have 'id' field
        """
        if "id" not in document:
            raise ValueError("Document must have an 'id' field")
        
        logger.info("Saving document to Cosmos DB",
                   container=container_name,
                   document_id=document["id"])
        
        container = await self.ensure_container(container_name)
        
        logger.debug("Creating document", document_id=document["id"], container=container_name)
        container.create_item(body=document)
        logger.info("Document saved successfully", document_id=document["id"], container=container_name)
    
    async def browse_container(
        self,
        container_name: str,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "timestamp",
        order_direction: str = "DESC"
    ) -> Dict[str, Any]:
        """
        Browse records in a container with pagination and ordering.
        
        Args:
            container_name: Name of the container
            page: Page number (1-indexed)
            page_size: Number of items per page
            order_by: Field to order by (default: timestamp)
            order_direction: ASC or DESC (default: DESC)
            
        Returns:
            Dict with items, total_count, page, page_size, total_pages
        """
        try:
            logger.info("Browsing container",
                       container=container_name,
                       page=page,
                       page_size=page_size,
                       order_by=order_by,
                       order_direction=order_direction)
            
            container = await self.ensure_container(container_name)
            
            # Build query with ordering
            order_clause = f"ORDER BY c.{order_by} {order_direction}"
            query = f"SELECT * FROM c {order_clause}"
            
            # Get all items (Cosmos DB SDK doesn't support OFFSET/LIMIT in query)
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            total_count = len(items)
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
            
            # Calculate pagination offsets
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            # Get page items
            page_items = items[start_idx:end_idx]
            
            logger.info("Container browsed successfully",
                       container=container_name,
                       total_count=total_count,
                       page_items=len(page_items),
                       total_pages=total_pages)
            
            return {
                "items": page_items,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
            
        except Exception as e:
            logger.error("Error browsing container",
                        container=container_name,
                        error=str(e),
                        exc_info=True)
            raise


# Singleton instance
cosmos_db_service = CosmosDBService()
