"""Service for prompt validator use case."""

from datetime import datetime
import structlog

from app.services.ai.azure_ai_service import azure_ai_service

logger = structlog.get_logger()


class PromptValidatorService:
    """Service for validating simulation prompts using the Prompt Validator Agent."""

    PROMPT_VALIDATOR_AGENT_NAME = "PromptValidatorAgent"
    PROMPT_VALIDATOR_AGENT_INSTRUCTIONS = """
        You are a specialized prompt validation agent that assesses the quality and completeness of simulation prompts.

        Your role is to:
        - Evaluate simulation prompts for clarity, completeness, and quality
        - Identify missing information or ambiguities
        - Provide constructive feedback and suggestions for improvement
        - Ensure prompts are suitable for generating realistic simulations

        Validation Criteria:
        1. **Clarity**: Is the prompt clear and easy to understand?
        2. **Completeness**: Does it provide sufficient context and details?
        3. **Specificity**: Are requirements and expectations well-defined?
        4. **Feasibility**: Can the prompt be used to generate a realistic simulation?
        5. **Context**: Is there enough background information?
        6. **Objectives**: Are the goals of the simulation clear?

        Response Format:
        Provide a structured validation response including:
        - Overall Assessment (Valid/Needs Improvement/Invalid)
        - Strengths of the prompt
        - Issues or weaknesses identified
        - Specific recommendations for improvement
        - Revised prompt suggestion (if applicable)

        Guidelines:
        - Be constructive and helpful in your feedback
        - Point out both strengths and weaknesses
        - Provide specific, actionable recommendations
        - Use clear and professional language
        - Focus on improving the prompt's usefulness for simulations
    """

    def __init__(self):
        pass

    async def validate_prompt(self, prompt: str) -> dict:
        """
        Validate a simulation prompt.
        
        Args:
            prompt: The simulation prompt to validate
            
        Returns:
            Dictionary with:
            - response_text: The validation result
            - tokens_used: Number of tokens used
            - agent_version: Version of the agent
            - timestamp: When the request was made
            - thread_id: Conversation ID
        """
        try:
            logger.info("Validating prompt", prompt_length=len(prompt))

            # Create agent
            agent = azure_ai_service.create_agent(
                agent_name=self.PROMPT_VALIDATOR_AGENT_NAME,
                instructions=self.PROMPT_VALIDATOR_AGENT_INSTRUCTIONS.strip()
            )

            # Get version from agent object
            agent_version = agent.agent_version_object.version

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
