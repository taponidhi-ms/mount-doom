"""Routes for Persona Distribution use case."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from datetime import datetime, timezone
import time
import structlog

from app.modules.persona_distribution.models import (
    PersonaDistributionRequest,
    PersonaDistributionResponse
)
from app.models.shared import BrowseResponse
from .persona_distribution_service import persona_distribution_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from app.modules.shared.route_helpers import (
    browse_records,
    delete_records,
    download_records_as_conversations
)

logger = structlog.get_logger()

router = APIRouter(prefix="/persona-distribution", tags=["Persona Distribution"])


@router.post("/generate", response_model=PersonaDistributionResponse)
async def generate_persona_distribution(request: PersonaDistributionRequest):
    """Generate persona distribution from simulation prompt."""
    logger.info("Received persona distribution generation request", prompt_length=len(request.prompt))
    
    start_time = datetime.now(timezone.utc)
    start_ms = time.time() * 1000

    try:
        # Get response from persona distribution generation service
        agent_response = await persona_distribution_service.generate_persona_distribution(request.prompt)
        
        end_time = datetime.now(timezone.utc)
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
            parsed_output=agent_response.parsed_output
        )

        logger.info("Returning successful persona distribution generation response")
        return PersonaDistributionResponse(
            response_text=agent_response.response_text,
            tokens_used=agent_response.tokens_used,
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            agent_details=agent_response.agent_details,
            parsed_output=agent_response.parsed_output
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
    """Browse persona distribution generation records with pagination and ordering."""
    return await browse_records(
        container_name=cosmos_db_service.PERSONA_DISTRIBUTION_CONTAINER,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order_direction=order_direction,
        use_case_name="persona distributions"
    )


@router.post("/delete")
async def delete_persona_distributions(ids: list[str]):
    """Delete persona distribution records by their IDs."""
    return await delete_records(
        container_name=cosmos_db_service.PERSONA_DISTRIBUTION_CONTAINER,
        ids=ids,
        use_case_name="persona distributions"
    )


@router.post("/download")
async def download_persona_distributions(ids: list[str]) -> Response:
    """Download persona distribution records as JSON."""
    return await download_records_as_conversations(
        container_name=cosmos_db_service.PERSONA_DISTRIBUTION_CONTAINER,
        ids=ids,
        scenario_name="persona_distribution_generation",
        filename="persona_distributions.json",
        use_case_name="persona distributions",
        input_field="prompt"
    )

