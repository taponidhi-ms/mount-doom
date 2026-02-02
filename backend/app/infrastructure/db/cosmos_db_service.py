from azure.cosmos import CosmosClient, PartitionKey, exceptions, DatabaseProxy
from azure.identity import DefaultAzureCredential
from app.core.config import settings
from typing import Optional, Dict, Any, Union, List
from pydantic import BaseModel
import structlog
import warnings
import urllib3

logger = structlog.get_logger()


class CosmosDBService:
    """
    Infrastructure service for Cosmos DB.
    
    Responsibilities:
    - Client initialization and management (lazy initialization)
    - Database reference management
    - Generic container operations
    - Container name constants
    - Support for both local emulator and cloud instances
    
    Does NOT contain:
    - Feature-specific business logic
    - Document structure definitions
    - Feature-specific save methods
    """
    
    _instance: Optional['CosmosDBService'] = None
    _client: Optional[CosmosClient] = None
    _database: Optional[DatabaseProxy] = None
    
    # Container names for each use case
    SINGLE_TURN_CONVERSATIONS_CONTAINER = "single_turn_conversations"
    MULTI_TURN_CONVERSATIONS_CONTAINER = "multi_turn_conversations"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Don't initialize client here - use lazy initialization
        # This prevents initialization on module import during dev mode restarts
        pass
    
    def _initialize_client(self):
        """Initialize the Cosmos DB Client with support for both local emulator and cloud."""
        try:
            if settings.cosmos_db_use_emulator:
                # Use local Cosmos DB emulator
                logger.info("Initializing Cosmos DB Client for LOCAL EMULATOR...",
                           endpoint=settings.cosmos_db_endpoint,
                           database=settings.cosmos_db_database_name)

                # Suppress SSL warnings for local emulator (uses self-signed certificate)
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

                # For local emulator, use the provided key (or default emulator key)
                # Note: The default key below is the standard, well-known Cosmos DB Emulator key
                # documented by Microsoft. It's safe to use as a fallback because:
                # 1. It only works with the local emulator (not cloud instances)
                # 2. The emulator only accepts local connections
                # 3. It's the same for all Cosmos DB Emulator installations
                # See: https://learn.microsoft.com/en-us/azure/cosmos-db/emulator
                emulator_key = settings.cosmos_db_key or "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="

                # Disable SSL verification for local emulator (uses self-signed certificate)
                self._client = CosmosClient(
                    url=settings.cosmos_db_endpoint,
                    credential=emulator_key,
                    connection_verify=False
                )
                logger.info("Using local Cosmos DB emulator with key authentication (SSL verification disabled)")
            else:
                # Use Azure Cloud Cosmos DB with DefaultAzureCredential
                logger.info("Initializing Cosmos DB Client for AZURE CLOUD...",
                           endpoint=settings.cosmos_db_endpoint[:50] + "...",
                           database=settings.cosmos_db_database_name)
                
                credential = DefaultAzureCredential()
                self._client = CosmosClient(
                    url=settings.cosmos_db_endpoint,
                    credential=credential
                )
                logger.info("Using Azure Cloud Cosmos DB with DefaultAzureCredential")
            
            logger.debug("CosmosClient created, ensuring database exists...")
            # Create database if it doesn't exist
            self._database = self._client.create_database_if_not_exists(
                id=settings.cosmos_db_database_name
            )
            logger.info("Cosmos DB Client initialized successfully",
                       database=settings.cosmos_db_database_name,
                       is_emulator=settings.cosmos_db_use_emulator)
        except Exception as e:
            logger.error("Failed to initialize Cosmos DB Client", 
                        error=str(e), 
                        is_emulator=settings.cosmos_db_use_emulator,
                        exc_info=True)
            raise
    
    @property
    def client(self) -> CosmosClient:
        """Get the Cosmos DB Client instance (lazy initialization)."""
        if self._client is None:
            self._initialize_client()
        assert self._client is not None
        return self._client
    
    @property
    def database(self):
        """Get the database client (lazy initialization)."""
        if self._database is None:
            self._initialize_client()
        assert self._database is not None
        return self._database
    
    async def ensure_container(self, container_name: str) -> Any:
        """
        Ensure a container exists, create if it doesn't.
        Uses lazy initialization via database property.
        
        Args:
            container_name: Name of the container
            
        Returns:
            Container client
        """
        try:
            logger.debug("Checking container existence", container=container_name)
            container = self.database.get_container_client(container_name)
            # Try to read container properties to check if it exists
            container.read()
            logger.debug("Container exists", container=container_name)
            return container
        except exceptions.CosmosResourceNotFoundError:
            # Container doesn't exist, create it
            logger.info("Container not found, creating", container=container_name)
            container = self.database.create_container(
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
        document: Union[Dict[str, Any], BaseModel]
    ):
        """
        Generic method to save a document to a container.
        
        Args:
            container_name: Name of the container
            document: Document to save (must include 'id' field)
            
        Raises:
            ValueError: If document doesn't have 'id' field
        """
        # Convert Pydantic model to dict if necessary
        if isinstance(document, BaseModel):
            doc_dict = document.model_dump(mode='json')
        else:
            doc_dict = document

        if "id" not in doc_dict:
            raise ValueError("Document must have an 'id' field")
        
        logger.info("Saving document to Cosmos DB",
                   container=container_name,
                   document_id=doc_dict["id"])
        
        container = await self.ensure_container(container_name)
        
        logger.debug("Creating document", document_id=doc_dict["id"], container=container_name)
        container.upsert_item(body=doc_dict)
        logger.info("Document saved successfully", document_id=doc_dict["id"], container=container_name)
    
    async def browse_container(
        self,
        container_name: str,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "timestamp",
        order_direction: str = "DESC",
        agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Browse records in a container with pagination and ordering.

        Args:
            container_name: Name of the container
            page: Page number (1-indexed)
            page_size: Number of items per page
            order_by: Field to order by (default: timestamp)
            order_direction: ASC or DESC (default: DESC)
            agent_name: Optional agent name to filter by

        Returns:
            Dict with items, total_count, page, page_size, total_pages
        """
        try:
            logger.info("Browsing container",
                       container=container_name,
                       page=page,
                       page_size=page_size,
                       order_by=order_by,
                       order_direction=order_direction,
                       agent_name=agent_name)

            container = await self.ensure_container(container_name)

            # Build query with optional filtering and ordering
            if agent_name:
                where_clause = "WHERE c.agent_name = @agent_name"
                order_clause = f"ORDER BY c.{order_by} {order_direction}"
                query = f"SELECT * FROM c {where_clause} {order_clause}"
                parameters = [{"name": "@agent_name", "value": agent_name}]
            else:
                order_clause = f"ORDER BY c.{order_by} {order_direction}"
                query = f"SELECT * FROM c {order_clause}"
                parameters = None

            # Get all items (Cosmos DB SDK doesn't support OFFSET/LIMIT in query)
            items = list(container.query_items(
                query=query,
                parameters=parameters,
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
                       total_pages=total_pages,
                       filtered_by_agent=agent_name)

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

    async def get_agent_version_summary(
        self,
        container_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get summary of all unique agent versions with conversation counts.

        Args:
            container_name: Name of the container to query

        Returns:
            List of dicts with agent_name, agent_version, and count
            Example: [{"agent_name": "persona_generator", "agent_version": "v12345678", "count": 42}]
        """
        try:
            logger.info("Getting agent version summary", container=container_name)

            container = await self.ensure_container(container_name)

            # Note: Cosmos DB SQL doesn't support GROUP BY in the traditional sense
            # We need to get all documents and group them in memory
            query = "SELECT c.agent_name, c.agent_version FROM c"

            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))

            # Group by agent_name and agent_version in memory
            version_counts: Dict[tuple, int] = {}
            for item in items:
                agent_name = item.get("agent_name")
                agent_version = item.get("agent_version")
                if agent_name and agent_version:
                    key = (agent_name, agent_version)
                    version_counts[key] = version_counts.get(key, 0) + 1

            # Convert to list of dicts
            result = [
                {
                    "agent_name": agent_name,
                    "agent_version": agent_version,
                    "count": count
                }
                for (agent_name, agent_version), count in sorted(version_counts.items())
            ]

            logger.info("Agent version summary retrieved",
                       container=container_name,
                       unique_versions=len(result),
                       total_conversations=sum(item["count"] for item in result))

            return result

        except Exception as e:
            logger.error("Error getting agent version summary",
                        container=container_name,
                        error=str(e),
                        exc_info=True)
            raise

    async def query_by_agent_and_version(
        self,
        container_name: str,
        agent_name: str,
        version: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query conversations for a specific agent and version.

        Args:
            container_name: Name of the container to query
            agent_name: The agent's name to filter by
            version: The agent's version to filter by
            limit: Optional maximum number of conversations to return

        Returns:
            List of documents matching the criteria, ordered by timestamp DESC
        """
        try:
            logger.info("Querying conversations by agent and version",
                       container=container_name,
                       agent_name=agent_name,
                       version=version,
                       limit=limit)

            container = await self.ensure_container(container_name)

            # Build query with optional TOP clause
            if limit is not None and limit > 0:
                query = f"""
                    SELECT TOP {limit} * FROM c
                    WHERE c.agent_name = @agent_name
                    AND c.agent_version = @version
                    ORDER BY c.timestamp DESC
                """
            else:
                query = """
                    SELECT * FROM c
                    WHERE c.agent_name = @agent_name
                    AND c.agent_version = @version
                    ORDER BY c.timestamp DESC
                """

            items = list(container.query_items(
                query=query,
                parameters=[
                    {"name": "@agent_name", "value": agent_name},
                    {"name": "@version", "value": version}
                ],
                enable_cross_partition_query=True
            ))

            logger.info("Conversations queried successfully",
                       container=container_name,
                       agent_name=agent_name,
                       version=version,
                       limit=limit,
                       count=len(items))

            return items

        except Exception as e:
            logger.error("Error querying by agent and version",
                        container=container_name,
                        agent_name=agent_name,
                        version=version,
                        error=str(e),
                        exc_info=True)
            raise

    async def query_cached_response(
        self,
        container_name: str,
        prompt: str,
        agent_name: str,
        agent_version: str
    ) -> Optional[Dict[str, Any]]:
        """
        Query for cached response matching prompt + agent + version.

        Args:
            container_name: Name of the container to query
            prompt: The exact prompt text (case-sensitive, whitespace-sensitive)
            agent_name: The agent's name to filter by
            agent_version: The agent's version to filter by

        Returns:
            Most recent matching document or None if no match found
        """
        try:
            logger.debug("Querying for cached response",
                        container=container_name,
                        agent_name=agent_name,
                        agent_version=agent_version,
                        prompt_length=len(prompt))

            container = await self.ensure_container(container_name)

            # Query for exact match on prompt, agent_name, and agent_version
            # Order by timestamp DESC to get most recent match
            query = """
                SELECT TOP 1 * FROM c
                WHERE c.prompt = @prompt
                AND c.agent_name = @agent_name
                AND c.agent_version = @agent_version
                ORDER BY c.timestamp DESC
            """

            items = list(container.query_items(
                query=query,
                parameters=[
                    {"name": "@prompt", "value": prompt},
                    {"name": "@agent_name", "value": agent_name},
                    {"name": "@agent_version", "value": agent_version}
                ],
                enable_cross_partition_query=True
            ))

            if items:
                logger.info("Cache hit found",
                           container=container_name,
                           agent_name=agent_name,
                           agent_version=agent_version,
                           document_id=items[0].get("id"))
                return items[0]
            else:
                logger.debug("Cache miss - no matching document found",
                            container=container_name,
                            agent_name=agent_name,
                            agent_version=agent_version)
                return None

        except Exception as e:
            # Graceful fallback - don't block generation on cache errors
            logger.warning("Error querying cached response (graceful fallback)",
                          container=container_name,
                          agent_name=agent_name,
                          agent_version=agent_version,
                          error=str(e))
            return None


# Singleton instance
cosmos_db_service = CosmosDBService()
