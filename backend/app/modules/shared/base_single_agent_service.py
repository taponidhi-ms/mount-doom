"""
Base service for single-agent operations.

This module provides a reusable base class for all single-agent use cases,
handling common patterns like agent creation, conversation management,
response extraction, and database persistence.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable, Protocol
from abc import ABC, abstractmethod
import json
import structlog

from app.infrastructure.ai.azure_ai_service import azure_ai_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from app.models.shared import AgentDetails
from app.models.single_agent import SingleAgentResult, SingleAgentDocument

logger = structlog.get_logger()


class AgentCreator(Protocol):
    """Protocol for agent creation functions."""
    def __call__(self) -> Any: ...


class BaseSingleAgentService(ABC):
    """
    Base class for single-agent services.
    
    Provides common functionality for:
    - Creating agents with proper caching
    - Managing conversations
    - Extracting responses and tokens
    - Parsing JSON outputs
    - Saving to database
    
    Subclasses must implement:
    - get_agent_creator(): Returns the agent creation function
    - get_container_name(): Returns the Cosmos DB container name
    - get_use_case_name(): Returns a human-readable use case name for logging
    """
    
    def __init__(self):
        pass
    
    @abstractmethod
    def get_agent_creator(self) -> Callable:
        """Return the function that creates the agent for this use case."""
        pass
    
    @abstractmethod
    def get_container_name(self) -> str:
        """Return the Cosmos DB container name for this use case."""
        pass
    
    @abstractmethod
    def get_use_case_name(self) -> str:
        """Return a human-readable name for this use case (for logging)."""
        pass
    
    def _parse_json_output(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to parse JSON from agent response.
        
        Args:
            response_text: The raw response text from the agent
            
        Returns:
            Parsed JSON dict or None if parsing fails
        """
        try:
            parsed = json.loads(response_text)
            logger.info(f"{self.get_use_case_name()}: Successfully parsed JSON output", 
                       keys=list(parsed.keys()) if isinstance(parsed, dict) else "not a dict")
            return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"{self.get_use_case_name()}: Failed to parse JSON output", 
                          error=str(e), 
                          response_preview=response_text[:200])
            return None
    
    async def generate(self, prompt: str, parse_json: bool = True) -> SingleAgentResult:
        """
        Generate a response using the agent.
        
        Args:
            prompt: The input prompt for the agent
            parse_json: Whether to attempt JSON parsing of the response
            
        Returns:
            SingleAgentResult containing the response and metadata
        """
        use_case = self.get_use_case_name()
        
        try:
            logger.info("="*60)
            logger.info(f"Starting {use_case} generation", prompt_length=len(prompt))
            logger.debug("Prompt preview", prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt)

            # Create agent with instructions
            logger.info(f"Creating {use_case} Agent...")
            agent_creator = self.get_agent_creator()
            agent = agent_creator()
            logger.info(f"{use_case} Agent ready", agent_version=agent.agent_version_object.version)

            # Create conversation with initial message
            timestamp = datetime.now(timezone.utc)
            logger.info("Creating conversation with user message...")
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": prompt}]
            )
            conversation_id = conversation.id
            logger.info("Conversation created", conversation_id=conversation_id)

            # Create response using the agent
            logger.info(f"Requesting response from {use_case} Agent...")
            response = azure_ai_service.openai_client.responses.create(
                conversation=conversation_id,
                extra_body={"agent": {"name": agent.agent_version_object.name, "type": "agent_reference"}},
                input=""
            )
            logger.info("Response received", conversation_id=conversation_id)

            # Get response text
            logger.debug("Extracting response text...")
            response_text = response.output_text

            if response_text is None:
                logger.error("No response text found in response")
                raise ValueError("No response found")
            
            logger.info(f"{use_case} generated successfully", 
                       response_length=len(response_text),
                       response_preview=response_text[:150] + "..." if len(response_text) > 150 else response_text)

            # Parse JSON output if requested
            parsed_output = None
            if parse_json:
                parsed_output = self._parse_json_output(response_text)

            # Extract token usage
            logger.debug("Extracting token usage...")
            tokens_used = None
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.total_tokens
                logger.info("Token usage extracted", tokens_used=tokens_used)
            else:
                logger.debug("No token usage information available")
            
            logger.info("="*60)
            logger.info(f"{use_case} generation completed",
                       tokens_used=tokens_used,
                       agent_version=agent.agent_version_object.version,
                       conversation_id=conversation_id,
                       parsed_successfully=parsed_output is not None)
            logger.info("="*60)

            return SingleAgentResult(
                response_text=response_text,
                tokens_used=tokens_used,
                agent_details=agent.agent_details,
                timestamp=timestamp,
                conversation_id=conversation_id,
                parsed_output=parsed_output
            )

        except Exception as e:
            logger.error(f"Error generating {use_case}", error=str(e), exc_info=True)
            raise
    
    async def save_to_database(
        self,
        prompt: str,
        response: str,
        tokens_used: Optional[int],
        time_taken_ms: float,
        agent_name: str,
        agent_version: Optional[str],
        agent_instructions: str,
        model: str,
        agent_timestamp: datetime,
        conversation_id: str,
        parsed_output: Optional[Dict[str, Any]] = None
    ):
        """
        Save the generation result to Cosmos DB.
        
        Uses the conversation_id as document ID.
        """
        use_case = self.get_use_case_name()
        container_name = self.get_container_name()
        
        logger.info(f"Saving {use_case} result to database", 
                   conversation_id=conversation_id,
                   container=container_name)
        
        try:
            document = SingleAgentDocument(
                id=conversation_id,
                timestamp=datetime.now(timezone.utc),
                prompt=prompt,
                response=response,
                tokens_used=tokens_used,
                time_taken_ms=time_taken_ms,
                agent_details=AgentDetails(
                    agent_name=agent_name,
                    agent_version=agent_version,
                    instructions=agent_instructions,
                    model_deployment_name=model,
                    created_at=agent_timestamp
                ),
                parsed_output=parsed_output
            )
            
            await cosmos_db_service.save_document(
                container_name=container_name,
                document=document.model_dump(mode='json')
            )
            
            logger.info(f"{use_case} result saved successfully", 
                       document_id=conversation_id)
            
        except Exception as e:
            logger.error(f"Error saving {use_case} result to database", 
                        error=str(e), 
                        exc_info=True)
            raise
