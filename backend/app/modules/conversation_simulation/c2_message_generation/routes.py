"""Routes for C2 Message Generation use case."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from app.modules.c2_message_generation.models import (
    C2MessageGenerationRequest,
    C2MessageGenerationResponse
)
from app.models.shared import BrowseResponse, AgentDetails
from app.core.config import settings
from .c2_message_generation_service import c2_message_generation_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
from datetime import datetime
import time
import structlog
import json

logger = structlog.get_logger()

router = APIRouter(prefix="/c2-message-generation", tags=["C2 Message Generation"])


@router.post("/generate", response_model=C2MessageGenerationResponse)
async def generate_c2_message(request: C2MessageGenerationRequest):
    """Generate a C2 (Customer) message from prompt."""
    logger.info("Received C2 message generation request", prompt_length=len(request.prompt))
    
    start_time = datetime.utcnow()
    start_ms = time.time() * 1000

    try:
        # Get response from C2 message generation service
        agent_response = await c2_message_generation_service.generate_message(request.prompt)
        
        end_time = datetime.utcnow()
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
    """
    Browse C2 message generation records with pagination and ordering.
    Returns a list of C2 message generation records from the database.
    """
    logger.info("Browsing C2 message generations", 
               page=page, 
               page_size=page_size, 
               order_by=order_by,
               order_direction=order_direction)

    try:
        result = await cosmos_db_service.browse_container(
            container_name=cosmos_db_service.C2_MESSAGE_GENERATION_CONTAINER,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_direction=order_direction
        )

        logger.info("Returning browse results", total_count=result["total_count"])
        return result

    except Exception as e:
        logger.error("Error browsing C2 message generations", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error browsing C2 message generations: {str(e)}")


@router.post("/delete")
async def delete_c2_message_generations(ids: list[str]):
    """Delete C2 message generation records by their IDs."""
    logger.info("Received delete request", count=len(ids))
    if not ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    try:
        container = await cosmos_db_service.ensure_container(
            cosmos_db_service.C2_MESSAGE_GENERATION_CONTAINER
        )
        
        deleted_count = 0
        errors = []
        
        for item_id in ids:
            try:
                container.delete_item(item=item_id, partition_key=item_id)
                deleted_count += 1
            except Exception as e:
                errors.append(f"Failed to delete {item_id}: {str(e)}")
                logger.warning(f"Failed to delete {item_id}", error=str(e))
        
        logger.info("Delete operation completed", deleted=deleted_count, failed=len(errors))
        return {"deleted_count": deleted_count, "failed_count": len(errors), "errors": errors}
    
    except Exception as e:
        logger.error("Error deleting C2 message generations", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting: {str(e)}")


@router.post("/download")
async def download_c2_message_generations(ids: list[str]):
    """
    Download C2 message generation records as JSON.
    Returns conversations array with system prompt, user prompt, and assistant response.
    """
    logger.info("Received download request", count=len(ids))
    
    if not ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    try:
        container = await cosmos_db_service.ensure_container(
            cosmos_db_service.C2_MESSAGE_GENERATION_CONTAINER
        )
        
        conversations = []
        
        for item_id in ids:
            try:
                item = container.read_item(item=item_id, partition_key=item_id)
                
                # Extract agent instructions from agent_details
                agent_details = item.get("agent_details", {})
                agent_instructions = agent_details.get("instructions", "")
                
                # Extract data from the stored item
                conversation = {
                    "Id": item.get("id"),
                    "scenario_name": "c2_message_generation",
                    "conversation": [
                        {
                            "role": "system",
                            "content": agent_instructions
                        },
                        {
                            "role": "user",
                            "content": item.get("prompt", "")
                        },
                        {
                            "role": "assistant",
                            "content": item.get("response", "")
                        }
                    ]
                }
                conversations.append(conversation)
                
            except Exception as e:
                logger.warning("Failed to retrieve item", item_id=item_id, error=str(e))
                # Continue with other items even if one fails
                continue
        
        result = {"conversations": conversations}
        json_str = json.dumps(result, indent=2)
        
        logger.info("Returning download data", conversation_count=len(conversations))
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="c2_message_generations.json"'}
        )
        
    except Exception as e:
        logger.error("Error downloading C2 message generations", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error downloading: {str(e)}")
