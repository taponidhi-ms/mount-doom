"""Configuration for C2 Message Generation Agent."""

from ..config import AgentConfig
from ..instructions import C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS


# Define agent configuration
AGENT_CONFIG = AgentConfig(
    agent_id="c2_message_generation",
    agent_name="C2MessageGeneratorAgent",
    display_name="C2 Message Generator",
    description="Generate customer (C2) messages for use in conversation simulations. Simulates realistic customer responses.",
    instructions=C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS,
    container_name="single_turn_conversations",
    scenario_name="C2MessageGeneratorAgent",
    input_field="prompt",
    input_label="Context Prompt",
    input_placeholder="Enter the conversation context for generating a customer message...",
    sample_inputs=[
        {
            "label": "Frustrated customer with billing issue",
            "value": "Generate a customer message expressing frustration about an incorrect charge on their bill. The customer should be upset but not rude.",
            "category": "Valid",
            "tags": ["billing", "frustrated", "negative-sentiment", "complaint"]
        },
        {
            "label": "Happy customer with service inquiry",
            "value": "Generate a positive customer message asking about upgrading their service plan. The customer should be enthusiastic and curious.",
            "category": "Valid",
            "tags": ["service-upgrade", "positive-sentiment", "inquiry", "enthusiastic"]
        },
        {
            "label": "Confused customer needing technical help",
            "value": "Generate a customer message from someone confused about how to set up their new device. They should be patient but clearly need step-by-step guidance.",
            "category": "Valid",
            "tags": ["technical-support", "confused", "neutral-sentiment", "patient", "device-setup"]
        },
    ]
)
