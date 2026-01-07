"""Agent creation logic for C2 Agent (Customer)."""

from app.services.ai.azure_ai_service import azure_ai_service
from app.instruction_sets.c2_agent import C2_AGENT_INSTRUCTIONS

C2_AGENT_NAME = "C2Agent"

def create_c2_agent():
    """Create or retrieve the C2 Agent (Customer)."""
    return azure_ai_service.create_agent(
        agent_name=C2_AGENT_NAME,
        instructions=C2_AGENT_INSTRUCTIONS
    )
