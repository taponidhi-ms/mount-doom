"""Service for C2 message generation use case."""

from datetime import datetime
import structlog
from typing import Optional, Dict, Any
import json

from app.infrastructure.ai.azure_ai_service import azure_ai_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from app.models.shared import AgentDetails
from .models import C2MessageGenerationResult, C2MessageGenerationDocument
from .agents import create_c2_message_generator_agent, C2_MESSAGE_GENERATOR_AGENT_NAME

logger = structlog.get_logger()


class C2MessageGenerationService:
    """Service for generating C2 (Customer) messages using the C2 Message Generator Agent."""

    def __init__(self):
        pass

    async def generate_message(self, prompt: str) -> C2MessageGenerationResult:
        """
        Generate a C2 customer message from the given prompt.
        
        Args:
            prompt: The prompt containing conversation context and properties
            
        Returns:
            C2MessageGenerationResult with:
            - response_text: The generated customer message
            - tokens_used: Number of tokens used
            - agent_details: Details about the agent
            - timestamp: When the request was made
            - conversation_id: Conversation ID
        """
        try:
            logger.info("="*60)
            logger.info("Starting C2 message generation", prompt_length=len(prompt))
            logger.debug("Prompt preview", prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt)

            # Create agent with instructions
            logger.info("Creating C2 Message Generator Agent...")
            agent = create_c2_message_generator_agent()
            logger.info("C2 Message Generator Agent ready", agent_version=agent.agent_version_object.version)

            # Create conversation with initial message
            timestamp = datetime.utcnow()
            logger.info("Creating conversation with user message...")
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": prompt}]
            )
            conversation_id = conversation.id
            logger.info("Conversation created", conversation_id=conversation_id)

            # Create response using the agent
            logger.info("Requesting response from C2 Message Generator Agent...")
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
            
            logger.info("C2 message generated successfully", 
                       response_length=len(response_text),
                       response_preview=response_text[:150] + "..." if len(response_text) > 150 else response_text)

            # Extract token usage
            logger.debug("Extracting token usage...")
            tokens_used = None
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.total_tokens
                logger.info("Token usage extracted", tokens_used=tokens_used)
            else:
                logger.debug("No token usage information available")
            
            logger.info("="*60)
            logger.info("C2 message generation completed",
                       tokens_used=tokens_used,
                       agent_version=agent.agent_version_object.version,
                       conversation_id=conversation_id)
            logger.info("="*60)

            return C2MessageGenerationResult(
                response_text=response_text,
                tokens_used=tokens_used,
                agent_details=agent.agent_details,
                timestamp=timestamp,
                conversation_id=conversation_id
            )

        except Exception as e:
            logger.error("Error generating C2 message", error=str(e), exc_info=True)
            raise

    async def generate_message_stateless(self, prompt: str) -> C2MessageGenerationResult:
        """
        Generate a C2 customer message without creating a persistent conversation.
        Used for integration with conversation simulation.
        
        Args:
            prompt: The prompt containing conversation context and properties
            
        Returns:
            C2MessageGenerationResult with response details
        """
        try:
            logger.debug("Starting stateless C2 message generation", prompt_length=len(prompt))

            # Create agent with instructions
            agent = create_c2_message_generator_agent()

            # Use stateless response creation (no conversation persistence)
            timestamp = datetime.utcnow()
            response = azure_ai_service.openai_client.responses.create(
                input=[{"role": "user", "content": prompt}],
                extra_body={"agent": {"name": agent.agent_version_object.name, "type": "agent_reference"}},
            )

            response_text = response.output_text

            if response_text is None:
                raise ValueError("No response found")

            # Extract token usage
            tokens_used = None
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.total_tokens

            return C2MessageGenerationResult(
                response_text=response_text,
                tokens_used=tokens_used,
                agent_details=agent.agent_details,
                timestamp=timestamp,
                conversation_id=""  # No conversation ID for stateless calls
            )

        except Exception as e:
            logger.error("Error in stateless C2 message generation", error=str(e), exc_info=True)
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
        conversation_id: str
    ):
        """
        Save C2 message generation result to database.
        
        Args:
            prompt: The input prompt
            response: The generated response
            tokens_used: Number of tokens used
            time_taken_ms: Time taken in milliseconds
            agent_name: Name of the agent
            agent_version: Version of the agent
            agent_instructions: Agent instructions
            model: Model deployment name
            agent_timestamp: Timestamp when agent was created
            conversation_id: The conversation ID from Azure AI
        """
        logger.info("Saving C2 message generation to database",
                   agent=agent_name,
                   tokens=tokens_used,
                   time_ms=round(time_taken_ms, 2),
                   conversation_id=conversation_id)
        
        # Create document with structure specific to C2 message generation
        agent_details = AgentDetails(
            agent_name=agent_name,
            agent_version=agent_version,
            instructions=agent_instructions,
            model_deployment_name=model,
            created_at=agent_timestamp
        )

        document = C2MessageGenerationDocument(
            id=conversation_id,
            prompt=prompt,
            response=response,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms,
            agent_details=agent_details
        )
        
        # Use generic save method from CosmosDBService
        await cosmos_db_service.save_document(
            container_name=cosmos_db_service.C2_MESSAGE_GENERATION_CONTAINER,
            document=document
        )
        logger.info("C2 message generation saved successfully", document_id=conversation_id)


# Singleton instance
c2_message_generation_service = C2MessageGenerationService()
