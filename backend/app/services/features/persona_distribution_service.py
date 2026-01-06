"""Service for persona distribution generation use case."""

from datetime import datetime
import structlog
from typing import Optional, Dict, Any
import json

from app.services.ai.azure_ai_service import azure_ai_service
from app.services.db.cosmos_db_service import cosmos_db_service
from app.models.schemas import PersonaDistributionResult
from app.models.db import PersonaDistributionDocument, AgentDetails
from app.instruction_sets.persona_distribution import PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS
from app.instruction_sets.persona_distribution_groundness_fact import PERSONA_DISTRIBUTION_GROUNDNESS_FACT_AGENT_INSTRUCTIONS

logger = structlog.get_logger()


class PersonaDistributionService:
    """Service for generating persona distributions using the Persona Distribution Generator Agent."""

    PERSONA_DISTRIBUTION_AGENT_NAME = "PersonaDistributionGeneratorAgent"
    PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS = PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS
    
    GROUNDNESS_FACT_AGENT_NAME = "PersonaDistributionGroundnessFactAgent"
    GROUNDNESS_FACT_AGENT_INSTRUCTIONS = PERSONA_DISTRIBUTION_GROUNDNESS_FACT_AGENT_INSTRUCTIONS

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

    async def _evaluate_groundness_fact(self, prompt: str, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Evaluate the groundness of the persona distribution output against the prompt.
        
        Args:
            prompt: The original input prompt
            response_text: The generated persona distribution response
            
        Returns:
            Groundness fact evaluation dict or None if evaluation fails
        """
        try:
            logger.info("="*60)
            logger.info("Starting groundness fact evaluation")
            
            # Create groundness fact agent
            logger.info("Creating Groundness Fact Agent...")
            groundness_agent = azure_ai_service.create_agent(
                agent_name=self.GROUNDNESS_FACT_AGENT_NAME,
                instructions=self.GROUNDNESS_FACT_AGENT_INSTRUCTIONS
            )
            logger.info("Groundness Fact Agent ready", agent_version=groundness_agent.agent_version_object.version)
            
            # Construct evaluation input
            evaluation_input = f"""PROMPT: {prompt}

OUTPUT: {response_text}

Evaluate the OUTPUT against the PROMPT and provide your grounding assessment."""
            
            logger.info("Creating conversation for groundness evaluation...")
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": evaluation_input}]
            )
            groundness_conversation_id = conversation.id
            logger.info("Groundness conversation created", conversation_id=groundness_conversation_id)
            
            # Get groundness evaluation
            logger.info("Requesting groundness evaluation...")
            evaluation_response = azure_ai_service.openai_client.responses.create(
                conversation=groundness_conversation_id,
                extra_body={"agent": {"name": groundness_agent.agent_version_object.name, "type": "agent_reference"}},
                input=""
            )
            logger.info("Groundness evaluation received")
            
            # Extract evaluation text
            evaluation_text = evaluation_response.output_text
            if evaluation_text is None:
                logger.error("No evaluation text found in groundness response")
                return None
            
            logger.info("Groundness evaluation completed", 
                       evaluation_length=len(evaluation_text),
                       evaluation_preview=evaluation_text[:150] + "..." if len(evaluation_text) > 150 else evaluation_text)
            
            # Parse groundness evaluation JSON
            groundness_fact = self._parse_json_output(evaluation_text)
            
            if groundness_fact:
                logger.info("Groundness fact parsed successfully",
                           score=groundness_fact.get("groundness_score"),
                           assessment=groundness_fact.get("overall_assessment"))
            
            logger.info("="*60)
            return groundness_fact
            
        except Exception as e:
            logger.error("Error evaluating groundness fact", error=str(e), exc_info=True)
            # Don't fail the entire request if groundness evaluation fails
            return None

    async def generate_persona_distribution(self, prompt: str) -> PersonaDistributionResult:
        """
        Generate a persona distribution from the given prompt.
        
        Args:
            prompt: The simulation prompt to generate persona distribution from
            
        Returns:
            PersonaDistributionResult with:
            - response_text: The generated persona distribution
            - tokens_used: Number of tokens used
            - agent_details: Details about the agent
            - timestamp: When the request was made
            - conversation_id: Conversation ID
            - parsed_output: Parsed JSON output (if successful)
        """
        try:
            logger.info("="*60)
            logger.info("Starting persona distribution generation", prompt_length=len(prompt))
            logger.debug("Prompt preview", prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt)

            # Create agent with instructions
            logger.info("Creating Persona Distribution Generator Agent...")
            agent = azure_ai_service.create_agent(
                agent_name=self.PERSONA_DISTRIBUTION_AGENT_NAME,
                instructions=self.PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS
            )
            logger.info("Persona Distribution Generator Agent ready", agent_version=agent.agent_version_object.version)

            # Create conversation with initial message
            timestamp = datetime.utcnow()
            logger.info("Creating conversation with user message...")
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": prompt}]
            )
            conversation_id = conversation.id
            logger.info("Conversation created", conversation_id=conversation_id)

            # Create response using the agent
            logger.info("Requesting response from Persona Distribution Generator Agent...")
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
            
            logger.info("Persona distribution generated successfully", 
                       response_length=len(response_text),
                       response_preview=response_text[:150] + "..." if len(response_text) > 150 else response_text)

            # Parse JSON output
            parsed_output = self._parse_json_output(response_text)

            # Evaluate groundness fact
            logger.info("Evaluating groundness fact...")
            groundness_fact = await self._evaluate_groundness_fact(prompt, response_text)

            # Extract token usage
            logger.debug("Extracting token usage...")
            tokens_used = None
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.total_tokens
                logger.info("Token usage extracted", tokens_used=tokens_used)
            else:
                logger.debug("No token usage information available")
            
            logger.info("="*60)
            logger.info("Persona distribution generation completed",
                       tokens_used=tokens_used,
                       agent_version=agent.agent_version_object.version,
                       conversation_id=conversation_id,
                       parsed_successfully=parsed_output is not None,
                       groundness_evaluated=groundness_fact is not None)
            logger.info("="*60)

            return PersonaDistributionResult(
                response_text=response_text,
                tokens_used=tokens_used,
                agent_details=agent.agent_details,
                timestamp=timestamp,
                conversation_id=conversation_id,
                parsed_output=parsed_output,
                groundness_fact=groundness_fact
            )

        except Exception as e:
            logger.error("Error generating persona distribution", error=str(e), exc_info=True)
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
        parsed_output: Optional[Dict[str, Any]],
        groundness_fact: Optional[Dict[str, Any]]
    ):
        """
        Save persona distribution generation result to database.
        
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
            groundness_fact: Groundness evaluation result (if successful)
        """
        logger.info("Saving persona distribution generation to database",
                   agent=agent_name,
                   tokens=tokens_used,
                   time_ms=round(time_taken_ms, 2),
                   conversation_id=conversation_id,
                   has_groundness_fact=groundness_fact is not None)
        
        # Create document with structure specific to persona distribution generation
        # Use conversation_id as the document ID
        agent_details = AgentDetails(
            agent_name=agent_name,
            agent_version=agent_version,
            instructions=agent_instructions,
            model_deployment_name=model,
            created_at=agent_timestamp
        )

        document = PersonaDistributionDocument(
            id=conversation_id,
            prompt=prompt,
            response=response,
            parsed_output=parsed_output,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms,
            agent_details=agent_details,
            groundness_fact=groundness_fact
        )
        
        # Use generic save method from CosmosDBService
        await cosmos_db_service.save_document(
            container_name=cosmos_db_service.PERSONA_DISTRIBUTION_CONTAINER,
            document=document
        )
        logger.info("Persona distribution generation saved successfully", document_id=conversation_id)


# Singleton instance
persona_distribution_service = PersonaDistributionService()
