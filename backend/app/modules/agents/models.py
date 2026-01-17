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


class AgentListResponse(BaseModel):
    """Response for listing all agents."""
    agents: List[AgentInfo]


class AgentInvokeRequest(BaseModel):
    """Request to invoke an agent."""
    input: str  # The input text (prompt or transcript depending on agent)


class AgentInvokeResponse(BaseModel):
    """Response from invoking an agent."""
    response_text: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    start_time: datetime
    end_time: datetime
    agent_details: Dict[str, Any]
    parsed_output: Optional[Dict[str, Any]] = None
