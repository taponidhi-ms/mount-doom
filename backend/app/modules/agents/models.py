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
    sample_inputs: List[Dict[str, Any]] = []  # Changed to Any to support tags as list


class AgentListResponse(BaseModel):
    """Response for listing all agents."""
    agents: List[AgentInfo]


class AgentInvokeRequest(BaseModel):
    """Request to invoke an agent (API layer)."""
    input: str  # The input text (prompt or transcript depending on agent)
    prompt_category: Optional[str] = None  # Optional category for the prompt (e.g., "Valid", "Invalid")
    prompt_tags: Optional[List[str]] = None  # Optional tags for the prompt


class AgentInvokeResponse(BaseModel):
    """Response from invoking an agent (API layer)."""
    response_text: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    start_time: datetime
    end_time: datetime
    agent_details: Dict[str, Any]
    conversation_id: str
    from_cache: bool = False


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
    from_cache: bool = False


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


# Multi-agent download models (eval format specific)

class AgentVersionInfo(BaseModel):
    """Information about an agent version with conversation count."""
    agent_id: str
    agent_name: str
    version: str
    conversation_count: int
    scenario_name: str


class AgentVersionSelection(BaseModel):
    """Selection of a specific agent and version for download."""
    agent_id: str
    version: str


class MultiAgentDownloadRequest(BaseModel):
    """Request to download conversations from multiple agent versions."""
    selections: List[AgentVersionSelection]
