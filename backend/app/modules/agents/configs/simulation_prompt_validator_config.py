"""Configuration for Simulation Prompt Validator Agent."""

from ..config import AgentConfig
from ..instructions import SIMULATION_PROMPT_VALIDATING_AGENT_INSTRUCTIONS


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
    input_placeholder='Enter JSON to validate (e.g., {"ConvCount":10,"Caller":"+18005551234","Recipient":"+18005559876"})...',
    sample_inputs=[
        {
            "label": "Valid JSON with all required fields",
            "value": '{"ConvCount":10,"Caller":"+18005551234","Recipient":"+18005559876"}',
            "category": "Valid",
            "tags": ["valid-format", "phone-numbers", "count-limit"]
        },
        {
            "label": "Invalid: ConvCount exceeds limit",
            "value": '{"ConvCount":100,"Caller":"+18005551234","Recipient":"+18005559876"}',
            "category": "Invalid",
            "tags": ["count-exceeded", "validation-error", "limit-test"]
        },
        {
            "label": "Invalid: Missing phone numbers",
            "value": '{"ConvCount":10,"Caller":"","Recipient":""}',
            "category": "Invalid",
            "tags": ["missing-data", "validation-error", "empty-fields"]
        },
        {
            "label": "Invalid: Same caller and recipient",
            "value": '{"ConvCount":10,"Caller":"+18007770999","Recipient":"+18007770999"}',
            "category": "Invalid",
            "tags": ["duplicate-numbers", "validation-error", "uniqueness-test"]
        },
        {
            "label": "Invalid: Malformed phone numbers",
            "value": '{"ConvCount":5,"Caller":"+1800-555-1234","Recipient":"+185555394A2"}',
            "category": "Invalid",
            "tags": ["malformed-format", "validation-error", "format-test"]
        },
    ]
)
