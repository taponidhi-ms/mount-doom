"""Service for prompt validator use case."""

from datetime import datetime
import structlog
import hashlib

from app.services.azure_ai_service import azure_ai_service
from app.instruction_sets import PROMPT_VALIDATOR_AGENT_NAME, PROMPT_VALIDATOR_AGENT_INSTRUCTIONS

logger = structlog.get_logger()


class PromptValidatorService:
    """Service for validating simulation prompts using the Prompt Validator Agent."""

    def __init__(self):
        self.agent_name = PROMPT_VALIDATOR_AGENT_NAME
        self.instructions = PROMPT_VALIDATOR_AGENT_INSTRUCTIONS
        self.model_deployment = "gpt-4"

    async def validate_prompt(self, prompt: str) -> dict:
        """
        Validate a simulation prompt.
        
        Args:
            prompt: The simulation prompt to validate
            
        Returns:
            Dictionary with:
            - response_text: The validation result
            - tokens_used: Number of tokens used
            - agent_version: Version hash of the agent
            - timestamp: When the request was made
            - thread_id: Conversation ID
        """
        try:
            logger.info("Validating prompt", prompt_length=len(prompt))

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

            logger.info("Prompt validated successfully",
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
            logger.error(f"Error validating prompt: {e}", error=str(e))
            raise


# Singleton instance
prompt_validator_service = PromptValidatorService()
