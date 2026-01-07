"""Agent creation logic for Prompt Validator Agent."""

from app.services.ai.azure_ai_service import azure_ai_service
from app.instruction_sets.prompt_validator import PROMPT_VALIDATOR_AGENT_INSTRUCTIONS

PROMPT_VALIDATOR_AGENT_NAME = "PromptValidatorAgent"

def create_prompt_validator_agent():
    """Create or retrieve the Prompt Validator Agent."""
    return azure_ai_service.create_agent(
        agent_name=PROMPT_VALIDATOR_AGENT_NAME,
        instructions=PROMPT_VALIDATOR_AGENT_INSTRUCTIONS
    )
