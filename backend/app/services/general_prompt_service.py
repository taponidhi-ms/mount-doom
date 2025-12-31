"""Service for general prompt use case."""

from typing import Optional, Tuple
import structlog

from app.services.azure_ai_service import azure_ai_service

logger = structlog.get_logger()


class GeneralPromptService:
    """Service for handling general prompts using direct model access."""

    async def generate_response(
            self,
            model_deployment_name: str,
            prompt: str
    ) -> Tuple[str, Optional[int]]:
        """
        Generate response for a general prompt using model directly.
        
        Args:
            model_deployment_name: The deployment name of the model to use
            prompt: The prompt to send to the model
            
        Returns:
            Tuple of (response_text, tokens_used)
        """
        try:
            logger.info("Generating response for general prompt",
                        model=model_deployment_name,
                        prompt_length=len(prompt))

            # Use the responses API via OpenAI client
            response = azure_ai_service.openai_client.responses.create(
                model=model_deployment_name,
                input=prompt
            )

            response_text = response.output_text

            if response_text is None:
                raise ValueError("No response found")

            # Extract token usage
            tokens_used = None
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.total_tokens

            logger.info("Response generated successfully",
                        response_length=len(response_text),
                        tokens_used=tokens_used,
                        model=model_deployment_name)

            return response_text, tokens_used

        except Exception as e:
            logger.error(f"Error generating response: {e}",
                         model=model_deployment_name,
                         error=str(e))
            raise


# Singleton instance
general_prompt_service = GeneralPromptService()
