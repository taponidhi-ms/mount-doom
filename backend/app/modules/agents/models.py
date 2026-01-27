"""
Models for the unified Agents API.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class AgentInfo(BaseModel):
    """Information about a single agent (for listing)."""
    agent_id: str
    agent_name: str
    display_name: str
    description: str
    instructions: str
    input_field: str
    input_label: str
    input_placeholder: str
    sample_inputs: List[Dict[str, str]] = []


class AgentListResponse(BaseModel):
    """Response for listing all agents."""
    agents: List[AgentInfo]


class AgentInvokeRequest(BaseModel):
    """Request to invoke an agent (API layer)."""
    input: str  # The input text (prompt or transcript depending on agent)


class AgentInvokeResponse(BaseModel):
    """Response from invoking an agent (API layer)."""
    response_text: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    start_time: datetime
    end_time: datetime
    agent_details: Dict[str, Any]
    conversation_id: str


# Service layer models (used internally by agents_service)

class AgentInvokeResult(BaseModel):
    """Result from invoking an agent (service layer)."""
    response_text: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    start_time: datetime
    end_time: datetime
    agent_details: Dict[str, Any]
    conversation_id: str


class CreateConversationResult(BaseModel):
    """Result from creating a persistent conversation (service layer)."""
    conversation_id: str
    agent_details: Dict[str, Any]
    agent_name: str
    timestamp: datetime


class InvokeOnConversationResult(BaseModel):
    """Result from invoking an agent on an existing conversation (service layer)."""
    response_text: str
    tokens_used: Optional[int] = None
    timestamp: datetime
