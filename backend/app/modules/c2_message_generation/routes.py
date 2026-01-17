"""Routes for C2 Message Generation feature."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from datetime import datetime, timezone
import time
import structlog

from app.modules.c2_message_generation.models import (
    C2MessageGenerationRequest,
    C2MessageGenerationResponse
)
from app.models.shared import BrowseResponse
from .c2_message_generation_service import c2_message_generation_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from app.modules.shared.route_helpers import (
    browse_records,
    delete_records,
    download_records_as_conversations
)

logger = structlog.get_logger()

router = APIRouter(prefix="/c2-message-generation", tags=["C2 Message Generation"])


@router.post("/generate", response_model=C2MessageGenerationResponse)
async def generate_c2_message(request: C2MessageGenerationRequest):
    """Generate a C2 (Customer) message from prompt."""
    logger.info("Received C2 message generation request", prompt_length=len(request.prompt))
    
    start_time = datetime.now(timezone.utc)
    start_ms = time.time() * 1000

    try:
        # Get response from C2 message generation service
        agent_response = await c2_message_generation_service.generate_message(request.prompt)
        
        end_time = datetime.now(timezone.utc)
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms

        logger.info("C2 message generated, saving to database", 
                   tokens=agent_response.tokens_used,
                   time_ms=round(time_taken_ms, 2))

        # Save to database using service method
        await c2_message_generation_service.save_to_database(
            prompt=request.prompt,
            response=agent_response.response_text,
            tokens_used=agent_response.tokens_used,
            time_taken_ms=time_taken_ms,
            agent_name=agent_response.agent_details.agent_name,
            agent_version=agent_response.agent_details.agent_version,
            agent_instructions=agent_response.agent_details.instructions,
            model=agent_response.agent_details.model_deployment_name,
            agent_timestamp=agent_response.agent_details.created_at,
            conversation_id=agent_response.conversation_id
        )

        logger.info("Returning successful C2 message generation response")
        return C2MessageGenerationResponse(
            response_text=agent_response.response_text,
            tokens_used=agent_response.tokens_used,
            time_taken_ms=time_taken_ms,
            start_time=start_time,
            end_time=end_time,
            agent_details=agent_response.agent_details
        )

    except Exception as e:
        logger.error("Error in C2 message generation endpoint", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating C2 message: {str(e)}")


@router.get("/browse", response_model=BrowseResponse)
async def browse_c2_message_generations(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    order_by: str = Query(default="timestamp", description="Field to order by"),
    order_direction: str = Query(default="DESC", pattern="^(ASC|DESC)$", description="Order direction")
):
    """Browse C2 message generation records with pagination and ordering."""
    return await browse_records(
        container_name=cosmos_db_service.C2_MESSAGE_GENERATION_CONTAINER,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order_direction=order_direction
    )


@router.post("/delete")
async def delete_c2_message_generations(ids: list[str]):
    """Delete C2 message generation records by their IDs."""
    return await delete_records(
        container_name=cosmos_db_service.C2_MESSAGE_GENERATION_CONTAINER,
        ids=ids
    )


@router.post("/download")
async def download_c2_message_generations(ids: list[str]) -> Response:
    """Download C2 message generation records as JSON."""
    return await download_records_as_conversations(
        container_name=cosmos_db_service.C2_MESSAGE_GENERATION_CONTAINER,
        ids=ids,
        scenario_name="c2_message_generation",
        filename="c2_message_generations.json",
        input_field="prompt"
    )

