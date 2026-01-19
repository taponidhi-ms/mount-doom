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
    role: str  # "agent" for C1, "customer" for C2
    content: str
    tokens_used: Optional[int] = None  # Only populated for C1 agent messages
    timestamp: datetime

class ConversationSimulationRequest(BaseRequest):
    """Request for conversation simulation feature."""
    customer_intent: str
    customer_sentiment: str
    conversation_subject: str

class ConversationSimulationResponse(BaseModel):
    """Response for conversation simulation feature."""
    conversation_history: List[ConversationMessage]
    conversation_status: str
    total_time_taken_ms: float
    start_time: datetime
    end_time: datetime
    agent_details: AgentDetails  # Primary agent (C1) details
    conversation_id: str

class ConversationSimulationResult(BaseModel):
    """Result from conversation simulation service."""
    conversation_history: List[ConversationMessage]
    conversation_status: str
    total_time_taken_ms: float
    start_time: datetime
    end_time: datetime
    agent_details: AgentDetails  # Primary agent (C1) details
    conversation_id: str

# DB Models
class ConversationSimulationDocument(BaseDocument):
    """Document for multi-turn conversation simulation."""
    conversation_properties: Dict[str, Any]
    conversation_history: List[ConversationMessage]
    conversation_status: str
    total_time_taken_ms: float
    # Primary agent (C1) details flattened at root
    agent_name: str
    agent_version: str
    agent_instructions: str
    agent_model: str
    agent_created_at: str
