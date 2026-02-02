"""Configuration for Persona Generator Agent."""

from ..config import AgentConfig
from ..instructions import PERSONA_GENERATOR_AGENT_INSTRUCTIONS


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
    sample_inputs=[
        {
            "label": "Technical support personas with varied sentiments",
            "value": "Generate 5 personas for technical support with varied sentiments (Frustrated, Confused, Angry) regarding internet connectivity issues.",
            "category": "Valid",
            "tags": ["technical-support", "internet", "negative-sentiments", "connectivity"]
        },
        {
            "label": "Travel agency personas",
            "value": "I need 3 personas for a travel agency. One planning a honeymoon (Happy), one cancelling a trip due to illness (Sad), and one inquiring about visa requirements (Neutral).",
            "category": "Valid",
            "tags": ["travel", "multi-sentiment", "specific-scenarios", "honeymoon", "visa"]
        },
        {
            "label": "E-commerce return personas with metadata",
            "value": "Create 4 personas for an e-commerce return process. Include metadata like 'OrderValue', 'CustomerLoyaltyTier', and 'ReturnReason'.",
            "category": "Valid",
            "tags": ["e-commerce", "returns", "metadata-rich", "loyalty"]
        },
    ]
)
