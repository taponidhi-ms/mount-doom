"""Configuration for D365 Transcript Parser Agent."""

from ..config import AgentConfig
from ..instructions import D365_TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS

AGENT_CONFIG = AgentConfig(
    agent_id="d365_transcript_parser",
    agent_name="D365TranscriptParserAgent",
    display_name="D365 Transcript Parser",
    description="Parses HTML transcripts from Dynamics 365 Customer Service Workspace into structured conversation format with 'agent' and 'customer' roles",
    instructions=D365_TRANSCRIPT_PARSER_AGENT_INSTRUCTIONS,
    container_name="single_turn_conversations",
    scenario_name="D365TranscriptParser",
    input_field="prompt",
    input_label="HTML Transcript",
    input_placeholder="Paste the HTML transcript from Dynamics 365 Customer Service Workspace...",
    sample_inputs=[
        {
            "label": "Sample D365 Transcript",
            "value": """<!DOCTYPE html>
<html><head><title>Conversation widget</title></head>
<body><div class="webchat__basic-transcript__activity">
<div aria-labelledby="label1"><div aria-hidden="true" id="label1">You said: Hello and thank you for calling our support line.</div></div>
<div class="webchat__basic-transcript__activity-body">
<div><div class="sent-message"><div class="lcw-markdown-render">Hello and thank you for calling our support line.</div></div></div>
</div></div>
<div class="webchat__basic-transcript__activity">
<div aria-labelledby="label2"><div aria-hidden="true" id="label2">Bot CU said: I need help with my account password reset.</div></div>
<div class="webchat__basic-transcript__activity-body">
<div><div class="received-message"><div class="lcw-markdown-render">I need help with my account password reset.</div></div></div>
</div></div>
<div class="webchat__basic-transcript__activity">
<div aria-labelledby="label3"><div aria-hidden="true" id="label3">You said: I can help you with that. What is your account email?</div></div>
<div class="webchat__basic-transcript__activity-body">
<div><div class="sent-message"><div class="lcw-markdown-render">I can help you with that. What is your account email?</div></div></div>
</div></div>
<div class="webchat__basic-transcript__activity">
<div aria-labelledby="label4"><div aria-hidden="true" id="label4">Bot CU said: My email is customer@example.com</div></div>
<div class="webchat__basic-transcript__activity-body">
<div><div class="received-message"><div class="lcw-markdown-render">My email is customer@example.com</div></div></div>
</div></div></body></html>""",
            "category": "Valid",
            "tags": ["password-reset", "account-support"]
        }
    ]
)
