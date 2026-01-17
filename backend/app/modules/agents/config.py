"""
Agent Configuration Registry.

This module maintains configurations for all agents in the system.
Each agent is defined with its name, description, instructions, and container.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field

# Import instructions from existing modules
from app.modules.persona_distribution.instructions import PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS
from app.modules.persona_generator.instructions import PERSONA_GENERATOR_AGENT_INSTRUCTIONS
from app.modules.transcript_parser.instructions import TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS
from app.modules.c2_message_generation.instructions import C2_MESSAGE_GENERATOR_AGENT_INSTRUCTIONS


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    agent_id: str
    agent_name: str
    display_name: str
    description: str
    instructions: str
    container_name: str
    input_field: str = "prompt"  # The field name for input (prompt or transcript)
    input_label: str = "Prompt"  # Display label for the input field
    input_placeholder: str = "Enter your prompt..."  # Placeholder for input


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
    ),
}


def get_agent_config(agent_id: str) -> Optional[AgentConfig]:
    """Get agent configuration by ID."""
    return AGENT_REGISTRY.get(agent_id)


def get_all_agents() -> Dict[str, AgentConfig]:
    """Get all agent configurations."""
    return AGENT_REGISTRY


def list_agent_ids() -> list[str]:
    """Get list of all agent IDs."""
    return list(AGENT_REGISTRY.keys())
