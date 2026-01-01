"""Service for persona distribution generation use case."""

from datetime import datetime
import structlog
from typing import Optional

from app.services.ai.azure_ai_service import azure_ai_service
from app.services.db.cosmos_db_service import cosmos_db_service
from app.models.schemas import PersonaDistributionResult

logger = structlog.get_logger()


class PersonaDistributionService:
    """Service for generating persona distributions using the Persona Distribution Generator Agent."""

    PERSONA_DISTRIBUTION_AGENT_NAME = "PersonaDistributionGeneratorAgent"
    PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS_FILE = "persona_distribution_agent.txt"

    def __init__(self):
        pass

    async def generate_persona_distribution(self, prompt: str) -> PersonaDistributionResult:
        """
        Generate a persona distribution from the given prompt.
        
        Args:
            prompt: The simulation prompt to generate persona distribution from
            
        Returns:
            PersonaDistributionResult with:
            - response_text: The generated persona distribution
            - tokens_used: Number of tokens used
            - agent_details: Details about the agent
            - timestamp: When the request was made
            - conversation_id: Conversation ID
        """
        try:
            logger.info("="*60)
            logger.info("Starting persona distribution generation", prompt_length=len(prompt))
            logger.debug("Prompt preview", prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt)

            # Create agent from file
            logger.info("Creating Persona Distribution Generator Agent...")
            agent = azure_ai_service.create_agent_from_file(
                agent_name=self.PERSONA_DISTRIBUTION_AGENT_NAME,
                instructions_path=self.PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS_FILE
            )
            logger.info("Persona Distribution Generator Agent ready", agent_version=agent.agent_version_object.version)

            # Create conversation with initial message
            timestamp = datetime.utcnow()
            logger.info("Creating conversation with user message...")
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": prompt}]
            )
            conversation_id = conversation.id
            logger.info("Conversation created", conversation_id=conversation_id)

            # Create response using the agent
            logger.info("Requesting response from Persona Distribution Generator Agent...")
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
            
            logger.info("Persona distribution generated successfully", 
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
            logger.info("Persona distribution generation completed",
                       tokens_used=tokens_used,
                       agent_version=agent.agent_version_object.version,
                       conversation_id=conversation_id)
            logger.info("="*60)

            return PersonaDistributionResult(
                response_text=response_text,
                tokens_used=tokens_used,
                agent_details=agent.agent_details,
                timestamp=timestamp,
                conversation_id=conversation_id
            )

        except Exception as e:
            logger.error("Error generating persona distribution", error=str(e), exc_info=True)
            raise

    async def save_to_database(
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
        """
        Save persona distribution generation result to database.
        
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
        """
        logger.info("Saving persona distribution generation to database",
                   agent=agent_name,
                   tokens=tokens_used,
                   time_ms=round(time_taken_ms, 2))
        
        # Create document with structure specific to persona distribution generation
        document_id = f"{datetime.utcnow().isoformat()}_{agent_name}"
        document = {
            "id": document_id,
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
        
        # Use generic save method from CosmosDBService
        await cosmos_db_service.save_document(
            container_name=cosmos_db_service.PERSONA_DISTRIBUTION_CONTAINER,
            document=document
        )
        logger.info("Persona distribution generation saved successfully", document_id=document_id)


# Singleton instance
persona_distribution_service = PersonaDistributionService()
