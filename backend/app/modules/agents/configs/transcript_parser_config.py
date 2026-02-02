"""Configuration for Transcript Parser Agent."""

from ..config import AgentConfig
from ..instructions import TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS


# Define agent configuration
AGENT_CONFIG = AgentConfig(
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
            "category": "Valid",
            "tags": ["phone-upgrade", "website-error", "urgent", "resolved"]
        },
        {
            "label": "Damaged product complaint",
            "value": "Customer: I just received my order but the device is damaged. I'm really frustrated! Rep: I sincerely apologize for the inconvenience. Can you describe the damage? Customer: The screen has cracks and it won't turn on. This is unacceptable! Rep: You're absolutely right. I'll process a replacement immediately at no cost to you.",
            "category": "Valid",
            "tags": ["product-damage", "complaint", "frustrated", "replacement", "negative-sentiment"]
        },
        {
            "label": "Account balance inquiry",
            "value": "Customer: Could you help me understand how to access my account balance? Rep: Of course! I'd be happy to help. You can log in to your account... Customer: Okay, got it. Thank you for walking me through this. Rep: You're welcome! Is there anything else I can assist with? Customer: No, that's all. Have a good day! Rep: You too!",
            "category": "Valid",
            "tags": ["account-inquiry", "simple", "positive-sentiment", "resolved", "polite"]
        },
    ]
)
