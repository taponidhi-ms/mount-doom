from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.models.shared import BaseRequest, BaseResponse, AgentDetails, BaseDocument

class PersonaGeneratorRequest(BaseRequest):
    """Request for persona generator use case."""
    prompt: str

class PersonaGeneratorResponse(BaseResponse):
    """Response for persona generator use case."""
    parsed_output: Optional[Dict[str, Any]] = None

class PersonaGeneratorResult(BaseModel):
    """Result from PersonaGeneratorService.generate_personas method."""
    response_text: str
    tokens_used: Optional[int] = None
    agent_details: AgentDetails
    timestamp: datetime
    conversation_id: str
    parsed_output: Optional[Dict[str, Any]] = None

class PersonaGeneratorDocument(BaseDocument):
    """Document for persona generation."""
    prompt: str
    response: str
    parsed_output: Optional[Dict[str, Any]] = None
    tokens_used: Optional[int] = None
    time_taken_ms: float
    agent_details: AgentDetails
