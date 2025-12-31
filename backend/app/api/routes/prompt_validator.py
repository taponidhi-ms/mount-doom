from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    PromptValidatorRequest,
    PromptValidatorResponse,
    AgentDetails
)
from app.core.config import settings
from app.services.features.prompt_validator_service import prompt_validator_service
from app.services.db.cosmos_db_service import cosmos_db_service
from datetime import datetime
import time
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/prompt-validator", tags=["Prompt Validator"])


@router.post("/validate", response_model=PromptValidatorResponse)
async def validate_prompt(request: PromptValidatorRequest):
    """Validate a simulation prompt."""
    logger.info("Received prompt validation request", prompt_length=len(request.prompt))
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    try:
        # Get response from prompt validator service
        agent_response = await prompt_validator_service.validate_prompt(request.prompt)
        
        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms
        
        logger.info("Validation complete, saving to database",
                   tokens=agent_response.tokens_used,
                   time_ms=round(time_taken_ms, 2))
        
        # Save to Cosmos DB
        await cosmos_db_service.save_prompt_validator(
            prompt=request.prompt,
            response=agent_response.response_text,
            tokens_used=agent_response.tokens_used,
            time_taken_ms=time_taken_ms,
            agent_name=agent_response.agent_details.agent_name,
            agent_version=agent_response.agent_details.agent_version,
            agent_instructions=agent_response.agent_details.instructions,
            model=agent_response.agent_details.model_deployment_name,
            agent_timestamp=agent_response.agent_details.created_at
        )
        
        logger.info("Returning successful validation response")
        
        return PromptValidatorResponse(
            response_text=agent_response.response_text,
            tokens_used=agent_response.tokens_used,
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            agent_details=agent_response.agent_details
        )
    
    except Exception as e:
        logger.error("Error in prompt validation endpoint", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error validating prompt: {str(e)}")
