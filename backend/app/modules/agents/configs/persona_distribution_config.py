"""Configuration for Persona Distribution Generator Agent."""

from ..config import AgentConfig
from ..instructions import PERSONA_DISTRIBUTION_AGENT_INSTRUCTIONS


# Define agent configuration
AGENT_CONFIG = AgentConfig(
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
            "category": "Valid",
            "tags": ["telecom", "billing", "technical-support", "multi-intent"]
        },
        {
            "label": "Retail bank customer service",
            "value": "Create a persona distribution for a retail bank's customer service. I need 50 conversations about credit card disputes, 30 about loan applications, and 20 about account balance checks.",
            "category": "Valid",
            "tags": ["banking", "financial-services", "credit-card", "loans"]
        },
        {
            "label": "Healthcare appointment scheduling",
            "value": "Simulate a healthcare provider's appointment line. 40% scheduling new appointments, 40% rescheduling existing ones, and 20% cancelling. Most callers should be anxious or neutral.",
            "category": "Valid",
            "tags": ["healthcare", "appointments", "scheduling", "sentiment-focused"]
        },
    ]
)
