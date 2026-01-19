"""
Agent Configuration Registry.

This module maintains configurations for all agents in the system.
Each agent is defined with its name, description, instructions, and container.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Import instructions from centralized instructions module
from .instructions import (
    PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS,
    PERSONA_GENERATOR_AGENT_INSTRUCTIONS,
    TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS,
    C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS,
)


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    agent_id: str
    agent_name: str
    display_name: str
    description: str
    instructions: str
    container_name: str
    input_field: str = "prompt"  # UI field identifier (used for frontend only, DB always uses "prompt")
    input_label: str = "Prompt"  # Display label for the input field
    input_placeholder: str = "Enter your prompt..."  # Placeholder for input
    sample_inputs: List[Dict[str, str]] = field(default_factory=list)  # Sample inputs for the UI


# Agent Registry - All single agents are defined here
AGENT_REGISTRY: Dict[str, AgentConfig] = {
    "persona_distribution": AgentConfig(
        agent_id="persona_distribution",
        agent_name="PersonaDistributionGeneratorAgent",
        display_name="Persona Distribution Generator",
        description="Generate persona distributions from simulation prompts. Outputs structured JSON with conversation counts, intents, sentiments, and proportions.",
        instructions=PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS,
        container_name="persona_distribution",
        input_field="prompt",
        input_label="Simulation Prompt",
        input_placeholder="Describe the persona distribution you want to generate (e.g., number of calls, intents, sentiments)...",
        sample_inputs=[
            {
                "label": "Telecom billing and technical support mix",
                "value": "Generate a distribution of 100 calls for a telecom company where 60% are billing inquiries (mostly negative sentiment), 30% are technical support (mixed sentiment), and 10% are new service requests (positive sentiment).",
            },
            {
                "label": "Retail bank customer service",
                "value": "Create a persona distribution for a retail bank's customer service. I need 50 conversations about credit card disputes, 30 about loan applications, and 20 about account balance checks.",
            },
            {
                "label": "Healthcare appointment scheduling",
                "value": "Simulate a healthcare provider's appointment line. 40% scheduling new appointments, 40% rescheduling existing ones, and 20% cancelling. Most callers should be anxious or neutral.",
            },
        ],
    ),
    "persona_generator": AgentConfig(
        agent_id="persona_generator",
        agent_name="PersonaGeneratorAgent",
        display_name="Persona Generator",
        description="Generate exact customer personas with specific intents, sentiments, subjects, and metadata for conversation simulations.",
        instructions=PERSONA_GENERATOR_AGENT_INSTRUCTIONS,
        container_name="persona_generator",
        input_field="prompt",
        input_label="Prompt",
        input_placeholder="Describe the personas you want to generate (e.g., 'Generate 5 personas for technical support')...",
        sample_inputs=[
            {
                "label": "Technical support personas with varied sentiments",
                "value": "Generate 5 personas for technical support with varied sentiments (Frustrated, Confused, Angry) regarding internet connectivity issues.",
            },
            {
                "label": "Travel agency personas",
                "value": "I need 3 personas for a travel agency. One planning a honeymoon (Happy), one cancelling a trip due to illness (Sad), and one inquiring about visa requirements (Neutral).",
            },
            {
                "label": "E-commerce return personas with metadata",
                "value": "Create 4 personas for an e-commerce return process. Include metadata like 'OrderValue', 'CustomerLoyaltyTier', and 'ReturnReason'.",
            },
        ],
    ),
    "transcript_parser": AgentConfig(
        agent_id="transcript_parser",
        agent_name="TranscriptParserAgent",
        display_name="Transcript Parser",
        description="Parse customer-representative transcripts to extract intent, subject, and sentiment from conversations.",
        instructions=TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS,
        container_name="transcript_parser",
        input_field="transcript",
        input_label="Transcript",
        input_placeholder="Paste the customer-representative conversation transcript to analyze...",
        sample_inputs=[
            {
                "label": "Phone upgrade inquiry",
                "value": "Customer: Hi, I've been trying to upgrade my phone plan but the website keeps giving me errors. Rep: I'm sorry about that. Let me look into this for you. When did you first encounter the error? Customer: This morning, around 10 AM. I really need this done today. Rep: I understand your urgency. I'm checking now... Ah, I found the issue. Let me process this manually for you.",
            },
            {
                "label": "Damaged product complaint",
                "value": "Customer: I just received my order but the device is damaged. I'm really frustrated! Rep: I sincerely apologize for the inconvenience. Can you describe the damage? Customer: The screen has cracks and it won't turn on. This is unacceptable! Rep: You're absolutely right. I'll process a replacement immediately at no cost to you.",
            },
            {
                "label": "Account balance inquiry",
                "value": "Customer: Could you help me understand how to access my account balance? Rep: Of course! I'd be happy to help. You can log in to your account... Customer: Okay, got it. Thank you for walking me through this. Rep: You're welcome! Is there anything else I can assist with? Customer: No, that's all. Have a good day! Rep: You too!",
            },
        ],
    ),
    "c2_message_generation": AgentConfig(
        agent_id="c2_message_generation",
        agent_name="C2MessageGeneratorAgent",
        display_name="C2 Message Generator",
        description="Generate customer (C2) messages for use in conversation simulations. Simulates realistic customer responses.",
        instructions=C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS,
        container_name="c2_message_generation",
        input_field="prompt",
        input_label="Context Prompt",
        input_placeholder="Enter the conversation context for generating a customer message...",
        sample_inputs=[
            {
                "label": "Frustrated customer with billing issue",
                "value": "Generate a customer message expressing frustration about an incorrect charge on their bill. The customer should be upset but not rude.",
            },
            {
                "label": "Happy customer with service inquiry",
                "value": "Generate a positive customer message asking about upgrading their service plan. The customer should be enthusiastic and curious.",
            },
            {
                "label": "Confused customer needing technical help",
                "value": "Generate a customer message from someone confused about how to set up their new device. They should be patient but clearly need step-by-step guidance.",
            },
        ],
    ),
}


def get_agent_config(agent_id: str) -> Optional[AgentConfig]:
    """Get agent configuration by ID."""
    return AGENT_REGISTRY.get(agent_id)


def get_all_agents() -> Dict[str, AgentConfig]:
    """Get all agent configurations."""
    return AGENT_REGISTRY


def list_agent_ids() -> List[str]:
    """Get list of all agent IDs."""
    return list(AGENT_REGISTRY.keys())
