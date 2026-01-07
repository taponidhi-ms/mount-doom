from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel
from app.models.shared import BaseRequest, BaseResponse, AgentDetails, BaseDocument

class PersonaDistributionRequest(BaseRequest):
    """Request for persona distribution generation use case."""
    prompt: str

class PersonaDistributionResponse(BaseResponse):
    """Response for persona distribution generation use case."""
    parsed_output: Optional[Dict[str, Any]] = None

class PersonaDistributionResult(BaseModel):
    """Result from PersonaDistributionService.generate_persona_distribution method."""
    response_text: str
    tokens_used: Optional[int] = None
    agent_details: AgentDetails
    timestamp: datetime
    conversation_id: str
    parsed_output: Optional[Dict[str, Any]] = None

class PersonaDistributionDocument(BaseDocument):
    """Document for persona distribution generation."""
    prompt: str
    response: str
    parsed_output: Optional[Dict[str, Any]] = None
    tokens_used: Optional[int] = None
    time_taken_ms: float
    agent_details: AgentDetails

class PersonaDistributionEvalsDocument(BaseDocument):       
    """Document for Persona Distribution Evals preparation."""
    source_run_ids: List[str]
    cxa_evals_config: Dict[str, Any]
    cxa_evals_input_data: Dict[str, Any]
