"""Configuration for Simulation Prompt Validator Agent."""

from ..config import AgentConfig
from ..instructions import SIMULATION_PROMPT_VALIDATING_AGENT_INSTRUCTIONS
from .shared_validator_sample_inputs import VALIDATOR_SAMPLE_INPUTS


# Define agent configuration
AGENT_CONFIG = AgentConfig(
    agent_id="simulation_prompt_validator",
    agent_name="SimulationPromptValidatingAgent",
    display_name="Simulation Prompt Validator",
    description="Validate simulation JSON prompts for caller/recipient phone number formats, phone number uniqueness, and ConvCount limits. Returns validation errors or empty array if valid.",
    instructions=SIMULATION_PROMPT_VALIDATING_AGENT_INSTRUCTIONS,
    container_name="single_turn_conversations",
    scenario_name="SimulationPromptValidatingAgent",
    input_field="prompt",
    input_label="JSON Input",
    input_placeholder='Enter JSON to validate (e.g., {"ConvCount":10,"intents":[...],"Sentiments":[...],"Proportions":[...]})...',
    sample_inputs=VALIDATOR_SAMPLE_INPUTS  # Use shared sample inputs from persona distribution responses
)
