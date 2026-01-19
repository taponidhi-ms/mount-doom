"""
Unified Agents Service.

This service handles all single-agent operations using a generic approach.
It uses the agent configuration registry to determine which agent to use.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
import json
import uuid
import structlog

from app.infrastructure.ai.azure_ai_service import azure_ai_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from app.models.shared import AgentDetails
from app.models.single_agent import SingleAgentDocument

from .config import get_agent_config, AgentConfig

logger = structlog.get_logger()


class UnifiedAgentsService:
    """
    Service for handling all single-agent operations.
    
    Uses the agent configuration registry to dynamically create and invoke agents.
    """
    
    _instance: Optional['UnifiedAgentsService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    def _parse_json_output(self, response_text: str, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to parse JSON from agent response.
        
        Args:
            response_text: The raw response text from the agent
            agent_id: The agent identifier for logging
            
        Returns:
            Parsed JSON dict or None if parsing fails
        """
        try:
            parsed = json.loads(response_text)
            logger.info(f"Agent {agent_id}: Successfully parsed JSON output", 
                       keys=list(parsed.keys()) if isinstance(parsed, dict) else "not a dict")
            return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"Agent {agent_id}: Failed to parse JSON output", 
                          error=str(e), 
                          response_preview=response_text[:200])
            return None
    
    async def invoke_agent(
        self,
        agent_id: str,
        input_text: str
    ) -> Dict[str, Any]:
        """
        Invoke an agent by its ID.
        
        Args:
            agent_id: The agent identifier from the registry
            input_text: The input text to send to the agent
            
        Returns:
            Dict containing response_text, tokens_used, agent_details, etc.
        """
        config = get_agent_config(agent_id)
        if not config:
            raise ValueError(f"Unknown agent ID: {agent_id}")
        
        logger.info("=" * 60)
        logger.info(f"Invoking agent: {config.display_name}", 
                   agent_id=agent_id,
                   input_length=len(input_text))
        
        try:
            # Create agent
            logger.info(f"Creating agent: {config.agent_name}")
            agent = azure_ai_service.create_agent(
                agent_name=config.agent_name,
                instructions=config.instructions
            )
            logger.info("Agent ready", agent_version=agent.agent_version_object.version)
            
            # Create conversation with initial message
            timestamp = datetime.now(timezone.utc)
            logger.info("Creating conversation...")
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": input_text}]
            )
            conversation_id = conversation.id
            logger.info("Conversation created", conversation_id=conversation_id)
            
            # Create response using the agent
            logger.info("Requesting response from agent...")
            response = azure_ai_service.openai_client.responses.create(
                conversation=conversation_id,
                extra_body={"agent": {"name": agent.agent_version_object.name, "type": "agent_reference"}},
                input=""
            )
            logger.info("Response received", conversation_id=conversation_id)
            
            # Get response text
            response_text = response.output_text
            if response_text is None:
                logger.error("No response text found")
                raise ValueError("No response found")
            
            logger.info(f"Agent response generated", 
                       response_length=len(response_text),
                       response_preview=response_text[:150] + "..." if len(response_text) > 150 else response_text)
            
            # Parse JSON output
            parsed_output = self._parse_json_output(response_text, agent_id)
            
            # Extract token usage
            tokens_used = None
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.total_tokens
                logger.info("Token usage extracted", tokens_used=tokens_used)

            # Delete conversation to clean up resources
            try:
                logger.info("Deleting conversation", conversation_id=conversation_id)
                azure_ai_service.openai_client.conversations.delete(conversation_id=conversation_id)
                logger.info("Conversation deleted successfully", conversation_id=conversation_id)
            except Exception as delete_error:
                logger.warning("Failed to delete conversation",
                             conversation_id=conversation_id,
                             error=str(delete_error))
                # Continue even if deletion fails - we have the data we need

            logger.info("=" * 60)

            return {
                "response_text": response_text,
                "tokens_used": tokens_used,
                "agent_details": agent.agent_details,
                "timestamp": timestamp,
                "conversation_id": conversation_id,
                "parsed_output": parsed_output,
                "config": config
            }
            
        except Exception as e:
            logger.error(f"Error invoking agent {agent_id}", error=str(e), exc_info=True)
            raise

    async def create_conversation(
        self,
        agent_id: str,
        initial_message: str
    ) -> Dict[str, Any]:
        """
        Create a persistent conversation for multi-turn interactions.

        Used by workflows to maintain conversation state across multiple agent invocations.

        Args:
            agent_id: The agent identifier from the registry
            initial_message: The first message to add to the conversation

        Returns:
            Dict containing:
                - conversation_id: str
                - agent_details: AgentDetails
                - timestamp: datetime

        Raises:
            ValueError: If agent_id is unknown
        """
        config = get_agent_config(agent_id)
        if not config:
            raise ValueError(f"Unknown agent ID: {agent_id}")

        logger.info(f"Creating persistent conversation for {config.display_name}", agent_id=agent_id)

        try:
            # Create agent
            agent = azure_ai_service.create_agent(
                agent_name=config.agent_name,
                instructions=config.instructions
            )
            logger.info("Agent ready for persistent conversation",
                       agent_version=agent.agent_version_object.version)

            # Create conversation with initial message
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": initial_message}]
            )
            logger.info("Persistent conversation created",
                       conversation_id=conversation.id,
                       agent_id=agent_id)

            return {
                "conversation_id": conversation.id,
                "agent_details": agent.agent_details,
                "agent_name": agent.agent_version_object.name,
                "timestamp": datetime.now(timezone.utc)
            }
        except Exception as e:
            logger.error(f"Error creating persistent conversation for {agent_id}",
                        error=str(e),
                        exc_info=True)
            raise

    async def invoke_agent_on_conversation(
        self,
        agent_id: str,
        conversation_id: str,
        agent_name: str
    ) -> Dict[str, Any]:
        """
        Invoke an agent on an existing conversation without deleting it.

        Used by workflows to get agent responses within a persistent conversation.

        Args:
            agent_id: The agent identifier
            conversation_id: The existing conversation ID
            agent_name: The Azure AI agent name (from create_conversation result)

        Returns:
            Dict containing:
                - response_text: str
                - tokens_used: Optional[int]
                - timestamp: datetime

        Raises:
            ValueError: If agent_id is unknown
        """
        config = get_agent_config(agent_id)
        if not config:
            raise ValueError(f"Unknown agent ID: {agent_id}")

        logger.info(f"Invoking {config.display_name} on persistent conversation",
                   agent_id=agent_id,
                   conversation_id=conversation_id)

        try:
            # Create response using the existing conversation
            response = azure_ai_service.openai_client.responses.create(
                conversation=conversation_id,
                extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
                input=""
            )

            response_text = response.output_text
            if response_text is None:
                logger.error("No response text found in persistent conversation")
                raise ValueError("No response found")

            logger.info(f"Agent response generated on persistent conversation",
                       response_length=len(response_text),
                       conversation_id=conversation_id)

            # Extract token usage
            tokens_used = None
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.total_tokens

            return {
                "response_text": response_text,
                "tokens_used": tokens_used,
                "timestamp": datetime.now(timezone.utc)
            }
        except Exception as e:
            logger.error(f"Error invoking agent on persistent conversation",
                        agent_id=agent_id,
                        conversation_id=conversation_id,
                        error=str(e),
                        exc_info=True)
            raise

    async def add_message_to_conversation(
        self,
        conversation_id: str,
        message: str,
        role: str = "user"
    ):
        """
        Add a message to an existing conversation.

        Used by workflows to add messages between agent invocations.

        Args:
            conversation_id: The conversation ID
            message: The message content to add
            role: The role of the message sender (default: "user")
        """
        logger.debug("Adding message to persistent conversation",
                    conversation_id=conversation_id,
                    message_length=len(message))

        try:
            azure_ai_service.openai_client.conversations.items.create(
                conversation_id=conversation_id,
                items=[{"type": "message", "role": role, "content": message}]
            )
            logger.debug("Message added to persistent conversation",
                        conversation_id=conversation_id)
        except Exception as e:
            logger.error("Error adding message to persistent conversation",
                        conversation_id=conversation_id,
                        error=str(e),
                        exc_info=True)
            raise

    async def delete_conversation(
        self,
        conversation_id: str
    ):
        """
        Delete a conversation to clean up resources.

        Used by workflows after completing multi-turn conversations.

        Args:
            conversation_id: The conversation ID to delete
        """
        logger.info("Deleting persistent conversation", conversation_id=conversation_id)

        try:
            azure_ai_service.openai_client.conversations.delete(conversation_id=conversation_id)
            logger.info("Persistent conversation deleted successfully",
                       conversation_id=conversation_id)
        except Exception as delete_error:
            logger.warning("Failed to delete persistent conversation",
                         conversation_id=conversation_id,
                         error=str(delete_error))
            # Don't raise - deletion failures should not block workflow completion

    async def save_to_database(
        self,
        agent_id: str,
        input_text: str,
        response: str,
        tokens_used: Optional[int],
        time_taken_ms: float,
        agent_details: AgentDetails,
        conversation_id: str,
        parsed_output: Optional[Dict[str, Any]] = None
    ):
        """
        Save the agent invocation result to Cosmos DB.
        
        Uses the container name from the agent configuration.
        """
        config = get_agent_config(agent_id)
        if not config:
            raise ValueError(f"Unknown agent ID: {agent_id}")
        
        container_name = config.container_name
        
        logger.info(f"Saving agent result to database", 
                   agent_id=agent_id,
                   conversation_id=conversation_id,
                   container=container_name)
        
        try:
            # Generate random UUID for document ID
            document_id = str(uuid.uuid4())

            # Build document - always use "prompt" as the field name per SingleAgentDocument schema
            # Flatten agent_details to root level with agent_ prefix
            document = {
                "id": document_id,
                "conversation_id": conversation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "prompt": input_text,  # Always use "prompt" field name
                "response": response,
                "tokens_used": tokens_used,
                "time_taken_ms": time_taken_ms,
                "agent_name": agent_details.agent_name,
                "agent_version": agent_details.agent_version,
                "agent_instructions": agent_details.instructions,
                "agent_model": agent_details.model_deployment_name,
                "agent_created_at": agent_details.created_at.isoformat() if isinstance(agent_details.created_at, datetime) else agent_details.created_at
            }

            await cosmos_db_service.save_document(
                container_name=container_name,
                document=document
            )

            logger.info(f"Agent result saved successfully",
                       document_id=document_id,
                       conversation_id=conversation_id)
            
        except Exception as e:
            logger.error(f"Error saving agent result to database", 
                        error=str(e), 
                        exc_info=True)
            raise


# Singleton instance
unified_agents_service = UnifiedAgentsService()
