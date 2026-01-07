from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.shared import BaseRequest, BaseDocument

class GeneralPromptRequest(BaseRequest):
    """Request for general prompt use case."""
    prompt: str

class GeneralPromptResponse(BaseModel):
    """Response for general prompt use case (no agent, direct model)."""
    model_deployment_name: str
    response_text: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    start_time: datetime
    end_time: datetime

class GeneralPromptResult(BaseModel):
    """Result from GeneralPromptService.generate_response method."""
    response_text: str
    tokens_used: Optional[int] = None
    conversation_id: str

class GeneralPromptDocument(BaseDocument):
    """Document for general prompt."""
    prompt: str
    response: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    model_deployment_name: str
