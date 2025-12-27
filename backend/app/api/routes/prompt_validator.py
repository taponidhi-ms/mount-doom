from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    PromptValidatorRequest,
    PromptValidatorResponse,
    AvailableAgentsResponse,
    AgentInfo
)
from app.services.azure_ai_service import azure_ai_service
from app.services.cosmos_db_service import cosmos_db_service
from app.core.config import settings
from datetime import datetime
import time

router = APIRouter(prefix="/prompt-validator", tags=["Prompt Validator"])


@router.get("/agents", response_model=AvailableAgentsResponse)
async def get_available_agents():
    """Get list of available agents for prompt validator use case."""
    agents = []
    
    if settings.prompt_validator_agent:
        agents.append(AgentInfo(
            agent_id=settings.prompt_validator_agent,
            agent_name="Prompt Validator Agent",
            description="Agent for validating simulation prompts"
        ))
    
    return AvailableAgentsResponse(agents=agents)


@router.post("/validate", response_model=PromptValidatorResponse)
async def validate_prompt(request: PromptValidatorRequest):
    """Validate a simulation prompt."""
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    try:
        # Get response from agent
        response_text, tokens_used = await azure_ai_service.get_agent_response(
            agent_id=request.agent_id,
            prompt=request.prompt,
            stream=request.stream
        )
        
        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms
        
        # Save to Cosmos DB
        await cosmos_db_service.save_prompt_validator(
            agent_id=request.agent_id,
            prompt=request.prompt,
            response=response_text,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms
        )
        
        return PromptValidatorResponse(
            agent_id=request.agent_id,
            response_text=response_text,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating prompt: {str(e)}")
