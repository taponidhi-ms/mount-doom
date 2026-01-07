"""Agent creation logic for General Prompt Agent."""

from app.services.ai.azure_ai_service import azure_ai_service

GENERAL_PROMPT_AGENT_NAME = "GeneralPromptAgent"
GENERAL_PROMPT_INSTRUCTIONS = "You are a helpful assistant that answers general questions"

def create_general_prompt_agent():
    """Create or retrieve the General Prompt Agent."""
    return azure_ai_service.create_agent(
        agent_name=GENERAL_PROMPT_AGENT_NAME,
        instructions=GENERAL_PROMPT_INSTRUCTIONS
    )
