"""Service for general prompt use case."""

from typing import Optional
import structlog

from app.services.ai.azure_ai_service import azure_ai_service
from app.core.config import settings
from app.models.schemas import GeneralPromptResult

logger = structlog.get_logger()


class GeneralPromptService:
    """Service for handling general prompts using direct model access."""

    async def generate_response(
            self,
            prompt: str
    ) -> GeneralPromptResult:
        """
        Generate response for a general prompt using model directly.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            GeneralPromptResult with:
            - response_text: The generated response
            - tokens_used: Number of tokens used
        """
        model_deployment_name = settings.default_model_deployment
        try:
            logger.info("="*60)
            logger.info("Starting general prompt processing",
                        model=model_deployment_name,
                        prompt_length=len(prompt))
            logger.debug("Prompt preview", prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt)

            # Use the responses API via OpenAI client
            logger.info("Sending prompt to model", model=model_deployment_name)
            response = azure_ai_service.openai_client.responses.create(
                model=model_deployment_name,
                input=prompt
            )
            logger.info("Response received from model")

            logger.debug("Extracting response text...")
            response_text = response.output_text

            if response_text is None:
                logger.error("No response text found")
                raise ValueError("No response found")
            
            logger.info("Response text extracted",
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
            logger.info("General prompt completed successfully",
                        response_length=len(response_text),
                        tokens_used=tokens_used,
                        model=model_deployment_name)
            logger.info("="*60)

            return GeneralPromptResult(
                response_text=response_text,
                tokens_used=tokens_used
            )

        except Exception as e:
            logger.error("Error generating response",
                         model=model_deployment_name,
                         error=str(e),
                         exc_info=True)
            raise


# Singleton instance
general_prompt_service = GeneralPromptService()
