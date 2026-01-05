from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class AgentDetails(BaseModel):
    """Details about the agent used for a request."""
    agent_name: str
    agent_version: Optional[str] = None
    instructions: str
    model_deployment_name: str
    created_at: datetime

class BaseDocument(BaseModel):
    """Base document for Cosmos DB."""
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PersonaDistributionDocument(BaseDocument):
    """Document for persona distribution generation."""
    prompt: str
    response: str
    parsed_output: Optional[Dict[str, Any]] = None
    tokens_used: Optional[int] = None
    time_taken_ms: float
    agent_details: AgentDetails

class PersonaGeneratorDocument(BaseDocument):
    """Document for persona generation."""
    prompt: str
    response: str
    parsed_output: Optional[Dict[str, Any]] = None
    tokens_used: Optional[int] = None
    time_taken_ms: float
    agent_details: AgentDetails

class GeneralPromptDocument(BaseDocument):
    """Document for general prompt."""
    prompt: str
    response: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    model_deployment_name: str

class PromptValidatorDocument(BaseDocument):
    """Document for prompt validation."""
    prompt: str
    response: str
    tokens_used: Optional[int] = None
    time_taken_ms: float
    agent_details: AgentDetails

class ConversationMessage(BaseModel):
    """Message in a conversation."""
    agent_name: str
    message: str
    timestamp: datetime

class ConversationSimulationDocument(BaseDocument):
    """Document for conversation simulation."""
    conversation_properties: Dict[str, Any]
    conversation_history: List[ConversationMessage]
    conversation_status: str
    total_time_taken_ms: float
    c1_agent_details: AgentDetails
    c2_agent_details: AgentDetails
    total_tokens_used: Optional[int] = None

class EvalsPrepDocument(BaseDocument):
    """Document for CXA AI Evals preparation."""
    source_run_ids: List[str]
    cxa_evals_config: Dict[str, Any]
    cxa_evals_input_data: List[Dict[str, Any]]
