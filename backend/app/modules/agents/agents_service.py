"""
Unified Agents Service.

This service handles all single-agent operations using a generic approach.
It uses the agent configuration registry to determine which agent to use.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
import json
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
            # Build document - use the input field name from config
            document = {
                "id": conversation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                config.input_field: input_text,  # Use dynamic field name (prompt or transcript)
                "response": response,
                "tokens_used": tokens_used,
                "time_taken_ms": time_taken_ms,
                "agent_details": {
                    "agent_name": agent_details.agent_name,
                    "agent_version": agent_details.agent_version,
                    "instructions": agent_details.instructions,
                    "model_deployment_name": agent_details.model_deployment_name,
                    "created_at": agent_details.created_at.isoformat() if isinstance(agent_details.created_at, datetime) else agent_details.created_at
                },
                "parsed_output": parsed_output
            }
            
            await cosmos_db_service.save_document(
                container_name=container_name,
                document=document
            )
            
            logger.info(f"Agent result saved successfully", 
                       document_id=conversation_id)
            
        except Exception as e:
            logger.error(f"Error saving agent result to database", 
                        error=str(e), 
                        exc_info=True)
            raise


# Singleton instance
unified_agents_service = UnifiedAgentsService()
