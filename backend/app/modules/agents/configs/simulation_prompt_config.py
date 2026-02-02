"""Configuration for Simulation Prompt Agent."""

from ..config import AgentConfig
from ..instructions import SIMULATION_PROMPT_AGENT_INSTRUCTIONS
from .shared_sample_inputs import SIMULATION_SAMPLE_INPUTS


# Define agent configuration
AGENT_CONFIG = AgentConfig(
    agent_id="simulation_prompt",
    agent_name="SimulationPromptAgent",
    display_name="Simulation Prompt",
    description="Detect simulation requests and respond with 'RunSimulation' for valid prompts. Rejects non-simulation requests and inappropriate content.",
    instructions=SIMULATION_PROMPT_AGENT_INSTRUCTIONS,
    container_name="single_turn_conversations",
    scenario_name="SimulationPromptAgent",
    input_field="prompt",
    input_label="Prompt",
    input_placeholder="Enter a simulation request (e.g., 'Simulate 10 customer service calls about billing issues')...",
    sample_inputs=SIMULATION_SAMPLE_INPUTS  # Use shared sample inputs
)
