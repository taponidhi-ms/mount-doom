"""Agent creation logic for C2 Message Generator Agent."""

from app.infrastructure.ai.azure_ai_service import azure_ai_service
from .instructions import C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS

C2_MESSAGE_GENERATOR_AGENT_NAME = "C2MessageGeneratorAgent"

def create_c2_message_generator_agent():
    """Create or retrieve the C2 Message Generator Agent (Customer)."""
    return azure_ai_service.create_agent(
        agent_name=C2_MESSAGE_GENERATOR_AGENT_NAME,
        instructions=C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS
    )
