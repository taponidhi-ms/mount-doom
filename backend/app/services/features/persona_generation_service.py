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
    PERSONA_AGENT_INSTRUCTIONS = """
        You are a specialized persona generation agent that creates detailed, realistic personas based on simulation prompts.

        Your role is to:
        - Analyze simulation prompts and extract key characteristics
        - Generate comprehensive persona profiles
        - Create realistic and consistent character backgrounds
        - Define behavioral traits, motivations, and communication styles

        When generating a persona:
        1. Carefully read and understand the simulation prompt
        2. Identify the context, scenario, and requirements
        3. Create a detailed persona including:
           - Name and basic demographics
           - Background and experience
           - Personality traits and characteristics
           - Communication style and preferences
           - Goals and motivations
           - Relevant context for the simulation

        Guidelines:
        - Make personas realistic and believable
        - Ensure consistency in personality and behavior
        - Tailor personas to fit the simulation context
        - Include enough detail to guide realistic interactions
        - Keep personas focused and relevant to the use case

        Output Format:
        Provide a well-structured persona description that can be used in simulations.
    """

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
            - thread_id: Conversation ID
        """
        try:
            logger.info("="*60)
            logger.info("Starting persona generation", prompt_length=len(prompt))
            logger.debug("Prompt preview", prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt)

            # Create agent
            logger.info("Creating Persona Agent...")
            agent = azure_ai_service.create_agent(
                agent_name=self.PERSONA_AGENT_NAME,
                instructions=self.PERSONA_AGENT_INSTRUCTIONS.strip()
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
                thread_id=conversation_id
            )

        except Exception as e:
            logger.error("Error generating persona", error=str(e), exc_info=True)
            raise


# Singleton instance
persona_generation_service = PersonaGenerationService()
