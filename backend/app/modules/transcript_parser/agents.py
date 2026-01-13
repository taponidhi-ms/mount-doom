"""Agent creation logic for Transcript Parser Agent."""

from app.infrastructure.ai.azure_ai_service import azure_ai_service
from .instructions import TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS

TRANSCRIPT_PARSER_AGENT_NAME = "TranscriptParserAgent"

def create_transcript_parser_agent():
    """Create or retrieve the Transcript Parser Agent."""
    return azure_ai_service.create_agent(
        agent_name=TRANSCRIPT_PARSER_AGENT_NAME,
        instructions=TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS
    )
