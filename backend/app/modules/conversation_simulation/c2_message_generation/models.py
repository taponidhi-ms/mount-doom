"""Models for C2 Message Generation use case."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel
from app.models.shared import BaseRequest, BaseResponse, AgentDetails, BaseDocument


class C2MessageGenerationRequest(BaseRequest):
    """Request for C2 message generation use case."""
    prompt: str


class C2MessageGenerationResponse(BaseResponse):
    """Response for C2 message generation use case."""
    pass


class C2MessageGenerationResult(BaseModel):
    """Result from C2MessageGenerationService.generate_message method."""
    response_text: str
    tokens_used: Optional[int] = None
    agent_details: AgentDetails
    timestamp: datetime
    conversation_id: str


class C2MessageGenerationDocument(BaseDocument):
    """Document for C2 message generation."""
    prompt: str
    response: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    agent_details: AgentDetails
