"""Agent creation logic for Persona Generator Agent."""

from app.infrastructure.ai.azure_ai_service import azure_ai_service
from .instructions import PERSONA_GENERATOR_AGENT_INSTRUCTIONS

PERSONA_GENERATOR_AGENT_NAME = "PersonaGeneratorAgent"

def create_persona_generator_agent():
    """Create or retrieve the Persona Generator Agent."""
    return azure_ai_service.create_agent(
        agent_name=PERSONA_GENERATOR_AGENT_NAME,
        instructions=PERSONA_GENERATOR_AGENT_INSTRUCTIONS
    )
