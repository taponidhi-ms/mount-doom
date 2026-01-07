"""Agent creation logic for Persona Distribution Generator Agent."""

from app.infrastructure.ai.azure_ai_service import azure_ai_service
from .instructions import PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS

PERSONA_DISTRIBUTION_AGENT_NAME = "PersonaDistributionGeneratorAgent"

def create_persona_distribution_agent():
    """Create or retrieve the Persona Distribution Generator Agent."""
    return azure_ai_service.create_agent(
        agent_name=PERSONA_DISTRIBUTION_AGENT_NAME,
        instructions=PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS
    )
