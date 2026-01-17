from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

# --- Common API Schemas ---

class AgentResponseData(BaseModel):
    """Data returned from an agent response."""
    response_text: str
    tokens_used: Optional[int] = None
    agent_version: str
    timestamp: datetime
    conversation_id: str  # Conversation ID for stateful interactions


class AgentInfo(BaseModel):
    """Information about an available agent."""
    agent_id: str
    agent_name: str
    description: Optional[str] = None


class ModelInfo(BaseModel):
    """Information about an available model."""
    model_deployment_name: str
    display_name: str
    description: Optional[str] = None


class BaseRequest(BaseModel):
    """Base request with common fields."""
    pass


class AgentDetails(BaseModel):
    """Details about the agent used for a request."""
    agent_name: str
    agent_version: Optional[str] = None
    instructions: str
    model_deployment_name: str
    created_at: datetime


class BaseResponse(BaseModel):
    """Base response with timing and token information."""
    response_text: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    start_time: datetime
    end_time: datetime
    agent_details: AgentDetails


# --- Common DB Models ---

class BaseDocument(BaseModel):
    """Base document for Cosmos DB."""
    id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AvailableAgentsResponse(BaseModel):
    """Response containing available agents for a feature."""
    agents: List[AgentInfo]


class AvailableModelsResponse(BaseModel):
    """Response containing available models."""
    models: List[ModelInfo]


class BrowseResponse(BaseModel):
    """Response for browse/list endpoints with pagination."""
    items: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
