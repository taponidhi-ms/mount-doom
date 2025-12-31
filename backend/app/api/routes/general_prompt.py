from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    GeneralPromptRequest,
    GeneralPromptResponse
)
from app.core.config import settings
from app.services.features.general_prompt_service import general_prompt_service
from app.services.db.cosmos_db_service import cosmos_db_service
from datetime import datetime
import time
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/general-prompt", tags=["General Prompt"])


@router.post("/generate", response_model=GeneralPromptResponse)
async def generate_response(request: GeneralPromptRequest):
    """Generate response for general prompt using model directly."""
    logger.info("Received general prompt request",
               prompt_length=len(request.prompt),
               model=settings.default_model_deployment)
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    try:
        # Get response from general prompt service
        result = await general_prompt_service.generate_response(
            prompt=request.prompt
        )
        
        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms
        
        logger.info("Response generated, saving to database",
                   tokens=result.tokens_used,
                   time_ms=round(time_taken_ms, 2))
        
        # Save to Cosmos DB
        await cosmos_db_service.save_general_prompt(
            model_id=settings.default_model_deployment,
            prompt=request.prompt,
            response=result.response_text,
            tokens_used=result.tokens_used,
            time_taken_ms=time_taken_ms
        )
        
        logger.info("Returning successful general prompt response")
        
        return GeneralPromptResponse(
            model_deployment_name=settings.default_model_deployment,
            response_text=result.response_text,
            tokens_used=result.tokens_used,
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time
        )
    
    except Exception as e:
        logger.error("Error in general prompt endpoint", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
