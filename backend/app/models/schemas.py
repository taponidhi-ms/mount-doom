from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AgentInfo(BaseModel):
    """Information about an available agent."""
    agent_id: str
    agent_name: str
    description: Optional[str] = None


class ModelInfo(BaseModel):
    """Information about an available model."""
    model_id: str
    model_name: str
    description: Optional[str] = None


class BaseRequest(BaseModel):
    """Base request with common fields."""
    pass


class BaseResponse(BaseModel):
    """Base response with timing and token information."""
    response_text: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    start_time: datetime
    end_time: datetime


class PersonaGenerationRequest(BaseRequest):
    """Request for persona generation use case."""
    agent_id: str
    prompt: str
    stream: bool = False


class PersonaGenerationResponse(BaseResponse):
    """Response for persona generation use case."""
    agent_id: str


class GeneralPromptRequest(BaseRequest):
    """Request for general prompt use case."""
    model_id: str
    prompt: str
    stream: bool = False


class GeneralPromptResponse(BaseResponse):
    """Response for general prompt use case."""
    model_id: str


class PromptValidatorRequest(BaseRequest):
    """Request for prompt validator use case."""
    agent_id: str
    prompt: str
    stream: bool = False


class PromptValidatorResponse(BaseResponse):
    """Response for prompt validator use case."""
    agent_id: str


class ConversationProperties(BaseModel):
    """Properties for conversation simulation."""
    customer_intent: str = Field(alias="CustomerIntent")
    customer_sentiment: str = Field(alias="CustomerSentiment")
    conversation_subject: str = Field(alias="ConversationSubject")
    
    class Config:
        populate_by_name = True


class ConversationMessage(BaseModel):
    """A single message in a conversation."""
    role: str  # "C1Agent" or "C2Agent"
    agent_id: str
    message: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    timestamp: datetime


class ConversationSimulationRequest(BaseRequest):
    """Request for conversation simulation use case."""
    c1_agent_id: str
    c2_agent_id: str
    conversation_properties: ConversationProperties
    max_turns: int = Field(default=10, le=20)
    stream: bool = False


class ConversationSimulationResponse(BaseModel):
    """Response for conversation simulation use case."""
    conversation_history: List[ConversationMessage]
    conversation_status: str
    total_tokens_used: Optional[int] = None
    total_time_taken_ms: float
    start_time: datetime
    end_time: datetime
    c1_agent_id: str
    c2_agent_id: str


class AvailableAgentsResponse(BaseModel):
    """Response containing available agents for a use case."""
    agents: List[AgentInfo]


class AvailableModelsResponse(BaseModel):
    """Response containing available models."""
    models: List[ModelInfo]
