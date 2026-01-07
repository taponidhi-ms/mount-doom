"""Agent creation logic for C1 Agent (Service Representative)."""

from app.services.ai.azure_ai_service import azure_ai_service
from app.instruction_sets.c1_agent import C1_AGENT_INSTRUCTIONS

C1_AGENT_NAME = "C1Agent"

def create_c1_agent():
    """Create or retrieve the C1 Agent (Service Representative)."""
    return azure_ai_service.create_agent(
        agent_name=C1_AGENT_NAME,
        instructions=C1_AGENT_INSTRUCTIONS
    )
