from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import (
    PersonaDistributionRequest,
    PersonaDistributionResponse,
    AgentDetails,
    BrowseResponse,
    PrepareEvalsRequest,
    PrepareEvalsResponse,
    EvalsDataResponse
)
from app.core.config import settings
from app.services.features.persona_distribution_service import persona_distribution_service
from app.services.features.evals_prep_service import evals_prep_service
from app.services.db.cosmos_db_service import cosmos_db_service
from datetime import datetime
import time
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/persona-distribution", tags=["Persona Distribution"])


@router.post("/generate", response_model=PersonaDistributionResponse)
async def generate_persona_distribution(request: PersonaDistributionRequest):
    """Generate persona distribution from simulation prompt."""
    logger.info("Received persona distribution generation request", prompt_length=len(request.prompt))
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000
    
    try:
        # Get response from persona distribution generation service
        agent_response = await persona_distribution_service.generate_persona_distribution(request.prompt)
        
        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms
        
        logger.info("Persona distribution generated, saving to database",
                   tokens=agent_response.tokens_used,
                   time_ms=round(time_taken_ms, 2))
        
        # Save to database using service method
        await persona_distribution_service.save_to_database(
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
            parsed_output=agent_response.parsed_output,
            groundness_fact=agent_response.groundness_fact
        )
        
        logger.info("Returning successful persona distribution generation response")
        
        return PersonaDistributionResponse(
            response_text=agent_response.response_text,
            tokens_used=agent_response.tokens_used,
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            agent_details=agent_response.agent_details,
            parsed_output=agent_response.parsed_output,
            groundness_fact=agent_response.groundness_fact
        )
    
    except Exception as e:
        logger.error("Error in persona distribution generation endpoint", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating persona distribution: {str(e)}")


@router.get("/browse", response_model=BrowseResponse)
async def browse_persona_distributions(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    order_by: str = Query(default="timestamp", description="Field to order by"),
    order_direction: str = Query(default="DESC", pattern="^(ASC|DESC)$", description="Order direction")
):
    """
    Browse persona distribution generation records with pagination and ordering.
    
    Returns a list of persona distribution generation records from the database.
    """
    logger.info("Browsing persona distributions",
               page=page,
               page_size=page_size,
               order_by=order_by,
               order_direction=order_direction)
    
    try:
        result = await cosmos_db_service.browse_container(
            container_name=cosmos_db_service.PERSONA_DISTRIBUTION_CONTAINER,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_direction=order_direction
        )
        
        logger.info("Returning browse results", total_count=result["total_count"])
        return result
    
    except Exception as e:
        logger.error("Error browsing persona distributions", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error browsing persona distributions: {str(e)}")


@router.post("/prepare-evals", response_model=PrepareEvalsResponse)
async def prepare_evals(request: PrepareEvalsRequest):
    """
    Prepare CXA AI Evals dataset from selected persona distribution runs.
    
    Combines multiple persona distribution runs into a standardized format
    for evaluation in the CXA AI Evals framework.
    """
    logger.info("Received evals preparation request", run_ids_count=len(request.selected_run_ids))
    
    try:
        # Prepare evals using the service
        result = await evals_prep_service.prepare_evals(request.selected_run_ids)
        
        # Save to database
        await evals_prep_service.save_to_database(
            evals_id=result["evals_id"],
            source_run_ids=result["source_run_ids"],
            cxa_evals_config=result["cxa_evals_config"],
            cxa_evals_input_data=result["cxa_evals_input_data"]
        )
        
        logger.info("Evals preparation completed successfully", evals_id=result["evals_id"])
        
        conversations_count = len(result["cxa_evals_input_data"].get("conversations", []))
        return PrepareEvalsResponse(
            evals_id=result["evals_id"],
            timestamp=result["timestamp"],
            source_run_ids=result["source_run_ids"],
            conversations_count=conversations_count,
            message=f"Successfully prepared evals from {len(result['source_run_ids'])} runs with {conversations_count} conversations"
        )
    
    except ValueError as e:
        logger.error("Validation error in evals preparation", error=str(e), exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error preparing evals", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error preparing evals: {str(e)}")


@router.get("/evals/latest", response_model=EvalsDataResponse)
async def get_latest_evals():
    """
    Get the most recently prepared evals dataset.
    
    Returns the latest CXA AI Evals configuration and input data.
    """
    logger.info("Fetching latest evals preparation")
    
    try:
        result = await evals_prep_service.get_latest_evals()
        
        if not result:
            raise HTTPException(status_code=404, detail="No evals preparations found")
        
        logger.info("Returning latest evals", evals_id=result.get("id"))
        
        return EvalsDataResponse(
            evals_id=result["id"],
            timestamp=result["timestamp"],
            source_run_ids=result["source_run_ids"],
            cxa_evals_config=result["cxa_evals_config"],
            cxa_evals_input_data=result["cxa_evals_input_data"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching latest evals", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching latest evals: {str(e)}")
