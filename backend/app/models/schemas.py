from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


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


class PersonaDistributionResult(BaseModel):
    """Result from PersonaDistributionService.generate_persona_distribution method."""
    response_text: str
    tokens_used: Optional[int] = None
    agent_details: AgentDetails
    timestamp: datetime
    conversation_id: str
    parsed_output: Optional[Dict[str, Any]] = None


class PersonaGeneratorResult(BaseModel):
    """Result from PersonaGeneratorService.generate_personas method."""
    response_text: str
    tokens_used: Optional[int] = None
    agent_details: AgentDetails
    timestamp: datetime
    conversation_id: str
    parsed_output: Optional[Dict[str, Any]] = None


class PromptValidatorResult(BaseModel):
    """Result from PromptValidatorService.validate_prompt method."""
    response_text: str
    tokens_used: Optional[int] = None
    agent_details: AgentDetails
    timestamp: datetime
    conversation_id: str


class GeneralPromptResult(BaseModel):
    """Result from GeneralPromptService.generate_response method."""
    response_text: str
    tokens_used: Optional[int] = None
    conversation_id: str


class BaseResponse(BaseModel):
    """Base response with timing and token information."""
    response_text: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    start_time: datetime
    end_time: datetime
    agent_details: AgentDetails


class PersonaDistributionRequest(BaseRequest):
    """Request for persona distribution generation use case."""
    prompt: str


class PersonaDistributionResponse(BaseResponse):
    """Response for persona distribution generation use case."""
    parsed_output: Optional[Dict[str, Any]] = None


class PersonaGeneratorRequest(BaseRequest):
    """Request for persona generator use case."""
    prompt: str


class PersonaGeneratorResponse(BaseResponse):
    """Response for persona generator use case."""
    parsed_output: Optional[Dict[str, Any]] = None


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


class PromptValidatorRequest(BaseRequest):
    """Request for prompt validator use case."""
    prompt: str


class PromptValidatorResponse(BaseResponse):
    """Response for prompt validator use case."""
    pass


class ConversationProperties(BaseModel):
    """Properties for conversation simulation."""
    customer_intent: str = Field(alias="CustomerIntent")
    customer_sentiment: str = Field(alias="CustomerSentiment")
    conversation_subject: str = Field(alias="ConversationSubject")
    
    class Config:
        populate_by_name = True


class ConversationMessage(BaseModel):
    """A single message in a conversation."""
    agent_name: str
    message: str
    timestamp: datetime


class ConversationSimulationResult(BaseModel):
    """Result from conversation simulation service."""
    conversation_history: List[ConversationMessage]
    conversation_status: str
    total_time_taken_ms: float
    start_time: datetime
    end_time: datetime
    c1_agent_details: AgentDetails
    c2_agent_details: AgentDetails
    conversation_id: str


class ConversationSimulationRequest(BaseRequest):
    """Request for conversation simulation use case."""
    customer_intent: str
    customer_sentiment: str
    conversation_subject: str


class ConversationSimulationResponse(BaseModel):
    """Response for conversation simulation use case."""
    conversation_history: List[ConversationMessage]
    conversation_status: str
    total_time_taken_ms: float
    start_time: datetime
    end_time: datetime
    c1_agent_details: AgentDetails
    c2_agent_details: AgentDetails
    conversation_id: str


class AvailableAgentsResponse(BaseModel):
    """Response containing available agents for a use case."""
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


class PrepareEvalsRequest(BaseModel):
    """Request for preparing CXA AI Evals from selected runs."""
    selected_run_ids: List[str] = Field(
        ..., 
        min_length=1,
        description="List of persona distribution run IDs to combine"
    )


class PrepareEvalsResponse(BaseModel):
    """Response for evals preparation."""
    evals_id: str
    timestamp: datetime
    source_run_ids: List[str]
    personas_count: int
    message: str


class EvalsDataResponse(BaseModel):
    """Response containing prepared evals data."""
    evals_id: str
    timestamp: datetime
    source_run_ids: List[str]
    cxa_evals_config: Dict[str, Any]
    cxa_evals_input_data: List[Dict[str, Any]]
