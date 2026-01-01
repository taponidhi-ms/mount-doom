"""Service for general prompt use case."""

from typing import Optional
from datetime import datetime
import structlog

from app.services.ai.azure_ai_service import azure_ai_service
from app.services.db.cosmos_db_service import cosmos_db_service
from app.core.config import settings
from app.models.schemas import GeneralPromptResult
from app.models.db import GeneralPromptDocument

logger = structlog.get_logger()


class GeneralPromptService:
    """Service for handling general prompts using agent with conversation pattern."""

    async def generate_response(
            self,
            prompt: str,
            cleanup_conversation: bool = True
    ) -> GeneralPromptResult:
        """
        Generate response for a general prompt using agent-based conversation pattern.
        
        This follows the Azure SDK sample pattern:
        1. Create an agent with instructions
        2. Create a conversation with initial user message
        3. Generate response using agent reference
        4. Optionally clean up conversation
        
        Args:
            prompt: The prompt to send to the agent
            cleanup_conversation: Whether to delete the conversation after completion (default: True)
            
        Returns:
            GeneralPromptResult with:
            - response_text: The generated response
            - tokens_used: Number of tokens used
        """
        model_deployment_name = settings.default_model_deployment
        conversation_id = None
        
        try:
            logger.info("="*60)
            logger.info("Starting general prompt processing",
                        model=model_deployment_name,
                        prompt_length=len(prompt))
            logger.debug("Prompt preview", prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt)

            # Step 1: Create agent with instructions
            logger.info("Creating agent for general prompt")
            agent = azure_ai_service.create_agent(
                agent_name="GeneralPromptAgent",
                instructions="You are a helpful assistant that answers general questions"
            )
            logger.info("Agent created/retrieved",
                       agent_name="GeneralPromptAgent",
                       agent_version=agent.agent_version_object.version)

            # Step 2: Create conversation with initial user message
            logger.info("Creating conversation with user message")
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": prompt}]
            )
            conversation_id = conversation.id
            logger.info("Conversation created", conversation_id=conversation_id)

            # Step 3: Generate response using agent reference
            logger.info("Generating response with agent", agent_name="GeneralPromptAgent")
            response = azure_ai_service.openai_client.responses.create(
                conversation=conversation_id,
                extra_body={"agent": {"name": "GeneralPromptAgent", "type": "agent_reference"}},
                input=""
            )
            logger.info("Response received from agent")

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

            # Step 4: Clean up conversation (if requested)
            if cleanup_conversation:
                logger.debug("Cleaning up conversation", conversation_id=conversation_id)
                azure_ai_service.openai_client.conversations.delete(conversation_id=conversation_id)
                logger.debug("Conversation deleted")
            else:
                logger.debug("Skipping conversation cleanup", conversation_id=conversation_id)

            logger.info("="*60)
            logger.info("General prompt completed successfully",
                        response_length=len(response_text),
                        tokens_used=tokens_used,
                        model=model_deployment_name)
            logger.info("="*60)

            return GeneralPromptResult(
                response_text=response_text,
                tokens_used=tokens_used,
                conversation_id=conversation_id
            )

        except Exception as e:
            logger.error("Error generating response",
                         model=model_deployment_name,
                         error=str(e),
                         exc_info=True)
            # Clean up conversation on error if it was created and cleanup is enabled
            if conversation_id and cleanup_conversation:
                try:
                    logger.debug("Attempting to clean up conversation after error", conversation_id=conversation_id)
                    azure_ai_service.openai_client.conversations.delete(conversation_id=conversation_id)
                except Exception as cleanup_error:
                    logger.debug("Failed to clean up conversation", error=str(cleanup_error))
            raise

    async def save_to_database(
        self,
        model_id: str,
        prompt: str,
        response: str,
        tokens_used: Optional[int],
        time_taken_ms: float,
        conversation_id: str
    ):
        """
        Save general prompt result to database.
        
        Args:
            model_id: ID of the model used
            prompt: The input prompt
            response: The generated response
            tokens_used: Number of tokens used
            time_taken_ms: Time taken in milliseconds
            conversation_id: The conversation ID from Azure AI
        """
        logger.info("Saving general prompt to database",
                   model=model_id,
                   tokens=tokens_used,
                   time_ms=round(time_taken_ms, 2),
                   conversation_id=conversation_id)
        
        # Create document with structure specific to general prompt
        # Use conversation_id as the document ID
        document = GeneralPromptDocument(
            id=conversation_id,
            model_deployment_name=model_id,
            prompt=prompt,
            response=response,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms
        )
        
        # Use generic save method from CosmosDBService
        await cosmos_db_service.save_document(
            container_name=cosmos_db_service.GENERAL_PROMPT_CONTAINER,
            document=document
        )
        logger.info("General prompt saved successfully", document_id=conversation_id)


# Singleton instance
general_prompt_service = GeneralPromptService()
