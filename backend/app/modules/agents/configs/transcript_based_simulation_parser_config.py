"""Configuration for Transcript Based Simulation Parser Agent."""

from ..config import AgentConfig
from ..instructions import TRANSCRIPT_BASED_SIMULATION_PARSER_AGENT_INSTRUCTIONS


# Define agent configuration
AGENT_CONFIG = AgentConfig(
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
            "category": "Valid",
            "tags": ["multiple-conversations", "guid-extraction", "phone-extraction"]
        },
        {
            "label": "Two conversation IDs with different format",
            "value": "Run transcript based simulation for Conversation IDs: 6d14de35-58ae-f011-bbd3-000d3a33b1cc, 7614de35-58ae-f011-bbd3-000d3a33b1cc against target number +19876543210",
            "category": "Valid",
            "tags": ["two-conversations", "format-variation", "guid-parsing"]
        },
        {
            "label": "Single conversation with target",
            "value": "Simulate transcript for conversation ID 1c47463d-58ae-f011-bbd3-000d3a33b1cc to phone number +14155552671",
            "category": "Valid",
            "tags": ["single-conversation", "simple-case", "guid-extraction"]
        },
        {
            "label": "Multiple IDs with international phone",
            "value": "Transcript based simulation for given Conversation IDs 7f14de35-58ae-f011-bbd3-000d3a33b1cc, 1c47463d-58ae-f011-bbd3-000d3a33b1cc, dd7a8a94-a0a2-f011-bbd3-0022480c3dbb and do it with this target phone number +447911123456",
            "category": "Valid",
            "tags": ["multiple-conversations", "international-phone", "uk-number", "guid-list"]
        },
    ]
)
