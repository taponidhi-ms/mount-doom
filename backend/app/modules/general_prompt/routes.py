from fastapi import APIRouter, HTTPException, Query
from app.modules.general_prompt.models import (
    GeneralPromptRequest,
    GeneralPromptResponse
)
from app.models.shared import BrowseResponse
from app.core.config import settings
from .general_prompt_service import general_prompt_service
from app.infrastructure.db.cosmos_db_service import cosmos_db_service
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
            prompt=request.prompt,
            cleanup_conversation=False
        )

        end_time = datetime.utcnow()
        end_ms = time.time() * 1000
        time_taken_ms = end_ms - start_ms

        logger.info("Response generated, saving to database", 
                   tokens=result.tokens_used,
                   time_ms=round(time_taken_ms, 2))

        # Save to database using service method
        await general_prompt_service.save_to_database(
            model_id=settings.default_model_deployment,
            prompt=request.prompt,
            response=result.response_text,
            tokens_used=result.tokens_used,
            time_taken_ms=time_taken_ms,
            conversation_id=result.conversation_id
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

@router.get("/browse", response_model=BrowseResponse)
async def browse_general_prompts(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    order_by: str = Query(default="timestamp", description="Field to order by"),
    order_direction: str = Query(default="DESC", pattern="^(ASC|DESC)$", description="Order direction")
):
    """
    Browse general prompt records with pagination and ordering.
    Returns a list of general prompt records from the database.
    """
    logger.info("Browsing general prompts", 
               page=page, 
               page_size=page_size, 
               order_by=order_by,
               order_direction=order_direction)

    try:
        result = await cosmos_db_service.browse_container(
            container_name=cosmos_db_service.GENERAL_PROMPT_CONTAINER,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_direction=order_direction
        )

        logger.info("Returning browse results", total_count=result["total_count"])
        return result

    except Exception as e:
        logger.error("Error browsing general prompts", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error browsing general prompts: {str(e)}")

@router.post("/delete")
async def delete_general_prompts(ids: list[str]):
    """Delete general prompt records by their IDs."""
    logger.info("Received delete request", count=len(ids))
    if not ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    try:
        container = await cosmos_db_service.ensure_container(
            cosmos_db_service.GENERAL_PROMPT_CONTAINER
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
        logger.error("Error deleting general prompts", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting: {str(e)}")
