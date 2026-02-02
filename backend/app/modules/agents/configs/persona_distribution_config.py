"""Configuration for Persona Distribution Generator Agent."""

from ..config import AgentConfig
from ..instructions import PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS
from .shared_sample_inputs import SIMULATION_SAMPLE_INPUTS


# Define agent configuration
AGENT_CONFIG = AgentConfig(
    agent_id="persona_distribution",
    agent_name="PersonaDistributionGeneratorAgent",
    display_name="Persona Distribution Generator",
    description="Generate persona distributions from simulation prompts. Outputs structured JSON with conversation counts, intents, sentiments, and proportions.",
    instructions=PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS,
    container_name="single_turn_conversations",
    scenario_name="PersonaDistributionGeneratorAgent",
    input_field="prompt",
    input_label="Simulation Prompt",
    input_placeholder="Describe the persona distribution you want to generate (e.g., number of calls, intents, sentiments)...",
    sample_inputs=SIMULATION_SAMPLE_INPUTS  # Use shared sample inputs
)
