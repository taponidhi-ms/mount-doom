"""Service for persona generation use case."""

from datetime import datetime
import structlog
from typing import Optional

from app.services.ai.azure_ai_service import azure_ai_service
from app.models.schemas import PersonaGenerationResult

logger = structlog.get_logger()


class PersonaGenerationService:
    """Service for generating personas using the Persona Agent."""

    PERSONA_AGENT_NAME = "PersonaAgent"
    PERSONA_AGENT_INSTRUCTIONS_FILE = "persona_generation_agent.txt"

    def __init__(self):
        pass

    async def generate_persona(self, prompt: str) -> PersonaGenerationResult:
        """
        Generate a persona from the given prompt.
        
        Args:
            prompt: The simulation prompt to generate persona from
            
        Returns:
            PersonaGenerationResult with:
            - response_text: The generated persona
            - tokens_used: Number of tokens used
            - agent_details: Details about the agent
            - timestamp: When the request was made
            - conversation_id: Conversation ID
        """
        try:
            logger.info("="*60)
            logger.info("Starting persona generation", prompt_length=len(prompt))
            logger.debug("Prompt preview", prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt)

            # Create agent from file
            logger.info("Creating Persona Agent...")
            agent = azure_ai_service.create_agent_from_file(
                agent_name=self.PERSONA_AGENT_NAME,
                instructions_path=self.PERSONA_AGENT_INSTRUCTIONS_FILE
            )
            logger.info("Persona Agent ready", agent_version=agent.agent_version_object.version)

            # Create conversation with initial message
            timestamp = datetime.utcnow()
            logger.info("Creating conversation with user message...")
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": prompt}]
            )
            conversation_id = conversation.id
            logger.info("Conversation created", conversation_id=conversation_id)

            # Create response using the agent
            logger.info("Requesting response from Persona Agent...")
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
            
            logger.info("Persona generated successfully", 
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
            logger.info("Persona generation completed",
                       tokens_used=tokens_used,
                       agent_version=agent.agent_version_object.version,
                       conversation_id=conversation_id)
            logger.info("="*60)

            return PersonaGenerationResult(
                response_text=response_text,
                tokens_used=tokens_used,
                agent_details=agent.agent_details,
                timestamp=timestamp,
                conversation_id=conversation_id
            )

        except Exception as e:
            logger.error("Error generating persona", error=str(e), exc_info=True)
            raise


# Singleton instance
persona_generation_service = PersonaGenerationService()
