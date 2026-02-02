"""Configuration for C1 Message Generation Agent."""

from ..config import AgentConfig
from ..instructions import C1_AGENT_INSTRUCTIONS


# Define agent configuration
AGENT_CONFIG = AgentConfig(
    agent_id="c1_message_generation",
    agent_name="C1MessageGeneratorAgent",
    display_name="C1 Message Generator",
    description="Generate customer service representative (C1) messages for conversation simulations. Simulates professional, empathetic service responses.",
    instructions=C1_AGENT_INSTRUCTIONS,
    container_name="single_turn_conversations",
    scenario_name="C1MessageGeneratorAgent",
    input_field="prompt",
    input_label="Context Prompt",
    input_placeholder="Enter the conversation context for generating a service representative response...",
    sample_inputs=[
        {
            "label": "Professional greeting and assistance offer",
            "value": "Generate an opening message from a customer service representative greeting a customer and offering assistance.",
            "category": "Valid",
            "tags": ["greeting", "professional", "opening", "polite"]
        },
        {
            "label": "Empathetic response to billing complaint",
            "value": "Generate a service representative's response to a customer complaining about an incorrect charge. Show empathy and offer to investigate.",
            "category": "Valid",
            "tags": ["billing", "empathy", "complaint-response", "investigation"]
        },
        {
            "label": "Technical support guidance",
            "value": "Generate a representative's response helping a customer troubleshoot their internet connection. Be patient and provide clear guidance.",
            "category": "Valid",
            "tags": ["technical-support", "troubleshooting", "patient", "guidance", "internet"]
        },
        {
            "label": "Resolution confirmation",
            "value": "Generate a representative's message confirming that a customer's issue has been resolved and asking if there's anything else they can help with.",
            "category": "Valid",
            "tags": ["resolution", "confirmation", "closing", "follow-up"]
        },
    ]
)
