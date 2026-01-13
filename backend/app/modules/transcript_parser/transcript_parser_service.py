"""Service for transcript parser use case."""

from datetime import datetime
import structlog
from typing import Optional, Dict, Any
import json

from app.infrastructure.ai.azure_ai_service import azure_ai_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from app.models.shared import AgentDetails
from .models import TranscriptParserResult, TranscriptParserDocument
from .agents import create_transcript_parser_agent

logger = structlog.get_logger()


class TranscriptParserService:
    """Service for parsing transcripts using the Transcript Parser Agent."""

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

    async def parse_transcript(self, transcript: str) -> TranscriptParserResult:
        """
        Parse a transcript to extract intent, subject, and sentiment.
        
        Args:
            transcript: The transcript text to parse
            
        Returns:
            TranscriptParserResult with:
            - response_text: The parsed result as JSON
            - tokens_used: Number of tokens used
            - agent_details: Details about the agent
            - timestamp: When the request was made
            - conversation_id: Conversation ID
            - parsed_output: Parsed JSON output (if successful)
        """
        try:
            logger.info("="*60)
            logger.info("Starting transcript parsing", transcript_length=len(transcript))
            logger.debug("Transcript preview", transcript=transcript[:200] + "..." if len(transcript) > 200 else transcript)

            # Create agent with instructions
            logger.info("Creating Transcript Parser Agent...")
            agent = create_transcript_parser_agent()
            logger.info("Transcript Parser Agent ready", agent_version=agent.agent_version_object.version)

            # Create conversation with initial message
            timestamp = datetime.utcnow()
            logger.info("Creating conversation with user message...")
            conversation = azure_ai_service.openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": transcript}]
            )
            conversation_id = conversation.id
            logger.info("Conversation created", conversation_id=conversation_id)

            # Create response using the agent
            logger.info("Requesting response from Transcript Parser Agent...")
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
            
            logger.info("Transcript parsed successfully", 
                       response_length=len(response_text),
                       response_preview=response_text[:150] + "..." if len(response_text) > 150 else response_text)

            # Parse JSON output
            parsed_output = self._parse_json_output(response_text)

            # Extract tokens used
            tokens_used = getattr(response, 'usage', None)
            if tokens_used:
                tokens_used = getattr(tokens_used, 'total_tokens', None)
            logger.info("Token usage extracted", tokens=tokens_used)

            logger.info("="*60)
            return TranscriptParserResult(
                response_text=response_text,
                tokens_used=tokens_used,
                agent_details=agent.agent_details,
                timestamp=timestamp,
                conversation_id=conversation_id,
                parsed_output=parsed_output
            )

        except Exception as e:
            logger.error("Error parsing transcript", error=str(e), exc_info=True)
            raise

    async def save_to_database(
        self,
        transcript: str,
        response: str,
        tokens_used: Optional[int],
        time_taken_ms: float,
        agent_name: str,
        agent_version: Optional[str],
        agent_instructions: str,
        model: str,
        agent_timestamp: datetime,
        conversation_id: str,
        parsed_output: Optional[Dict[str, Any]]
    ):
        """
        Save transcript parsing result to database.
        
        Args:
            transcript: The input transcript
            response: The parsing response
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
        logger.info("Saving transcript parsing to database",
                   agent=agent_name,
                   tokens=tokens_used,
                   time_ms=round(time_taken_ms, 2),
                   conversation_id=conversation_id)
        
        # Create document with structure specific to transcript parsing
        # Use conversation_id as the document ID
        agent_details = AgentDetails(
            agent_name=agent_name,
            agent_version=agent_version,
            instructions=agent_instructions,
            model_deployment_name=model,
            created_at=agent_timestamp
        )

        document = TranscriptParserDocument(
            id=conversation_id,
            transcript=transcript,
            response=response,
            parsed_output=parsed_output,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms,
            agent_details=agent_details
        )
        
        # Use generic save method from CosmosDBService
        await cosmos_db_service.save_document(
            container_name=cosmos_db_service.TRANSCRIPT_PARSER_CONTAINER,
            document=document
        )
        logger.info("Transcript parsing saved successfully", document_id=conversation_id)


# Singleton instance
transcript_parser_service = TranscriptParserService()
