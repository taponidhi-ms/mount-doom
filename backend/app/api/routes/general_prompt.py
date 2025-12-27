from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    GeneralPromptRequest,
    GeneralPromptResponse,
    AvailableModelsResponse,
    ModelInfo
)
from app.services.azure_ai_service import azure_ai_service
from app.services.cosmos_db_service import cosmos_db_service
from app.core.config import settings
from datetime import datetime
import time

router = APIRouter(prefix="/general-prompt", tags=["General Prompt"])


@router.get("/models", response_model=AvailableModelsResponse)
async def get_available_models():
    """Get list of available models for general prompt use case."""
    models = [
        ModelInfo(
            model_id=settings.general_model_1,
            model_name="GPT-4",
            description="Advanced language model for complex tasks"
        ),
        ModelInfo(
            model_id=settings.general_model_2,
            model_name="GPT-3.5 Turbo",
            description="Fast and efficient model for general tasks"
        )
    ]
    
    return AvailableModelsResponse(models=models)


@router.post("/generate", response_model=GeneralPromptResponse)
async def generate_response(request: GeneralPromptRequest):
    """Generate response for general prompt using model directly."""
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    try:
        # Get response from model
        response_text, tokens_used = await azure_ai_service.get_model_response(
            model_id=request.model_id,
            prompt=request.prompt,
            stream=request.stream
        )
        
        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms
        
        # Save to Cosmos DB
        await cosmos_db_service.save_general_prompt(
            model_id=request.model_id,
            prompt=request.prompt,
            response=response_text,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms
        )
        
        return GeneralPromptResponse(
            model_id=request.model_id,
            response_text=response_text,
            tokens_used=tokens_used,
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
