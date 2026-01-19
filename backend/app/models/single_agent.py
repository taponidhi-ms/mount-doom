"""
Base schemas for single-agent operations.

These schemas provide a common interface for all single-agent use cases,
enabling code reuse while maintaining type safety.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.models.shared import AgentDetails, BaseDocument


class SingleAgentRequest(BaseModel):
    """Base request for single-agent operations.
    
    Subclass this for specific use cases that need additional fields.
    """
    prompt: str


class SingleAgentResult(BaseModel):
    """Result from a single-agent service operation.
    
    Used internally between service and route layers.
    """
    response_text: str
    tokens_used: Optional[int] = None
    agent_details: AgentDetails
    timestamp: datetime
    conversation_id: str
    parsed_output: Optional[Dict[str, Any]] = None


class SingleAgentResponse(BaseModel):
    """API response for single-agent operations.
    
    This is the standardized response format for all single-agent endpoints.
    """
    response_text: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    start_time: datetime
    end_time: datetime
    agent_details: AgentDetails
    parsed_output: Optional[Dict[str, Any]] = None


class SingleAgentDocument(BaseDocument):
    """Base document for single-agent results in Cosmos DB.

    All single-agent use cases should use this as their document format.
    """
    prompt: str
    response: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    agent_details: AgentDetails
    parsed_output: Optional[Dict[str, Any]] = None
