from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.shared import BaseRequest, BaseResponse, AgentDetails, BaseDocument

class PromptValidatorRequest(BaseRequest):
    """Request for prompt validator use case."""
    prompt: str

class PromptValidatorResponse(BaseResponse):
    """Response for prompt validator use case."""
    pass

class PromptValidatorResult(BaseModel):
    """Result from PromptValidatorService.validate_prompt method."""
    response_text: str
    tokens_used: Optional[int] = None
    agent_details: AgentDetails
    timestamp: datetime
    conversation_id: str

class PromptValidatorDocument(BaseDocument):
    """Document for prompt validation."""
    prompt: str
    response: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    agent_details: AgentDetails
