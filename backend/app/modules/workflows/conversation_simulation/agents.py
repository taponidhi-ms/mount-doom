"""Agent creation logic for Conversation Simulation Workflow."""

from app.infrastructure.ai.azure_ai_service import azure_ai_service
from app.modules.agents.instructions import C1_AGENT_INSTRUCTIONS, C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS

C1_MESSAGE_GENERATOR_AGENT_NAME = "C1MessageGeneratorAgent"
C2_MESSAGE_GENERATOR_AGENT_NAME = "C2MessageGeneratorAgent"


def create_c1_agent():
    """Create or retrieve the C1 Agent (Service Representative)."""
    return azure_ai_service.create_agent(
        agent_name=C1_MESSAGE_GENERATOR_AGENT_NAME,
        instructions=C1_AGENT_INSTRUCTIONS
    )


def create_c2_agent():
    """Create or retrieve the C2 Agent (Customer)."""
    return azure_ai_service.create_agent(
        agent_name=C2_MESSAGE_GENERATOR_AGENT_NAME,
        instructions=C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS
    )
