from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    PersonaGenerationRequest,
    PersonaGenerationResponse,
    AgentDetails
)
from app.core.config import settings
from app.services.features.persona_generation_service import persona_generation_service
from app.services.db.cosmos_db_service import cosmos_db_service
from datetime import datetime
import time
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/persona-generation", tags=["Persona Generation"])


@router.post("/generate", response_model=PersonaGenerationResponse)
async def generate_persona(request: PersonaGenerationRequest):
    """Generate persona from simulation prompt."""
    logger.info("Received persona generation request", prompt_length=len(request.prompt))
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    try:
        # Get response from persona generation service
        agent_response = await persona_generation_service.generate_persona(request.prompt)
        
        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms
        
        logger.info("Persona generated, saving to database",
                   tokens=agent_response["tokens_used"],
                   time_ms=round(time_taken_ms, 2))
        
        # Save to Cosmos DB
        agent_details = agent_response["agent_details"]
        await cosmos_db_service.save_persona_generation(
            prompt=request.prompt,
            response=agent_response["response_text"],
            tokens_used=agent_response["tokens_used"],
            time_taken_ms=time_taken_ms,
            agent_name=agent_details.agent_name,
            agent_version=agent_details.agent_version,
            agent_instructions=agent_details.instructions,
            model=agent_details.model_deployment_name,
            agent_timestamp=agent_details.created_at
        )
        
        logger.info("Returning successful persona generation response")
        
        return PersonaGenerationResponse(
            response_text=agent_response["response_text"],
            tokens_used=agent_response["tokens_used"],
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            agent_details=agent_details
        )
    
    except Exception as e:
        logger.error("Error in persona generation endpoint", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating persona: {str(e)}")
