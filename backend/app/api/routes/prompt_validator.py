from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    PromptValidatorRequest,
    PromptValidatorResponse,
    AgentDetails,
    AvailableModelsResponse,
    ModelInfo
)
from app.services.azure_ai_service import azure_ai_service
from app.services.cosmos_db_service import cosmos_db_service
from app.core.config import settings
from app.instruction_sets import PROMPT_VALIDATOR_AGENT_NAME, PROMPT_VALIDATOR_AGENT_INSTRUCTIONS
from datetime import datetime
import time

router = APIRouter(prefix="/prompt-validator", tags=["Prompt Validator"])


@router.get("/models", response_model=AvailableModelsResponse)
async def get_available_models():
    """Get list of available models for prompt validator use case."""
    models = [
        ModelInfo(
            model_id="gpt-4",
            model_name="GPT-4",
            description="Advanced language model for prompt validation"
        ),
        ModelInfo(
            model_id="gpt-35-turbo",
            model_name="GPT-3.5 Turbo",
            description="Fast and efficient model for prompt validation"
        )
    ]
    
    return AvailableModelsResponse(models=models)


@router.post("/validate", response_model=PromptValidatorResponse)
async def validate_prompt(request: PromptValidatorRequest):
    """Validate a simulation prompt."""
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    try:
        # Get response from agent using fixed agent name and instructions
        response_text, tokens_used, agent_version, agent_timestamp = await azure_ai_service.get_agent_response(
            agent_name=PROMPT_VALIDATOR_AGENT_NAME,
            instructions=PROMPT_VALIDATOR_AGENT_INSTRUCTIONS,
            prompt=request.prompt,
            model=request.model,
            stream=request.stream
        )
        
        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms
        
        # Save to Cosmos DB
        await cosmos_db_service.save_prompt_validator(
            prompt=request.prompt,
            response=response_text,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms,
            agent_name=PROMPT_VALIDATOR_AGENT_NAME,
            agent_version=agent_version,
            agent_instructions=PROMPT_VALIDATOR_AGENT_INSTRUCTIONS,
            model=request.model,
            agent_timestamp=agent_timestamp
        )
        
        agent_details = AgentDetails(
            agent_name=PROMPT_VALIDATOR_AGENT_NAME,
            agent_version=agent_version,
            instructions=PROMPT_VALIDATOR_AGENT_INSTRUCTIONS,
            model=request.model,
            timestamp=agent_timestamp
        )
        
        return PromptValidatorResponse(
            response_text=response_text,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            agent_details=agent_details
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating prompt: {str(e)}")
