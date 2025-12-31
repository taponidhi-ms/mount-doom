"""Service for persona generation use case."""

from datetime import datetime
import structlog
import hashlib
from typing import Optional

from app.services.azure_ai_service import azure_ai_service
from app.instruction_sets import PERSONA_AGENT_NAME, PERSONA_AGENT_INSTRUCTIONS

logger = structlog.get_logger()


class PersonaGenerationService:
    """Service for generating personas using the Persona Agent."""

    def __init__(self):
        self.agent_name = PERSONA_AGENT_NAME
        self.instructions = PERSONA_AGENT_INSTRUCTIONS
        self.model_deployment = "gpt-4"

    async def generate_persona(self, prompt: str) -> dict:
        """
        Generate a persona from the given prompt.
        
        Args:
            prompt: The simulation prompt to generate persona from
            
        Returns:
            Dictionary with:
            - response_text: The generated persona
            - tokens_used: Number of tokens used
            - agent_version: Version hash of the agent
            - timestamp: When the request was made
            - thread_id: Conversation ID
        """
        try:
            logger.info("Generating persona", prompt_length=len(prompt))

            # Create agent
            agent = azure_ai_service.create_agent(
                agent_name=self.agent_name,
                instructions=self.instructions,
                model_deployment_name=self.model_deployment
            )

            # Generate version hash from instructions
            instructions_hash = hashlib.sha256(agent.instructions.encode()).hexdigest()[:8]
            agent_version = f"v{instructions_hash}"

            # Create conversation with initial message
            timestamp = datetime.utcnow()
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": prompt}]
            )
            conversation_id = conversation.id

            logger.info("Created conversation", conversation_id=conversation_id)

            # Create response using the agent
            response = azure_ai_service.openai_client.responses.create(
                conversation=conversation_id,
                extra_body={"agent": {"name": agent.agent_version_object.name, "type": "agent_reference"}},
                input=""
            )

            logger.info("Response created", conversation_id=conversation_id)

            # Get response text
            response_text = response.output_text

            if response_text is None:
                raise ValueError("No response found")

            # Extract token usage
            tokens_used = None
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.total_tokens

            logger.info("Persona generated successfully",
                        response_length=len(response_text),
                        tokens_used=tokens_used,
                        conversation_id=conversation_id)

            return {
                "response_text": response_text,
                "tokens_used": tokens_used,
                "agent_version": agent_version,
                "timestamp": timestamp,
                "thread_id": conversation_id
            }

        except Exception as e:
            logger.error(f"Error generating persona: {e}", error=str(e))
            raise


# Singleton instance
persona_generation_service = PersonaGenerationService()
