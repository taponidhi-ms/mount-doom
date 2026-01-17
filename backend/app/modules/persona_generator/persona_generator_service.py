"""Service for persona generator feature."""

from datetime import datetime, timezone
import structlog
from typing import Optional, Dict, Any
import json

from app.infrastructure.ai.azure_ai_service import azure_ai_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from app.models.shared import AgentDetails
from .models import PersonaGeneratorResult, PersonaGeneratorDocument
from .agents import create_persona_generator_agent

logger = structlog.get_logger()


class PersonaGeneratorService:
    """Service for generating exact personas using the Persona Generator Agent."""

    def __init__(self):
        pass

    def _parse_json_output(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON from agent response.
        
        Args:
            response_text: The raw response text from the agent
            
        Returns:
            Parsed JSON dict or None if parsing fails
        """
        try:
            # Try to parse the response as JSON
            parsed = json.loads(response_text)
            logger.info("Successfully parsed JSON output", 
                       keys=list(parsed.keys()) if isinstance(parsed, dict) else "not a dict")
            return parsed
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse JSON output", error=str(e), response_preview=response_text[:200])
            return None

    async def generate_personas(self, prompt: str) -> PersonaGeneratorResult:
        """
        Generate exact personas from the given prompt.
        
        Args:
            prompt: The prompt describing what personas to generate
            
        Returns:
            PersonaGeneratorResult with:
            - response_text: The generated personas JSON
            - tokens_used: Number of tokens used
            - agent_details: Details about the agent
            - timestamp: When the request was made
            - conversation_id: Conversation ID
            - parsed_output: Parsed JSON output (if successful)
        """
        try:
            logger.info("="*60)
            logger.info("Starting persona generation", prompt_length=len(prompt))
            logger.debug("Prompt preview", prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt)

            # Create agent with instructions
            logger.info("Creating Persona Generator Agent...")
            agent = create_persona_generator_agent()
            logger.info("Persona Generator Agent ready", agent_version=agent.agent_version_object.version)

            # Create conversation with initial message
            timestamp = datetime.now(timezone.utc)
            logger.info("Creating conversation with user message...")
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": prompt}]
            )
            conversation_id = conversation.id
            logger.info("Conversation created", conversation_id=conversation_id)

            # Create response using the agent
            logger.info("Requesting response from Persona Generator Agent...")
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
            
            logger.info("Personas generated successfully", 
                       response_length=len(response_text),
                       response_preview=response_text[:150] + "..." if len(response_text) > 150 else response_text)

            # Parse JSON output
            parsed_output = self._parse_json_output(response_text)

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
                       conversation_id=conversation_id,
                       parsed_successfully=parsed_output is not None)
            logger.info("="*60)

            return PersonaGeneratorResult(
                response_text=response_text,
                tokens_used=tokens_used,
                agent_details=agent.agent_details,
                timestamp=timestamp,
                conversation_id=conversation_id,
                parsed_output=parsed_output
            )

        except Exception as e:
            logger.error("Error generating personas", error=str(e), exc_info=True)
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
        agent_timestamp: datetime,
        conversation_id: str,
        parsed_output: Optional[Dict[str, Any]]
    ):
        """
        Save persona generation result to database.
        
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
            conversation_id: The conversation ID from Azure AI
            parsed_output: Parsed JSON output (if successful)
        """
        logger.info("Saving persona generation to database",
                   agent=agent_name,
                   tokens=tokens_used,
                   time_ms=round(time_taken_ms, 2),
                   conversation_id=conversation_id)
        
        # Create document with structure specific to persona generation
        # Use conversation_id as the document ID
        agent_details = AgentDetails(
            agent_name=agent_name,
            agent_version=agent_version,
            instructions=agent_instructions,
            model_deployment_name=model,
            created_at=agent_timestamp
        )

        document = PersonaGeneratorDocument(
            id=conversation_id,
            prompt=prompt,
            response=response,
            parsed_output=parsed_output,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms,
            agent_details=agent_details
        )
        
        # Use generic save method from CosmosDBService
        await cosmos_db_service.save_document(
            container_name=cosmos_db_service.PERSONA_GENERATOR_CONTAINER,
            document=document
        )
        logger.info("Persona generation saved successfully", document_id=conversation_id)


# Singleton instance
persona_generator_service = PersonaGeneratorService()
