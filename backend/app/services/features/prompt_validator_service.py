"""Service for prompt validator use case."""

from datetime import datetime
import structlog

from app.services.ai.azure_ai_service import azure_ai_service
from app.models.schemas import PromptValidatorResult

logger = structlog.get_logger()


class PromptValidatorService:
    """Service for validating simulation prompts using the Prompt Validator Agent."""

    PROMPT_VALIDATOR_AGENT_NAME = "PromptValidatorAgent"
    PROMPT_VALIDATOR_AGENT_INSTRUCTIONS_FILE = "prompt_validator_agent.txt"

    def __init__(self):
        pass

    async def validate_prompt(self, prompt: str) -> PromptValidatorResult:
        """
        Validate a simulation prompt.
        
        Args:
            prompt: The simulation prompt to validate
            
        Returns:
            PromptValidatorResult with:
            - response_text: The validation result
            - tokens_used: Number of tokens used
            - agent_details: Details about the agent
            - timestamp: When the request was made
            - thread_id: Conversation ID
        """
        try:
            logger.info("="*60)
            logger.info("Starting prompt validation", prompt_length=len(prompt))
            logger.debug("Prompt to validate", prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt)

            # Create agent from file
            logger.info("Creating Prompt Validator Agent...")
            agent = azure_ai_service.create_agent_from_file(
                agent_name=self.PROMPT_VALIDATOR_AGENT_NAME,
                instructions_path=self.PROMPT_VALIDATOR_AGENT_INSTRUCTIONS_FILE
            )
            logger.info("Prompt Validator Agent ready", agent_version=agent.agent_version_object.version)

            # Create conversation with initial message
            timestamp = datetime.utcnow()
            logger.info("Creating conversation with validation request...")
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": prompt}]
            )
            conversation_id = conversation.id
            logger.info("Conversation created", conversation_id=conversation_id)

            # Create response using the agent
            logger.info("Requesting validation from Prompt Validator Agent...")
            response = azure_ai_service.openai_client.responses.create(
                conversation=conversation_id,
                extra_body={"agent": {"name": agent.agent_version_object.name, "type": "agent_reference"}},
                input=""
            )
            logger.info("Validation response received", conversation_id=conversation_id)

            # Get response text
            logger.debug("Extracting validation result...")
            response_text = response.output_text

            if response_text is None:
                logger.error("No validation result found")
                raise ValueError("No response found")
            
            logger.info("Validation result extracted",
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
            logger.info("Prompt validation completed",
                       tokens_used=tokens_used,
                       agent_version=agent.agent_version_object.version,
                       conversation_id=conversation_id)
            logger.info("="*60)

            return PromptValidatorResult(
                response_text=response_text,
                tokens_used=tokens_used,
                agent_details=agent.agent_details,
                timestamp=timestamp,
                thread_id=conversation_id
            )

        except Exception as e:
            logger.error("Error validating prompt", error=str(e), exc_info=True)
            raise


# Singleton instance
prompt_validator_service = PromptValidatorService()
