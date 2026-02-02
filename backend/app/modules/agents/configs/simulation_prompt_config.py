"""Configuration for Simulation Prompt Agent."""

from ..config import AgentConfig
from ..instructions import SIMULATION_PROMPT_AGENT_INSTRUCTIONS


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
    sample_inputs=[
        {
            "label": "Basic simulation request",
            "value": "Simulate 10 customer service calls about billing issues",
            "category": "Valid",
            "tags": ["simulation", "billing", "customer-service", "simple"]
        },
        {
            "label": "Detailed simulation with parameters",
            "value": "Run a simulation of 25 conversations where customers call about product returns. 60% should be frustrated, 40% should be neutral.",
            "category": "Valid",
            "tags": ["simulation", "returns", "sentiment-specified", "detailed"]
        },
        {
            "label": "Transcript-based simulation",
            "value": "Simulate based on transcript from conversation ID abc123 to phone number +18005551234",
            "category": "Valid",
            "tags": ["simulation", "transcript-based", "conversation-id"]
        },
        {
            "label": "Non-simulation request (should reject)",
            "value": "What is the weather like today?",
            "category": "Invalid",
            "tags": ["non-simulation", "rejection-test", "weather-query"]
        },
        {
            "label": "Technical support simulation",
            "value": "I need to simulate 15 technical support calls about internet connectivity issues",
            "category": "Valid",
            "tags": ["simulation", "technical-support", "internet", "connectivity"]
        },
    ]
)
