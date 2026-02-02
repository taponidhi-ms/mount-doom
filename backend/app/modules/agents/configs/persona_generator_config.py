"""Configuration for Persona Generator Agent."""

from ..config import AgentConfig
from ..instructions import PERSONA_GENERATOR_AGENT_INSTRUCTIONS
from .shared_sample_inputs import SIMULATION_SAMPLE_INPUTS


# Define agent configuration
AGENT_CONFIG = AgentConfig(
    agent_id="persona_generator",
    agent_name="PersonaGeneratorAgent",
    display_name="Persona Generator",
    description="Generate exact customer personas with specific intents, sentiments, subjects, and metadata for conversation simulations.",
    instructions=PERSONA_GENERATOR_AGENT_INSTRUCTIONS,
    container_name="single_turn_conversations",
    scenario_name="PersonaGeneratorAgent",
    input_field="prompt",
    input_label="Prompt",
    input_placeholder="Describe the personas you want to generate (e.g., 'Generate 5 personas for technical support')...",
    sample_inputs=SIMULATION_SAMPLE_INPUTS  # Use shared sample inputs
)
