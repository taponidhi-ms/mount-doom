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
    C1_AGENT_INSTRUCTIONS,
    SIMULATION_PROMPT_VALIDATING_AGENT_INSTRUCTIONS,
    TRANSCRIPT_BASED_SIMULATION_PARSER_AGENT_INSTRUCTIONS,
    SIMULATION_PROMPT_AGENT_INSTRUCTIONS,
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
    scenario_name: str = ""  # Scenario name for eval downloads (defaults to agent_name if not set)
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
        container_name="single_turn_conversations",
        scenario_name="PersonaDistributionGeneratorAgent",
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
        container_name="single_turn_conversations",
        scenario_name="PersonaGeneratorAgent",
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
        container_name="single_turn_conversations",
        scenario_name="TranscriptParserAgent",
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
        container_name="single_turn_conversations",
        scenario_name="C2MessageGeneratorAgent",
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
    "c1_message_generation": AgentConfig(
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
            },
            {
                "label": "Empathetic response to billing complaint",
                "value": "Generate a service representative's response to a customer complaining about an incorrect charge. Show empathy and offer to investigate.",
            },
            {
                "label": "Technical support guidance",
                "value": "Generate a representative's response helping a customer troubleshoot their internet connection. Be patient and provide clear guidance.",
            },
            {
                "label": "Resolution confirmation",
                "value": "Generate a representative's message confirming that a customer's issue has been resolved and asking if there's anything else they can help with.",
            },
        ],
    ),
    "simulation_prompt_validator": AgentConfig(
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
            },
            {
                "label": "Invalid: ConvCount exceeds limit",
                "value": '{"ConvCount":100,"Caller":"+18005551234","Recipient":"+18005559876"}',
            },
            {
                "label": "Invalid: Missing phone numbers",
                "value": '{"ConvCount":10,"Caller":"","Recipient":""}',
            },
            {
                "label": "Invalid: Same caller and recipient",
                "value": '{"ConvCount":10,"Caller":"+18007770999","Recipient":"+18007770999"}',
            },
            {
                "label": "Invalid: Malformed phone numbers",
                "value": '{"ConvCount":5,"Caller":"+1800-555-1234","Recipient":"+185555394A2"}',
            },
        ],
    ),
    "transcript_based_simulation_parser": AgentConfig(
        agent_id="transcript_based_simulation_parser",
        agent_name="TranscriptBasedSimulationParserAgent",
        display_name="Transcript Based Simulation Parser",
        description="Extract conversation GUIDs and target phone numbers from transcript-based simulation requests. Returns structured JSON with targetPhoneNumber and conversationIDs.",
        instructions=TRANSCRIPT_BASED_SIMULATION_PARSER_AGENT_INSTRUCTIONS,
        container_name="single_turn_conversations",
        scenario_name="TranscriptBasedSimulationParserAgent",
        input_field="prompt",
        input_label="Input Message",
        input_placeholder="Enter message with conversation IDs and target phone number (e.g., 'Simulate based on conversations...')...",
        sample_inputs=[
            {
                "label": "Multiple conversation IDs with target phone",
                "value": "Simulate based on these conversations' transcripts against number +18556215741. Conversation IDs are: 4d8dda54-029a-f011-bbd3-6045bd04d7c7, 37dc7b0c-d300-40a2-9746-2cf981e04316, fea51dd0-cabd-e56c-bd02-c7865f78eef1",
            },
            {
                "label": "Two conversation IDs with different format",
                "value": "Run transcript based simulation for Conversation IDs: 6d14de35-58ae-f011-bbd3-000d3a33b1cc, 7614de35-58ae-f011-bbd3-000d3a33b1cc against target number +19876543210",
            },
            {
                "label": "Single conversation with target",
                "value": "Simulate transcript for conversation ID 1c47463d-58ae-f011-bbd3-000d3a33b1cc to phone number +14155552671",
            },
            {
                "label": "Multiple IDs with international phone",
                "value": "Transcript based simulation for given Conversation IDs 7f14de35-58ae-f011-bbd3-000d3a33b1cc, 1c47463d-58ae-f011-bbd3-000d3a33b1cc, dd7a8a94-a0a2-f011-bbd3-0022480c3dbb and do it with this target phone number +447911123456",
            },
        ],
    ),
    "simulation_prompt": AgentConfig(
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
            },
            {
                "label": "Detailed simulation with parameters",
                "value": "Run a simulation of 25 conversations where customers call about product returns. 60% should be frustrated, 40% should be neutral.",
            },
            {
                "label": "Transcript-based simulation",
                "value": "Simulate based on transcript from conversation ID abc123 to phone number +18005551234",
            },
            {
                "label": "Non-simulation request (should reject)",
                "value": "What is the weather like today?",
            },
            {
                "label": "Technical support simulation",
                "value": "I need to simulate 15 technical support calls about internet connectivity issues",
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
