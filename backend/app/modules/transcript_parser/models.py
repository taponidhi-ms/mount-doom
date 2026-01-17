from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.models.shared import BaseRequest, BaseResponse, AgentDetails, BaseDocument

class TranscriptParserRequest(BaseRequest):
    """Request for transcript parser feature."""
    transcript: str

class TranscriptParserResponse(BaseResponse):
    """Response for transcript parser feature."""
    parsed_output: Optional[Dict[str, Any]] = None

class TranscriptParserResult(BaseModel):
    """Result from TranscriptParserService.parse_transcript method."""
    response_text: str
    tokens_used: Optional[int] = None
    agent_details: AgentDetails
    timestamp: datetime
    conversation_id: str
    parsed_output: Optional[Dict[str, Any]] = None

class TranscriptParserDocument(BaseDocument):
    """Document for transcript parsing."""
    transcript: str
    response: str
    parsed_output: Optional[Dict[str, Any]] = None
    tokens_used: Optional[int] = None
    time_taken_ms: float
    agent_details: AgentDetails
