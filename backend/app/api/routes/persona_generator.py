from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import (
    PersonaGeneratorRequest,
    PersonaGeneratorResponse,
    AgentDetails,
    BrowseResponse
)
from app.core.config import settings
from app.services.features.persona_generator_service import persona_generator_service
from app.services.db.cosmos_db_service import cosmos_db_service
from datetime import datetime
import time
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/persona-generator", tags=["Persona Generator"])


@router.post("/generate", response_model=PersonaGeneratorResponse)
async def generate_personas(request: PersonaGeneratorRequest):
    """Generate exact personas from prompt."""
    logger.info("Received persona generation request", prompt_length=len(request.prompt))
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    try:
        # Get response from persona generator service
        agent_response = await persona_generator_service.generate_personas(request.prompt)
        
        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms
        
        logger.info("Personas generated, saving to database",
                   tokens=agent_response.tokens_used,
                   time_ms=round(time_taken_ms, 2))
        
        # Save to database using service method
        await persona_generator_service.save_to_database(
            prompt=request.prompt,
            response=agent_response.response_text,
            tokens_used=agent_response.tokens_used,
            time_taken_ms=time_taken_ms,
            agent_name=agent_response.agent_details.agent_name,
            agent_version=agent_response.agent_details.agent_version,
            agent_instructions=agent_response.agent_details.instructions,
            model=agent_response.agent_details.model_deployment_name,
            agent_timestamp=agent_response.agent_details.created_at,
            conversation_id=agent_response.conversation_id,
            parsed_output=agent_response.parsed_output
        )
        
        logger.info("Returning successful persona generation response")
        
        return PersonaGeneratorResponse(
            response_text=agent_response.response_text,
            tokens_used=agent_response.tokens_used,
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            agent_details=agent_response.agent_details,
            parsed_output=agent_response.parsed_output
        )
    
    except Exception as e:
        logger.error("Error in persona generation endpoint", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating personas: {str(e)}")


@router.get("/browse", response_model=BrowseResponse)
async def browse_persona_generations(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    order_by: str = Query(default="timestamp", description="Field to order by"),
    order_direction: str = Query(default="DESC", pattern="^(ASC|DESC)$", description="Order direction")
):
    """
    Browse persona generation records with pagination and ordering.
    
    Returns a list of persona generation records from the database.
    """
    logger.info("Browsing persona generations",
               page=page,
               page_size=page_size,
               order_by=order_by,
               order_direction=order_direction)
    
    try:
        result = await cosmos_db_service.browse_container(
            container_name=cosmos_db_service.PERSONA_GENERATOR_CONTAINER,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_direction=order_direction
        )
        
        logger.info("Returning browse results", total_count=result["total_count"])
        return result
    
    except Exception as e:
        logger.error("Error browsing persona generations", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error browsing persona generations: {str(e)}")
