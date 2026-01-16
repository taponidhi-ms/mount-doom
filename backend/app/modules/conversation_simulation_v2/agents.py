"""Agent creation logic for Conversation Simulation Agents V2."""

from app.infrastructure.ai.azure_ai_service import azure_ai_service
from .instructions import C1_AGENT_INSTRUCTIONS

C1_MESSAGE_GENERATOR_AGENT_NAME = "C1MessageGeneratorAgent"

def create_c1_agent():
    """Create or retrieve the C1 Agent (Service Representative) for V2."""
    return azure_ai_service.create_agent(
        agent_name=C1_MESSAGE_GENERATOR_AGENT_NAME,
        instructions=C1_AGENT_INSTRUCTIONS
    )
