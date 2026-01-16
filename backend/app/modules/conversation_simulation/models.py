from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.shared import BaseRequest, AgentDetails, BaseDocument

# API Schemas
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

# DB Models
class ConversationSimulationDocument(BaseDocument):
    """Document for conversation simulation."""
    conversation_properties: Dict[str, Any]
    conversation_history: List[ConversationMessage]
    conversation_status: str
    total_time_taken_ms: float
    c1_agent_details: AgentDetails
    c2_agent_details: AgentDetails
    total_tokens_used: Optional[int] = None
